import streamlit as st
import pandas as pd
from settings.db_connection import get_engine
import plotly.express as px
import pydeck as pdk
from settings.modstopage import FOOTER

st.set_page_config(
    page_title="Información del mercado",
    page_icon=":material/location_city:",
    layout="wide",
    initial_sidebar_state="collapsed"
)
@st.cache_data
def load_data():
    engine = get_engine()
    query = "SELECT * FROM casas"
    casas = pd.read_sql_query(sql=query, con=engine)
   
    query = "SELECT * FROM localizaciones"
    localizaciones = pd.read_sql_query(sql=query, con=engine)

    df = casas.merge(localizaciones, how='left', left_on='localizacion', right_on='nombre')

    if not df.empty:
        print("Se han cargado con exito los datos")
    else:
        print("No se han cargado los datos")
    return df


df = load_data()
st.header("Información general del mercado de alquiler en Granada :material/location_city:", divider="violet")

# Asegurar la columna sea datetime
df['fecha_agregacion'] = pd.to_datetime(df["fecha_agregacion"])
# Filtrar dataset por mes
months = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
            "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

choice = st.selectbox("Mes",months)
if choice == "Todos":
    df_month = df
else:
    number_month = months.index(choice)
    df_month = df[df['fecha_agregacion'].dt.month == number_month]

with st.container():

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Precio Medio Alquiler")
        price_mean = round(df_month['precio'].mean(), 2)
        price_mean_str = str(price_mean) + ' €'
        st.metric(label=" ", value=price_mean_str)

    with col2:
        st.subheader("Media m2")
        metres_mean = round(df_month['metros_reales'].mean(), 2)
        metres_mean_str = str(metres_mean) + ' m2'
        st.metric(label=" ", value=metres_mean_str)

    with col3:
        m2_price = round(price_mean/metres_mean, 2)
        m2_price_str = str(m2_price) + ' €/m2'
        st.subheader("Precio m2")
        st.metric(label=" ", value=m2_price_str)


with st.container():
    st.divider()
    st.subheader("Gráficos")

    # Grafico barras Precio promedio por localizacion
    df_grouped = df_month.groupby("localizacion", as_index=False)['precio'].mean()
    x_axis = "localizacion"
    y_axis= "precio"
    fig = px.bar(
        df_grouped,
        x=x_axis,
        y=y_axis,
        labels={x_axis: "Localización", y_axis: "Precio promedio (€)"},
        hover_data={'precio': ':.2f'},
        title="Precio promedio por localización",
        color='precio',
        color_continuous_scale=px.colors.sequential.Purp_r
    )
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        # Grafico circular cantidad de pisos por localizacion
        df_grouped = df_month['localizacion'].value_counts().nlargest(10).reset_index()
        df_grouped.columns = ['localizacion', 'cantidad']

        fig = px.pie(
            df_grouped,
            names='localizacion',
            values='cantidad',
            title='Distribucion de pisos por localizacion (10 con más pisos)',
            color_discrete_sequence=px.colors.sequential.Purp_r
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Grafico circular precio medio por tipo de piso
        df_grouped = df_month.groupby("piso", as_index=False)["precio"].mean()
        df_grouped.columns = ['piso', 'precio_promedio']

        fig = px.pie(
            df_grouped,
            names='piso',
            values='precio_promedio',
            hover_data={'precio_promedio': ':.2f'},
            title='Precio promedio por tipo de piso',
            color_discrete_sequence=px.colors.sequential.Purp_r
        )
        st.plotly_chart(fig, use_container_width=True)
    
    print(df_month)

    # CREAR MAPA CON LAS COLUMNAS ELEVANDO SEGUN EL PRECIO MEDIO DE CADA ZONA

    # Agrupar para obtener la media del precio por localizacion
    df_grouped = df_month.groupby("localizacion", as_index=False)['precio'].mean().round(2)

    # Añadir latitud y longitud representativas (por ejemplo, la primera de cada grupo)
    coordenadas = df_month.groupby("localizacion", as_index=False)[["latitud", "longitud"]].first()

    # Unir coordenadas con el DataFrame agrupado
    df_grouped = df_grouped.merge(coordenadas, on="localizacion")

    df_grouped["precio_norm"] = df_grouped["precio"] / df_grouped["precio"].max()

    # Configurar las columnas del mapa
    heatmap_layer = pdk.Layer(
        "ColumnLayer",
        data=df_grouped,
        get_position='[longitud, latitud]',
        get_elevation='precio_norm  * 500',  
        elevation_scale=1,
        radius=50,
        get_fill_color='[150, 100, 255, 180]',  
        pickable=True,
        auto_highlight=True,
        
    ) 

    st.subheader("Mapa interactivo con el precio medio de cada zona")
    # Vista inicial mapa
    view_state = pdk.ViewState(
        latitude=df_month.loc[df_month['localizacion'] == "Granada", "latitud"].iloc[0],
        longitude=df_month.loc[df_month['localizacion'] == "Granada", "longitud"].iloc[0],
        zoom=13,
        pitch=45,
        
    )   
    # Mostrar mapa
    st.pydeck_chart(pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=view_state,
        tooltip={"text": "Localización: {localizacion}\n"
        "Precio: {precio}€"}
        
    ))
# Añadir footer
st.markdown(FOOTER,unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from settings.db_connection import get_engine
from sqlalchemy import text
import settings.modstopage as mod
import os

# Configuracion de la pagina
st.set_page_config(
    page_title="Predictor de Alquileres - Granada",
    page_icon=":material/location_city:",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Captura parámetros si vienen desde la URL para la prueba de carga con LOCUST
params = st.query_params

metros = int(params.get("metros", 65))
habitaciones = int(params.get("habitaciones", 3))
banios = int(params.get("banios", 2))

localizacion = params.get("localizacion", "Zaidín, Granada")

piso = params.get("piso", "Primeros pisos")

ascensor = params.get("ascensor", "false").lower() == "true"
garaje = params.get("garaje", "false").lower() == "true"
calefaccion = params.get("calefaccion", "false").lower() == "true"
aire_acondicionado = params.get("aire_acondicionado", "false").lower() == "true"
trastero = params.get("trastero", "false").lower() == "true"
terraza = params.get("terraza", "false").lower() == "true"
piscina = params.get("piscina", "false").lower() == "true"
zonas_verdes = params.get("zonas_verdes", "false").lower() == "true"


# Cargar recursos (modelo y encoders)
@st.cache_resource
def load_resources():
    # Cargar modelo Ridge
    base_path = os.path.dirname(__file__)
    model_path = os.path.join(base_path, "..", "resources", "modelo_mll.pkl")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Cargar columnas esperadas por el modelo
    encoded_columns_path = os.path.join(base_path, "..", "resources", "encoded_columns.npy")
    encoded_columns = np.load(encoded_columns_path, allow_pickle=True)
    
    return model, encoded_columns

# Obtener la media del precio de todas las casas de la bd
@st.cache_resource
def price_mean():
    engine = get_engine()
    query = text("SELECT AVG(precio) from casas")
    with engine.connect() as con:
        mean = con.execute(query).scalar() # Scalar obtiene directamente el primer valor de la primera columna de la primera fila

    return mean if mean is not None else 0




model, enconded_columns = load_resources()
st.header("Predictor de Precios de Alquiler")
st.subheader("Predice el valor de alquiler en Granada basado en las características de la propiedad"
             , divider="violet")

# Formulario
with st.form("prediction_form"):
    st.subheader(":material/description: Datos de la propiedad")

    col_left, col_right = st.columns(2)

    with col_left:
        # Informacion basica
        metros = st.slider("Metros cuadrados", 20, 200, metros, 5)
        habitaciones = st.selectbox("Habitaciones", [1, 2, 3, 4, 5], index=[1, 2, 3, 4, 5].index(habitaciones))
        banios = st.selectbox("Baños", [1, 2, 3], index=[1, 2, 3].index(banios))

        # Localizacion
        localizacion = st.selectbox(
            "Localizacion",
            [
            "Albaicín, Granada", "Barrio de los Periodistas, Granada", "Bola de Oro, Granada",
            "Campus de la Salud, Granada", "Carrera de la Virgen - Paseo del Salón, Granada", "Catedral, Granada",
            "Centro, Granada", "Figares, Granada", "Gran Capitán, Granada",
            "Los Pajaritos, Granada", "Plaza de Toros, Granada", "Recogidas, Granada",
            "Ronda - Arabial, Granada", "San Ildefonso, Granada", "San Matías - Pavaneras, Granada",
            "Zaidín, Granada",
            "Armilla", "Atarfe", "Cajar",
            "Gojar", "Huétor-Vega", "La Zubia",
            "Monachil", "Otro"
            ],
            index=[
            "Albaicín, Granada", "Barrio de los Periodistas, Granada", "Bola de Oro, Granada",
            "Campus de la Salud, Granada", "Carrera de la Virgen - Paseo del Salón, Granada", "Catedral, Granada",
            "Centro, Granada", "Figares, Granada", "Gran Capitán, Granada",
            "Los Pajaritos, Granada", "Plaza de Toros, Granada", "Recogidas, Granada",
            "Ronda - Arabial, Granada", "San Ildefonso, Granada", "San Matías - Pavaneras, Granada",
            "Zaidín, Granada", "Armilla", "Atarfe", "Cajar", "Gojar", "Huétor-Vega", "La Zubia", "Monachil", "Otro"
            ].index(localizacion) # Datos para el test en locust
        )

        with col_right:
            # Planta
            piso = st.radio(
                "Planta",
                ["Bajo", "Primeros pisos", "Ultimos pisos", "Muchas plantas"],
                index=["Bajo", "Primeros pisos", "Ultimos pisos"].index(piso),
                horizontal=True
            )
            
            # Caracteristicas extras
            st.markdown("**Características extras:**")
            feature_col1, feature_col2 = st.columns(2)

            with feature_col1:
                ascensor = st.checkbox("Ascensor", value=ascensor)
                garaje = st.checkbox("Garaje", value=garaje)
                calefaccion = st.checkbox("Calefacción", value=calefaccion)
                aire_acondicionado = st.checkbox("Aire acondicionado", value=aire_acondicionado)

            with feature_col2:
                trastero = st.checkbox("Trastero", value=trastero)
                terraza = st.checkbox("Terraza", value=terraza)
                piscina = st.checkbox("Piscina", value=piscina)
                zonas_verdes = st.checkbox("Zonas verdes", value=zonas_verdes)
        
        # Boton submit
        submitted = st.form_submit_button("Calcular Precio de Alquiler") or params.get("submit") == ["true"]

# Procesamiento despues del submit
if submitted:

    try:
        # 1. Crear df con los datos del formulario
        input_data = {
            'metros_reales': metros,
            'habitaciones': habitaciones,
            'baños': banios,
            'ascensor': int(ascensor),
            'garaje': int(garaje),
            'calefaccion': int(calefaccion),
            'aire_acondicionado': int(aire_acondicionado),
            'trastero': int(trastero),
            'terraza': int(terraza),
            'piscina': int(piscina),
            'zonas_verdes': int(zonas_verdes),
            'localizacion': localizacion,
            'piso': piso.replace(" ", "_")            
        }

        input_df = pd.DataFrame([input_data])

        # 2. Aplicar one-hot encoding como en el entrenamiento
        input_encoded = pd.get_dummies(input_df, dtype='int', columns=['localizacion', 'piso'])
       
        # 3. Asegurar que tenemos todas las columnas esperadas
            # Se crea una lista con las columnas que no estan excluyendo las columnas titulo y precio
        missing_cols = [col for col in enconded_columns if col not in input_encoded.columns and col != 'titulo' and col != 'precio']
        for col in missing_cols:
            if col != 'precio': # Excluir la variable objetivo si está en las columnas para asegurar
                input_encoded[col] = 0

        # 4. Ordenar columnas como el modelo espera
        input_encoded = input_encoded.reindex(columns=[col for col in enconded_columns if col != 'titulo' and col != 'precio'], fill_value=0)

        # 5. Realizar prediccion
        prediccion = model.predict(input_encoded)

        # 6. Mostrar resultados
        st.success("Resultado de la Predicción")

        # 7. Mostrar el precio estimado
        price_mean = price_mean()
        
        # Calcular los rangos
        precio_bajo = price_mean - 100
        precio_alto = price_mean + 100

        # Determinar el delta según los rangos
        if prediccion[0] < precio_bajo:
            delta = "Precio competitivo"
            delta_color = "normal"
            st.markdown(mod.METRIC_ARROW_ROTATE, unsafe_allow_html=True) # Gira la flecha hacia abajo
        elif precio_bajo <= prediccion[0] <= precio_alto:
            delta = "Precio normal"
            delta_color = "off"
            st.markdown(mod.METRIC_ARROW_DISABLE, unsafe_allow_html=True) # Desactivar flecha
        elif prediccion[0] > precio_alto:
            delta = "Precio alto"
            delta_color = "inverse"

        st.metric(
            label="**Precio estimado de alquiler mensual**",
            value=f"{prediccion[0]:.2f} €",
            delta=delta,
            delta_color=delta_color
        )
    except Exception as e:
        st.error(f"❌ Error al realizar la predicción: {str(e)}")
        st.error("Por favor verifica que todos los datos estén correctamente ingresados")

    st.caption("***Transparencia ante todo:*** Esta herramienta te ofrece una estimación orientativa, " \
    "no se recomienda tomar decisiones críticas basandose solamente en este resultado. " \
    "Además, factores como el estado de la vivienda o si tiene características especiales no siempre están reflejados en la predicción." \
    " Por eso, es recomendable hacer un análisis más detallado y consultar con un profesional si lo consideras necesario.")    

with st.container():
    st.markdown(mod.FOOTER,unsafe_allow_html=True)

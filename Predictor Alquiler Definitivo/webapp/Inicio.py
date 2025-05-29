import streamlit as st
import settings.modstopage as mod
import base64

st.set_page_config(
    page_title="Predictor de Alquileres - Granada",
    page_icon=":material/location_city:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(mod.INICIO, unsafe_allow_html=True)
st.markdown("<h1>Bienvenido a la página de inicio</h1>", unsafe_allow_html=True)

# Espaciado
st.markdown("<br><br>", unsafe_allow_html=True)

# Crear columnas con espacios laterales
left_space, col1, col2, right_space = st.columns([1, 3, 3, 1])

# Botones dentro de las columnas
with col1:
    if st.button("Predecir precio vivienda", key="button_1"):
        st.switch_page("pages/01_Predecir_precio.py")

with col2:
    if st.button("Información del mercado", key="button_2"):
        st.switch_page("pages/02_Informacion_del_mercado.py")

st.markdown(mod.FOOTER, unsafe_allow_html=True)        
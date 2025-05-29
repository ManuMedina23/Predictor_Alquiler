import streamlit as st
import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from settings.db_connection import get_engine
from settings.models import Incidencia

# Configuracion de la pagina
st.set_page_config(
    page_title="Contacto", 
    page_icon=":material/location_city:", 
    layout="centered")

# Parametros para la conexion con la bd
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para guardar las incidencias
def guardar_incidencia(incidencia):
    # Variable de tipo session
    db: Session = SessionLocal()
    try:
        db.add(incidencia)
        db.commit()
        db.refresh(incidencia)
    except:
        st.error("Error enviando la incidencia, vuelvelo a intentar más tarde")
    finally:
        db.close()
        
# Funcion para validar el formato del email
def validar_email(email):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, email) is not None


# Titulo pagina
st.header("Mande su incidencia", divider="violet")

# Formulario de incidencia
with st.form("login_form", clear_on_submit=True):
    nombre = st.text_input("Nombre")
    email = st.text_input("Email")
    asunto = st.text_input("Asunto")
    mensaje = st.text_area("Mensaje")
    submit_button = st.form_submit_button("Enviar")

# Verificaciones de que los datos no esten vacios y sean correctos
if submit_button:
    if nombre.strip():
        if validar_email(email):
            if asunto.strip():
                if mensaje.strip():
                    nueva_incidencia = Incidencia(
                        nombre = nombre,
                        email = email,
                        asunto = asunto,
                        mensaje = mensaje
                    )
                    guardar_incidencia(nueva_incidencia)
                    st.info(f"Incidencia número {nueva_incidencia.id_incidencia} registrada")
                else:
                    st.error("El mensaje no puede estar vacio")
            else:
                st.error("El asunto no puede estar vacio")
        else:
            st.error("Email incorrecto")
    else:
        st.error("El nombre no puede estar vacio")    

    
import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
import bcrypt
from settings.db_connection import get_engine
from settings.models import Usuario, Incidencia

# Configuracion pagina streamlit
st.set_page_config(
    page_title="Admin", 
    page_icon=":material/location_city:", 
    layout="wide")

# Parametros para la conexion con la bd
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Funcion para autenticar 
def auntenticar_usuario(nombre, password):
    # Variable de tipo Session
    db: Session = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.nombre == nombre).one()
        # Comprueba si el hash de la contraseña introducida es igual a la guardada en la bd
        if bcrypt.checkpw(password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
            return usuario
        else:
            return None
    except NoResultFound:
        return None
    finally:
        db.close()
        engine.dispose()

# Funcion para obtener un df de las incidencias registradas en la bd
def obtener_incidencias():
    db: Session = SessionLocal()
    try:
        incidencias = db.query(Incidencia).all()
        data = [i.__dict__ for i in incidencias]
        for fila in data:
            fila.pop("_sa_instance_state", None)  # Limpiar metadata interna de SQLAlchemy    
        return pd.DataFrame(data)
    finally:
        db.close()
        
# Funcion para guardar los cambios de la incidencias en la BD
def guardar_cambios_incidencias(df_original, df_editado):
    db: Session = SessionLocal()
    try:
        for i in range(len(df_original)):
            row_original = df_original.iloc[i]
            row_editado = df_editado.iloc[i]
            cambios = {}
            for columna in df_original.columns:
                val_original = row_original[columna]
                val_editado = row_editado[columna]

                if val_original != val_editado:
                    # Convertir tipo NumPy a tipo nativo de Python
                    if isinstance(val_editado, (np.integer, np.int64)):
                        val_editado = int(val_editado)
                    elif isinstance(val_editado, (np.floating, np.float64)):
                        val_editado = float(val_editado)
                    elif isinstance(val_editado, (np.bool_,)):
                        val_editado = bool(val_editado)
                    elif isinstance(val_editado, (np.str_,)):
                        val_editado = str(val_editado)
                    
                    cambios[columna] = val_editado

            if cambios:
                id_incidencia = row_original["id_incidencia"]
                if isinstance(id_incidencia, (np.integer, np.int64)):
                    id_incidencia = int(id_incidencia)

                incidencia = db.query(Incidencia).filter(
                    Incidencia.id_incidencia == id_incidencia
                ).first()
                for campo, valor in cambios.items():
                    setattr(incidencia, campo, valor)
        db.commit()
        st.success("Cambios guardados correctamente.")

    except Exception as e:
        st.error("Ocurrió un error al guardar los cambios.")
        st.text(str(e))
    finally:
        db.close()            


# Titulo pagina
# Si aun NO esta logueado se mostrará el formulario de login
if not st.session_state.get("authenticated"):
    st.markdown("<h1 style='text-align: center;'>Iniciar Sesión</h1>", unsafe_allow_html=True)
    # Formulario de login
    with st.form("login_form"):
        nombre = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Entrar")

    if submit_button:
        usuario = auntenticar_usuario(nombre, password)
        if usuario:
            st.success(f"Bienvenido {usuario.nombre}")
            st.session_state["authenticated"] = True
            st.session_state["es_admin"] = usuario.es_admin
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
# Si ya esta logueado se mostrará las opciones disponibles           
else:
    if st.session_state.get("es_admin"):
        st.title("Página administrador")

        #Guardar df incidencias en la session si aun no esta
        if "df_actual" not in st.session_state:
            # Cargar incidencias
            df_original = obtener_incidencias()   
            st.session_state.df_actual = df_original.copy()
            st.rerun()
        else: 
            df_original = st.session_state.df_actual
            # Si el df esta vacio mostrar que no hay incidencias
            if df_original.empty:
                st.error("No existen incidencias actualmente")
            # En caso contrario mostrar el df
            else:    
                # Se fuerza el orden de las columnas
                orden_columnas = [
                    "id_incidencia",
                    "nombre",
                    "email",
                    "asunto",
                    "mensaje",
                    "en_curso",
                    "finalizada",
                    "observaciones"
                ]
                df_original = df_original[orden_columnas]

                st.header("Gestionar Incidencias", divider="violet")

                # Editar incidencias
                df_editado = st.data_editor(
                    df_original,
                    use_container_width=True,
                    num_rows="fixed",  # Para que no se agreguen nuevas filas
                    key="editor"
                    )
                        
                # Guardas cambios en las incidencias
                if st.button("Guardar cambios"):
                    guardar_cambios_incidencias(df_original, df_editado)
                    # Actualizar el DataFrame de incidencias en sesión
                    st.session_state.df_actual = df_editado.copy()
                    col1, col2 = st.columns([1,9])
                    with col1:
                        # El primer guardado funciona correctamente, si tras el se intenta volver a editar al pinchar fuera del valor
                        # este ultimo cambio se va a borrar y habría que volver a escribirlo siendo frustante
                        # con este boton se fuerza el refresco de la tabla y se puede editar con total seguridad de nuevo
                        if st.button("Refrescar"):                          
                            st.session_state.df_actual = obtener_incidencias().copy()
                    with col2:
                        st.info("Importante refrescar tras guardar un cambio ")
                                             
        
    else:
        st.info("No tienes ningun permiso")
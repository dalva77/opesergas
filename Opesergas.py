# C:/python_projects/opesergas/Inicio.py

import streamlit as st
from src import database_manager
from src import config_manager

# --- CONFIGURACIÓN DE LA PÁGINA (se aplica a todas las páginas) ---
st.set_page_config(
    page_title="Opesergas",  # Este es el título de la pestaña del navegador
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CÓDIGO DE INICIALIZACIÓN (se ejecuta una vez al iniciar) ---
# Se asegura de que las tablas 'examenes' y 'resultados' existan.
database_manager.initialize_database()

# --- ELEMENTOS GLOBALES DE LA BARRA LATERAL (se muestran en todas las páginas) ---
mode = config_manager.get_current_mode()
if mode == "dummy":
    st.sidebar.warning("⚠️ MODO DE PRUEBAS ACTIVO")

st.sidebar.success("Selecciona una página arriba para empezar.")


# --- CONTENIDO DE LA PÁGINA DE INICIO ---
st.title("✅ Opesergas: Prepara tu Examen")

st.markdown(
    """
    ¡Bienvenida **Mónica** 😊! 

    Esta aplicación está diseñada para ayudarte a practicar para tus exámenes de oposición
    del SERGAS (Servicio Gallego de Salud) utilizando preguntas de convocatorias anteriores.

    **¿Cómo empezar?**

    1.  Usa el menú de la izquierda para navegar a la sección **"Nuevo Examen"**.
    2.  Elige el número de preguntas que deseas.
    3.  ¡Comienza a practicar!

    ¡Mucha suerte en tu estudio!
    """
)

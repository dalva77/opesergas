import streamlit as st
from src import database_manager

# --- INICIALIZACIÓN DE LA BASE DE DATOS ---
# Se asegura de que las tablas 'examenes' y 'resultados' existan.
database_manager.initialize_database()

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Inicio",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PÁGINA PRINCIPAL ---
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

st.sidebar.success("Selecciona una página arriba para empezar.")

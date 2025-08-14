# Registro de Decisiones de Diseño del Proyecto Opesergas

Este documento recoge las decisiones de arquitectura y diseño clave tomadas durante el desarrollo del proyecto, junto con su contexto y justificación.

---

### Decisión 1: Elección del Framework para la Interfaz de Usuario

*   **Fecha:** 2025-08-14
*   **Decisión:** Se utilizará **Streamlit** para el desarrollo de la interfaz de usuario del Producto Mínimo Viable (MVP).
*   **Contexto y Alternativas:**
    *   Se necesitaba un framework de Python para construir una aplicación de escritorio o una interfaz web local.
    *   Las alternativas consideradas fueron:
        *   **Flet:** Moderno y potente, pero con una comunidad más pequeña.
        *   **NiceGUI:** Fácil de usar, pero genera una aplicación web en lugar de una de escritorio nativa.
        *   **PyQt/PySide:** Muy potente y personalizable, pero con una curva de aprendizaje elevada y mayor verbosidad.
        *   **Tkinter:** Incluido en Python, pero con un aspecto visual anticuado.
*   **Justificación:**
    *   **Velocidad de Desarrollo:** Streamlit permite crear un prototipo funcional con una velocidad inigualable, lo cual es ideal para la fase de MVP.
    *   **Familiaridad:** El usuario ya tiene cierta experiencia con Streamlit, lo que reduce la curva de aprendizaje.
    *   **Bajo Riesgo:** La arquitectura del proyecto separa la lógica de negocio (`database_manager.py`) de la interfaz de usuario. Si en el futuro Streamlit resulta ser demasiado limitante, migrar la "vista" a otro framework será una tarea de bajo coste, ya que el núcleo de la aplicación permanecerá intacto.

---

### Decisión 2: Arquitectura de la Aplicación

*   **Fecha:** 2025-08-14
*   **Decisión:** La aplicación se estructurará en tres capas principales:
    1.  **Capa de Datos (`database_manager.py`):** Un módulo aislado que gestiona toda la interacción con la base de datos SQLite. No tendrá ninguna dependencia de la interfaz de usuario.
    2.  **Capa de Interfaz de Usuario (Streamlit):** Compuesta por `app.py` (página principal) y los scripts dentro de la carpeta `pages/` (para las diferentes secciones de la aplicación).
    3.  **Capa de Testing (`tests/`):** Un conjunto de tests (usando `pytest`) que verificarán la correctitud de la capa de datos de forma independiente.
*   **Contexto:**
    *   Se necesitaba una estructura que fuera mantenible, escalable y, sobre todo, que facilitara las pruebas unitarias.
    *   Las aplicaciones de Streamlit pueden volverse difíciles de testear si la lógica de negocio está mezclada con el código de la interfaz.
*   **Justificación:**
    *   **Testabilidad:** Desacoplar la lógica de la base de datos permite crear tests robustos y fiables para el núcleo de la aplicación, garantizando su correcto funcionamiento.
    *   **Mantenibilidad:** La separación de responsabilidades hace que el código sea más fácil de entender, modificar y depurar.
    *   **Escalabilidad:** La arquitectura de múltiples páginas de Streamlit (`pages/`) permite añadir nuevas funcionalidades (como una página de estadísticas) de forma modular sin afectar al código existente.

---

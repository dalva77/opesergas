# Registro de Decisiones de Diseño del Proyecto Opesergas

Este documento recoge las decisiones de arquitectura y diseño clave tomadas durante el desarrollo del proyecto, junto con su contexto y justificación.

---

### Decisión 1: Elección del Framework para la Interfaz de Usuario

* **Fecha:** 2025-08-14
* **Decisión:** Se utilizará **Streamlit** para el desarrollo de la interfaz de usuario del Producto Mínimo Viable (MVP).
* **Contexto y Alternativas:**
  * Se necesitaba un framework de Python para construir una aplicación de escritorio o una interfaz web local.
  * Las alternativas consideradas fueron:
    * **Flet:** Moderno y potente, pero con una comunidad más pequeña.
    * **NiceGUI:** Fácil de usar, pero genera una aplicación web en lugar de una de escritorio nativa.
    * **PyQt/PySide:** Muy potente y personalizable, pero con una curva de aprendizaje elevada y mayor verbosidad.
    * **Tkinter:** Incluido en Python, pero con un aspecto visual anticuado.
* **Justificación:**
  * **Velocidad de Desarrollo:** Streamlit permite crear un prototipo funcional con una velocidad inigualable, lo cual es ideal para la fase de MVP.
  * **Familiaridad:** El usuario ya tiene cierta experiencia con Streamlit, lo que reduce la curva de aprendizaje.
  * **Bajo Riesgo:** La arquitectura del proyecto separa la lógica de negocio (`database_manager.py`) de la interfaz de usuario. Si en el futuro Streamlit resulta ser demasiado limitante, migrar la "vista" a otro framework será una tarea de bajo coste, ya que el núcleo de la aplicación permanecerá intacto.

---

### Decisión 2: Arquitectura de la Aplicación

* **Fecha:** 2025-08-14
* **Decisión:** La aplicación se estructurará en tres capas principales:
    1. **Capa de Datos (`database_manager.py`):** Un módulo aislado que gestiona toda la interacción con la base de datos SQLite. No tendrá ninguna dependencia de la interfaz de usuario.
    2. **Capa de Interfaz de Usuario (Streamlit):** Compuesta por `app.py` (página principal) y los scripts dentro de la carpeta `pages/` (para las diferentes secciones de la aplicación).
    3. **Capa de Testing (`tests/`):** Un conjunto de tests (usando `pytest`) que verificarán la correctitud de la capa de datos de forma independiente.
* **Contexto:**
  * Se necesitaba una estructura que fuera mantenible, escalable y, sobre todo, que facilitara las pruebas unitarias.
  * Las aplicaciones de Streamlit pueden volverse difíciles de testear si la lógica de negocio está mezclada con el código de la interfaz.
* **Justificación:**
  * **Testabilidad:** Desacoplar la lógica de la base de datos permite crear tests robustos y fiables para el núcleo de la aplicación, garantizando su correcto funcionamiento.
  * **Mantenibilidad:** La separación de responsabilidades hace que el código sea más fácil de entender, modificar y depurar.
  * **Escalabilidad:** La arquitectura de múltiples páginas de Streamlit (`pages/`) permite añadir nuevas funcionalidades (como una página de estadísticas) de forma modular sin afectar al código existente.

---

### Decisión 3: Arquitectura y Flujo de la Interfaz de Usuario (MVP)

*   **Fecha:** 2025-08-15
*   **Decisión:** El flujo completo de un examen se gestionará dentro de un único script (`pages/1_Nuevo_Examen.py`), utilizando el objeto `st.session_state` de Streamlit para controlar el estado y presentar diferentes "pantallas" lógicas al usuario de forma secuencial. La interacción con la base de datos se minimizará: una lectura al inicio y una única escritura transaccional al final.
*   **Contexto:** Se necesita un patrón de diseño para la interfaz que sea compatible con el modelo de ejecución de Streamlit (que re-ejecuta el script en cada interacción) y que, al mismo tiempo, ofrezca una experiencia de usuario fluida y sea resiliente a errores o cierres inesperados.
*   **Justificación:**
    *   **Gestión de Estado Idiomática:** El uso de `st.session_state` es la forma nativa y recomendada por Streamlit para mantener la información a lo largo de las interacciones del usuario, evitando soluciones más complejas.
    *   **Flujo Lógico Multi-Pantalla:** El script `pages/1_Nuevo_Examen.py` implementará la siguiente lógica condicional basada en el estado:
        1.  **Pantalla de Configuración (Estado por defecto):** Si `'exam_in_progress'` no está en `st.session_state`, se muestra la interfaz para elegir el número de preguntas. Al empezar, se cargan las preguntas en el estado de sesión y se activa el flag `'exam_in_progress'`.
        2.  **Pantalla de Realización:** Mientras `'exam_in_progress'` sea `True`, se muestra la pregunta actual. Las respuestas del usuario se van acumulando en `st.session_state` sin tocar la base de datos.
        3.  **Pantalla de Resultados:** Una vez respondidas todas las preguntas, se muestra el resumen. En este punto, y solo en este punto, se llama a la función `database_manager.save_exam_flow()` para persistir todos los datos (examen, resultados, estadísticas) de forma atómica.
    *   **Resiliencia y Consistencia:** Este diseño garantiza la robustez del sistema:
        *   **A Nivel de Aplicación:** `st.session_state` es volátil. Si la aplicación se cierra a mitad de un examen, el estado se pierde y el usuario comienza de cero en el siguiente arranque, sin estados inconsistentes.
        *   **A Nivel de Base de Datos:** Dado que todas las operaciones de escritura están encapsuladas en una única transacción (`save_exam_flow`), es imposible que un examen quede guardado a medias en la base de datos. O se guarda todo, o no se guarda nada.

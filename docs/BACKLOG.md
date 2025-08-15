# Backlog del Proyecto Opesergas

Este documento contiene la lista de tareas planificadas para el desarrollo de la aplicación.

---

## Fase 1: Lógica de Negocio y Preparación del Entorno

**Objetivo:** Construir y verificar el núcleo de la aplicación, asegurando que la lógica de la base de datos sea robusta y fiable antes de desarrollar cualquier interfaz de usuario.

* **Tarea 1.1: Configuración del Entorno de Desarrollo**
  * [x] Actualizar `requirements.txt` para incluir `streamlit` y `pytest`.
  * [x] Crear la estructura de carpetas inicial: `pages/`, `tests/` y `src/`.

* **Tarea 1.2: Desarrollo del Gestor de Base de Datos (`src/database_manager.py`)**
  * [x] Crear el fichero `src/database_manager.py`.
  * [x] Implementar `get_db_connection()` para conectar con `database/questions.db`.
  * [x] Implementar `initialize_database()` para crear las tablas `examenes` y `resultados` si no existen.
  * [x] Implementar `get_questions(num_questions)` para obtener preguntas aleatorias.
  * [x] Implementar `create_exam_session()` para iniciar un nuevo examen.
  * [x] Implementar `save_result()` para guardar la respuesta de un usuario.
  * [x] Implementar `update_question_stats()` para actualizar las estadísticas de una pregunta.
  * [x] Implementar `finalize_exam_session()` para marcar un examen como completado.
  * [x] Implementar la función transaccional `save_exam_flow()` que agrupe las operaciones de guardado.

* **Tarea 1.3: Creación de Tests para el Gestor de Base de Datos**
  * [x] Crear el fichero `tests/test_database_manager.py`.
  * [x] Escribir un test para `initialize_database()` que verifique la creación de las tablas.
  * [x] Escribir tests para `get_questions()`.
  * [x] Escribir tests para `create_exam_session()`.
  * [x] Escribir tests para `save_result()`.
  * [x] Escribir tests para `update_question_stats()`.
  * [x] Escribir un test para `finalize_exam_session()`.
  * [x] Escribir un test para la función transaccional `save_exam_flow()`.

---

## Fase 2: Implementación del Producto Mínimo Viable (MVP) - Interfaz de Usuario

**Objetivo:** Desarrollar la interfaz de usuario con Streamlit que permita a un usuario realizar un examen completo y ver sus resultados.

* **Tarea 2.1: Creación de la Página Principal (`app.py`)**
  * [ ] Crear el fichero `app.py`.
  * [ ] Añadir un título y un texto de bienvenida.
  * [ ] Incluir una breve instrucción sobre cómo navegar a las diferentes secciones usando la barra lateral.

* **Tarea 2.2: Implementación del Flujo de Examen (`pages/1_Nuevo_Examen.py`)**
  * [ ] Crear el fichero `pages/1_Nuevo_Examen.py`.
  * [ ] **Sub-tarea 2.2.1: Configuración del Examen**
    * [ ] Añadir un campo numérico para que el usuario elija el número de preguntas.
    * [ ] Añadir un botón "Empezar Examen".
  * [ ] **Sub-tarea 2.2.2: Realización del Examen**
    * [ ] Al pulsar el botón, obtener las preguntas de la base de datos usando `database_manager`.
    * [ ] Almacenar el estado del examen (preguntas, respuestas del usuario, pregunta actual) en `st.session_state`.
    * [ ] Mostrar una pregunta y sus opciones a la vez.
    * [ ] Usar botones o un radio group para la selección de respuesta.
    * [ ] Implementar la navegación entre preguntas (p. ej., un botón "Siguiente").
  * [ ] **Sub-tarea 2.2.3: Revisión de Resultados**
    * [ ] Al finalizar, calcular la puntuación.
    * [ ] Mostrar un resumen (ej. "Aciertos: 8/10").
    * [ ] Mostrar la lista completa de preguntas del examen, destacando la respuesta del usuario y la respuesta correcta para cada una.
  * [ ] **Sub-tarea 2.2.4: Persistencia de Resultados**
    * [ ] En segundo plano, al finalizar el examen, llamar a la función transaccional `save_exam_flow()` de `database_manager`.

---

## Fase 3: Documentación y Refinamiento

**Objetivo:** Completar la documentación del proyecto y realizar mejoras basadas en el MVP.

* **Tarea 3.1: Rellenar Ficheros de Documentación**
  * [ ] Actualizar `README.md` con la descripción final, estructura de ficheros y guías de uso.
  * [x] Rellenar `ARCHITECTURE.md` con la descripción de los componentes.
  * [x] Rellenar `DECISIONS.md` con las decisiones tomadas.
  * [x] Mantener `CHANGELOG.md` actualizado.

* **Tarea 3.2: Mejoras Futuras (Post-MVP)**
  * [ ] Implementar la página de `Estadisticas.py`.
  * [ ] Añadir filtros para la selección de preguntas (por `tags`, `fuente`, `anno`).
  * [ ] Mejorar el diseño visual de la aplicación.

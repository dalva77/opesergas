# Backlog del Proyecto Opesergas

Este documento contiene la lista de tareas planificadas para el desarrollo de la aplicación.

---

## Fase 1: Lógica de Negocio y Preparación del Entorno

**Objetivo:** Construir y verificar el núcleo de la aplicación, asegurando que la lógica de la base de datos sea robusta y fiable antes de desarrollar cualquier interfaz de usuario.

*   **Tarea 1.1: Configuración del Entorno de Desarrollo**
    *   [x] Actualizar `requirements.txt` para incluir `streamlit` y `pytest`.
    *   [x] Crear la estructura de carpetas inicial: `pages/`, `tests/` y `src/`.
*   **Tarea 1.2: Desarrollo del Gestor de Base de Datos (`src/database_manager.py`)**
    *   [x] Crear el fichero `src/database_manager.py`.
    *   [x] Implementar `get_db_connection()` para conectar con `database/questions.db`.
    *   [x] Implementar `initialize_database()` para crear las tablas `examenes` y `resultados` si no existen.
    *   [x] Implementar `get_questions(num_questions)` para obtener preguntas aleatorias.
    *   [x] Implementar `create_exam_session()` para iniciar un nuevo examen.
    *   [x] Implementar `save_result()` para guardar la respuesta de un usuario.
    *   [x] Implementar `update_question_stats()` para actualizar las estadísticas de una pregunta.
    *   [x] Implementar `finalize_exam_session()` para marcar un examen como completado.
    *   [x] Implementar la función transaccional `save_exam_flow()` que agrupe las operaciones de guardado.
*   **Tarea 1.3: Creación de Tests para el Gestor de Base de Datos**
    *   [x] Crear el fichero `tests/test_database_manager.py`.
    *   [x] Escribir un test para `initialize_database()` que verifique la creación de las tablas.
    *   [x] Escribir tests para `get_questions()`.
    *   [x] Escribir tests para `create_exam_session()`.
    *   [x] Escribir tests para `save_result()`.
    *   [x] Escribir tests para `update_question_stats()`.
    *   [x] Escribir un test para `finalize_exam_session()`.
    *   [x] Escribir un test para la función transaccional `save_exam_flow()`.

---

## Fase 2: Implementación y Validación del MVP

**Objetivo:** Desarrollar y verificar una interfaz de usuario funcional que permita a un usuario realizar un examen completo y ver sus resultados.

*   **Tarea 2.1: Creación de la Página Principal (`app.py`)**
    *   [x] Crear el fichero `app.py`.
    *   [x] Añadir un título y un texto de bienvenida.
    *   [x] Incluir una llamada a `initialize_database()` para asegurar que la BBDD está lista.
*   **Tarea 2.2: Implementación del Flujo de Examen (`pages/1_Nuevo_Examen.py`)**
    *   [x] Crear el fichero `pages/1_Nuevo_Examen.py`.
    *   [x] **Sub-tarea 2.2.1: Configuración del Examen**
    *   [x] **Sub-tarea 2.2.2: Realización del Examen**
    *   [x] **Sub-tarea 2.2.3: Revisión de Resultados**
    *   [x] **Sub-tarea 2.2.4: Persistencia de Resultados**
*   **Tarea 2.3: Validación Manual Exhaustiva del MVP (Prioritaria)**
    *   [ ] Verificar que la lógica de aciertos/fallos en la pantalla de resultados es siempre correcta.
    *   [ ] Comprobar manualmente en la base de datos que las tablas `examenes`, `resultados` y `preguntas` se actualizan correctamente tras completar un examen.

---

## Fase 3: Documentación y Refinamiento

**Objetivo:** Completar la documentación del proyecto y realizar mejoras basadas en el MVP.

*   **Tarea 3.1: Rellenar Ficheros de Documentación**
    *   [x] Actualizar `README.md` con la descripción final, estructura de ficheros y guías de uso.
    *   [x] Rellenar `ARCHITECTURE.md` con la descripción de los componentes.
    *   [x] Rellenar `DECISIONS.md` con las decisiones tomadas.
    *   [x] Mantener `CHANGLOG.md` actualizado.
*   **Tarea 3.2: Mejoras y Correcciones (Post-MVP)**
    *   [ ] Investigar y corregir el nombre de la página principal ("app") en el menú lateral.
    *   [ ] Implementar la página de `Estadisticas.py`.
    *   [ ] Añadir filtros para la selección de preguntas (por `tags`, `fuente`, `anno`).
    *   [ ] Mejorar el diseño visual de la aplicación.
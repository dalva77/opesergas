# Changelog del Proyecto Opesergas

## [0.3.0] - 2025-08-16

### Added

*   **Implementación del MVP (Fase 2):**
    *   Creado el punto de entrada de la aplicación `app.py` con la página de bienvenida y la inicialización de la base de datos.
    *   Implementado el flujo completo de examen en `pages/1_Nuevo_Examen.py`, incluyendo las pantallas de configuración, realización y revisión de resultados.

### Changed

*   **Refactorización de la API de `database_manager`:**
    *   Se ha modificado la firma de la función `save_exam_flow` para aceptar una única lista de resultados (`results`), mejorando la abstracción y el desacoplamiento con la interfaz de usuario.
    *   La lógica para calcular el total de preguntas y aciertos ahora reside completamente en el backend.

### Fixed

*   **Bug de Integración:**
    *   Solucionado un `TypeError` que ocurría al finalizar un examen debido a una discrepancia en los argumentos entre la UI y el `database_manager`.
*   **Suite de Pruebas:**
    *   Actualizado el test `test_save_exam_flow_guarda_todo_atomicamente` para alinearlo con la nueva firma de la función refactorizada, manteniendo la cobertura del 100%.

## [0.2.0] - 2025-08-15

### Added

*   **Finalización de la Lógica de Negocio (Fase 1):**
    *   Implementada y testeada la función `finalize_exam_session` para completar un examen.
    *   Implementada y testeada la función transaccional `save_exam_flow`, que gestiona de forma atómica todo el proceso de guardado de un examen.
    *   La suite de tests ahora cubre el 100% del `database_manager`.

### Fixed

*   **Entorno de Testing:**
    *   Añadido un fichero `pytest.ini` para configurar el `pythonpath`, solucionando errores de `ModuleNotFoundError` durante la recolección de tests.
*   **Robustez del Código:**
    *   Corregido un `warning` de Pylance en `_create_exam_session` para gestionar de forma segura un posible retorno `None` de `cursor.lastrowid`, evitando potenciales `TypeError`.

## [0.1.0] - 2025-08-14

### Added

* **Estructura Inicial del Proyecto:**
  * Creadas las carpetas `src/` para el código fuente, `tests/` para las pruebas y `pages/` para las vistas de Streamlit.
  * Actualizado `requirements.txt` con las dependencias `streamlit` y `pytest`.

* **Núcleo de Lógica de Base de Datos (`src/database_manager.py`):**
  * Implementado el gestor de la base de datos con un patrón de funciones públicas/privadas para garantizar la consistencia de los datos mediante transacciones.
  * Añadidas funciones para inicializar la base de datos (`initialize_database`).
  * Añadidas funciones para la gestión del ciclo de vida de un examen:
    * `get_questions()`
    * `create_exam_session()`
    * `save_result()`
    * `update_question_stats()`

* **Suite de Pruebas (`tests/test_database_manager.py`):**
  * Desarrollada una suite de tests completa con `pytest` para el `database_manager`.
  * Implementada una estrategia de testing robusta que utiliza bases de datos temporales en fichero para asegurar un entorno de pruebas aislado y realista.
  * Añadidos tests unitarios para todas las funciones implementadas en el `database_manager`.

* **Documentación:**
  * Actualizados `AI_CONTEXT.MD`, `BACKLOG.MD` y `CHANGELOG.MD` para reflejar el estado actual del proyecto.
  * Verificado y documentado el esquema exacto de la tabla `preguntas` de la base de datos.
### Resumen de Contexto para el Desarrollo de la App de Tests

**Asunto:** Sesión de implementación del núcleo de la lógica de negocio (`database_manager.py`) y su suite de tests. Se ha establecido una base de código robusta y verificada.

**1. Objetivo Final del Proyecto**

El objetivo sigue siendo desarrollar una aplicación de escritorio con Streamlit que permita a los usuarios generar exámenes tipo test personalizados a partir de una base de datos SQLite.

**2. Estado Actual del Proyecto**

* **Estructura de Ficheros:** Se ha creado la carpeta `src/` para alojar el código fuente de la aplicación, separándolo de los scripts de `utils/`. También se ha creado la carpeta `tests/`.
* **Lógica de Negocio (`src/database_manager.py`):**
  * Se ha implementado un patrón de funciones públicas/privadas para la gestión de conexiones y transacciones, garantizando la atomicidad y la consistencia de los datos.
  * **Funciones implementadas y testeadas:**
    * `initialize_database()`
    * `get_questions()`
    * `create_exam_session()`
    * `save_result()`
    * `update_question_stats()`
  * **Funciones pendientes:**
    * `finalize_exam_session()`
    * La función de alto nivel `save_exam_flow()` que gestionará la transacción completa de guardar un examen.
* **Testing (`tests/test_database_manager.py`):**
  * Se ha establecido una suite de tests robusta con `pytest`.
  * Se ha implementado una estrategia de testing que utiliza una **base de datos temporal en fichero** para cada test, lo que permite verificar el comportamiento real del `database_manager` sin efectos secundarios.
* **Esquema de la Base de Datos:**
  * Se ha verificado el esquema real de la tabla `preguntas` en la base de datos (`database/questions.db`), confirmando la existencia y el tipo de todas las columnas, incluidas las de estadísticas: `veces_preguntada`, `veces_acertada` y `veces_fallada`.

**3. Arquitectura y Decisiones Clave**

* Se ha decidido colocar el código fuente de la aplicación en `src/`, manteniendo `app.py` y `pages/` en la raíz para la compatibilidad con Streamlit.
* Se ha consolidado el patrón de diseño para `database_manager.py` que combina funciones públicas (para operaciones simples) y privadas (para ser orquestadas dentro de transacciones complejas), resolviendo así el problema de la consistencia de los datos.

**4. Próximos Pasos (Punto de Partida para la Siguiente Sesión)**

La siguiente sesión debe continuar directamente con el ciclo TDD donde lo hemos dejado:

* **Tarea Inmediata:** **Tarea 1.2 / 1.3 (Continuación)**.
* **Acción 1:** Añadir el test para la función `finalize_exam_session()` en `tests/test_database_manager.py`.
* **Acción 2:** Ejecutar los tests para verlo fallar.
* **Acción 3:** Implementar la función `finalize_exam_session()` en `src/database_manager.py`.
* **Acción 4:** Ejecutar los tests de nuevo para confirmar que todos pasan.
* **Acción 5:** Proceder con la implementación de la función transaccional `save_exam_flow()`.

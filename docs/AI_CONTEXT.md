### Resumen de Contexto para el Desarrollo de la App de Tests

**Asunto:** Sesión de arranque para el diseño y planificación del proyecto "Opesergas". Se ha establecido la arquitectura, el plan de desarrollo y se ha completado la documentación inicial del proyecto.

**1. Objetivo Final del Proyecto**

El objetivo es desarrollar una aplicación de escritorio con Streamlit que permita a los usuarios generar exámenes tipo test personalizados a partir de una base de datos SQLite ya existente que contiene un banco de preguntas de oposiciones del SERGAS.

**2. Estado Actual del Proyecto**

* **Base de Datos:** Se parte de una base de datos (`backup_database/questions.db`) que contiene únicamente la tabla `preguntas`, ya poblada. La aplicación deberá ser capaz de crear las tablas `examenes` y `resultados` en su primer arranque si estas no existen.
* **Planificación:** Se ha definido un plan de desarrollo detallado y por fases, que se encuentra en `docs/BACKLOG.md`.
* **Arquitectura:** Se ha decidido una arquitectura de 3 capas (Presentación, Lógica, Datos) que está documentada en `docs/ARCHITECTURE.md`.
* **Decisiones de Diseño:** Las decisiones clave, como la elección de Streamlit y la estructura de la aplicación, han sido documentadas en `docs/DECISIONS.md`.
* **Documentación Principal:** El fichero `README.md` ha sido completado con toda la información relevante del proyecto.

**3. Arquitectura Acordada**

* **Capa de Presentación (UI):** Streamlit. Ficheros `app.py` y `pages/*.py`.
* **Capa de Lógica de Negocio:** Un módulo `database_manager.py` que contendrá toda la lógica de interacción con la base de datos, completamente aislado de la UI.
* **Capa de Datos:** Base de datos SQLite en `database/questions.db`.
* **Capa de Testing:** Una carpeta `tests/` con tests de `pytest` para validar la capa de lógica de negocio.

**4. Próximos Pasos (Punto de Partida para la Siguiente Sesión)**

La siguiente sesión debe comenzar directamente con la ejecución de la **Fase 1** del plan de desarrollo definido en `docs/BACKLOG.md`.

* **Tarea Inmediata:** **Tarea 1.1: Configuración del Entorno de Desarrollo**.
  * **Acción 1:** Actualizar el fichero `requirements.txt` para añadir las dependencias `streamlit` y `pytest`.
  * **Acción 2:** Crear las carpetas vacías `pages/` y `tests/` en la raíz del proyecto para alojar los futuros scripts.

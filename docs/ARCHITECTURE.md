# Arquitectura del Proyecto Opesergas

Este documento describe la arquitectura de alto nivel de la aplicación, sus componentes principales, sus responsabilidades y las interacciones entre ellos.

---

## 1. Visión General

La aplicación está diseñada siguiendo una **arquitectura de tres capas**, que separa claramente la presentación (interfaz de usuario), la lógica de negocio (gestión de datos) y el almacenamiento de datos (base de datos).

El objetivo de esta arquitectura es conseguir un sistema:

* **Modular:** Cada componente tiene una responsabilidad única.
* **Testable:** La lógica de negocio se puede probar de forma aislada.
* **Mantenible:** Los cambios en un componente tienen un impacto mínimo en los demás.

A continuación se muestra un diagrama de los componentes principales y sus interacciones:

```
┌─────────────────────────┐
│                         │
│  Interfaz de Usuario    │
│ (Streamlit)             │
│                         │
│  - app.py (Raíz)        │
│  - pages/*.py (Raíz)    │
│                         │
└───────────┬─────────────┘
            │
            │ (Llama a funciones)
            ▼
┌─────────────────────────┐
│                         │
│  Lógica de Negocio      │
│ (src/database_manager.py) │
│                         │
│  - Conexión a BBDD      │
│  - Consultas SQL        │
│  - Lógica de examen     │
│                         │
└───────────┬─────────────┘
            │
            │ (Ejecuta transacciones)
            ▼
┌─────────────────────────┐
│                         │
│  Capa de Datos          │
│ (SQLite)                │
│                         │
│  - database/questions.db│
│                         │
└─────────────────────────┘
```

---

## 2. Descripción de Componentes

### 2.1. Interfaz de Usuario (Capa de Presentación)

* **Tecnología:** **Streamlit**.
* **Ficheros:** `app.py` (punto de entrada) y los scripts dentro de `pages/`. Ambos residen en la **raíz del proyecto** para asegurar la compatibilidad con el sistema de páginas de Streamlit.
* **Responsabilidades:**
  * Presentar la información al usuario de forma interactiva.
  * Capturar las entradas del usuario (ej. número de preguntas, selección de respuestas).
  * Gestionar el estado de la sesión de la interfaz de usuario (usando `st.session_state`).
  * Mostrar los resultados y el feedback al usuario.
* **Interacciones:**
  * **NO** interactúa directamente con la base de datos.
  * **SÍ** llama a las funciones públicas expuestas por el `database_manager.py` para solicitar datos o ejecutar operaciones.

### 2.2. Lógica de Negocio (Capa de Lógica)

* **Tecnología:** **Python estándar**.
* **Fichero:** `src/database_manager.py`.
* **Responsabilidades:**
  * Actuar como la única puerta de enlace (`gateway`) a la base de datos.
  * Contener toda la lógica de negocio: selección de preguntas, creación de exámenes, cálculo de estadísticas, etc.
  * Gestionar las transacciones para garantizar la consistencia de los datos (atomicidad).
  * Abstraer los detalles de las consultas SQL. La capa de presentación no sabe SQL, solo llama a funciones como `get_questions()`.
* **Interacciones:**
  * Es invocado por la capa de Interfaz de Usuario.
  * Ejecuta consultas y transacciones (lectura y escritura) sobre la base de datos SQLite.

### 2.3. Almacenamiento de Datos (Capa de Datos)

* **Tecnología:** **SQLite**.
* **Fichero:** `database/questions.db`.
  * **Nota Importante:** Este fichero es la base de datos "activa" de la aplicación. Está incluido en el fichero `.gitignore` para evitar que los datos de sesión del usuario se suban al repositorio. Para la configuración inicial, debe copiarse desde `backup_database/questions.db`.
* **Responsabilidades:**
  * Almacenar de forma persistente todos los datos de la aplicación.
  * Garantizar la integridad de los datos a través de su esquema.
* **Esquema de Tablas:**
  * **`preguntas`**: El banco central de preguntas. Su estructura es la siguiente:
    ```sql
    CREATE TABLE preguntas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero INTEGER NOT NULL,
        numero_original TEXT,
        enunciado TEXT NOT NULL,
        opciones TEXT NOT NULL,       -- Objeto de opciones serializado como string JSON
        raw_ocr TEXT,
        fuente TEXT NOT NULL,
        anno INTEGER NOT NULL,
        respuesta_correcta TEXT,
        tags TEXT,                    -- Lista de tags serializada como string JSON
        veces_preguntada INTEGER NOT NULL DEFAULT 0,
        veces_acertada INTEGER NOT NULL DEFAULT 0,
        veces_fallada INTEGER NOT NULL DEFAULT 0,
        UNIQUE(numero, fuente, anno)
    );
    ```
  * **`examenes`**: Registra cada examen que se realiza (fecha, total de preguntas, aciertos, etc.).
  * **`resultados`**: Almacena la respuesta de un usuario a una pregunta específica dentro de un examen.

---

## 3. Flujo de Datos (Ejemplo: Realizar un Examen)

1. **Usuario (en UI):** Pide un nuevo examen de 10 preguntas.
2. **`pages/1_Nuevo_Examen.py` (UI):** Llama a `database_manager.get_questions(10)`.
3. **`src/database_manager.py` (Lógica):** Abre una conexión, ejecuta una `SELECT` en `database/questions.db`, devuelve la lista de preguntas a la UI y cierra la conexión.
4. **Usuario (en UI):** Responde a todas las preguntas.
5. **`pages/1_Nuevo_Examen.py` (UI):** Al finalizar, recopila todas las respuestas y llama a una única función transaccional como `database_manager.save_exam_flow(...)`.
6. **`src/database_manager.py` (Lógica):** Inicia una transacción en la base de datos para ejecutar de forma atómica todas las operaciones necesarias:
    * Crear una nueva fila en la tabla `examenes`.
    * Crear múltiples filas en la tabla `resultados`.
    * Actualizar los contadores en la tabla `preguntas` para cada pregunta.
    * Marcar el examen como finalizado.
7. **`src/database_manager.py` (Lógica):** Confirma (`commit`) la transacción si todo ha ido bien, o la revierte (`rollback`) en caso de error, y devuelve un mensaje de éxito a la UI.
8. **`pages/1_Nuevo_Examen.py` (UI):** Muestra al usuario la pantalla de resultados.
# Arquitectura del Proyecto Opesergas

Este documento describe la arquitectura de alto nivel de la aplicación, sus componentes principales, sus responsabilidades y las interacciones entre ellos.

---

## 1. Visión General

La aplicación está diseñada siguiendo una **arquitectura de tres capas**, que separa claramente la presentación (interfaz de usuario), la lógica de negocio (gestión de datos) y el almacenamiento de datos (base de datos).

El objetivo de esta arquitectura es conseguir un sistema:
*   **Modular:** Cada componente tiene una responsabilidad única.
*   **Testable:** La lógica de negocio se puede probar de forma aislada.
*   **Mantenible:** Los cambios en un componente tienen un impacto mínimo en los demás.

A continuación se muestra un diagrama de los componentes principales y sus interacciones:

```
┌─────────────────────────┐
│                         │
│  Interfaz de Usuario    │
│ (Streamlit)             │
│                         │
│  - app.py               │
│  - pages/*.py           │
│                         │
└───────────┬─────────────┘
            │
            │ (Llama a funciones)
            ▼
┌─────────────────────────┐
│                         │
│  Lógica de Negocio      │
│ (database_manager.py)   │
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

*   **Tecnología:** **Streamlit**.
*   **Ficheros:** `app.py`, `pages/1_Nuevo_Examen.py`, etc.
*   **Responsabilidades:**
    *   Presentar la información al usuario de forma interactiva.
    *   Capturar las entradas del usuario (ej. número de preguntas, selección de respuestas).
    *   Gestionar el estado de la sesión de la interfaz de usuario (usando `st.session_state`).
    *   Mostrar los resultados y el feedback al usuario.
*   **Interacciones:**
    *   **NO** interactúa directamente con la base de datos.
    *   **SÍ** llama a las funciones expuestas por el `database_manager.py` para solicitar datos o para enviar operaciones a realizar (ej. "dame 10 preguntas", "guarda este resultado").

### 2.2. Lógica de Negocio (Capa de Lógica)

*   **Tecnología:** **Python estándar**.
*   **Fichero:** `database_manager.py`.
*   **Responsabilidades:**
    *   Actuar como la única puerta de enlace (`gateway`) a la base de datos.
    *   Contener toda la lógica de negocio:
        *   Cómo se seleccionan las preguntas.
        *   Cómo se crea una sesión de examen.
        *   Cómo se calculan y actualizan las estadísticas.
        *   Cómo se guardan los resultados.
    *   Abstraer los detalles de las consultas SQL. La capa de presentación no sabe SQL, solo llama a funciones como `get_questions()`.
*   **Interacciones:**
    *   Es invocado por la capa de Interfaz de Usuario.
    *   Ejecuta consultas y transacciones (lectura y escritura) sobre la base de datos SQLite.

### 2.3. Almacenamiento de Datos (Capa de Datos)

*   **Tecnología:** **SQLite**.
*   **Fichero:** `database/questions.db`.
*   **Responsabilidades:**
    *   Almacenar de forma persistente todos los datos de la aplicación.
    *   Garantizar la integridad de los datos a través de su esquema (claves primarias, claves foráneas, etc.).
    *   Las tablas principales son:
        *   `preguntas`: El banco central de preguntas.
        *   `examenes`: Registra cada examen que se realiza.
        *   `resultados`: Almacena la respuesta de un usuario a una pregunta específica dentro de un examen.
*   **Interacciones:**
    *   Solo es accedida por la capa de Lógica de Negocio (`database_manager.py`).

---

## 3. Flujo de Datos (Ejemplo: Realizar un Examen)

1.  **Usuario (en UI):** Pide un nuevo examen de 10 preguntas.
2.  **`1_Nuevo_Examen.py` (UI):** Llama a `database_manager.get_questions(10)`.
3.  **`database_manager.py` (Lógica):** Ejecuta una `SELECT` en `database/questions.db` y devuelve la lista de preguntas a la UI.
4.  **Usuario (en UI):** Responde a una pregunta.
5.  **`1_Nuevo_Examen.py` (UI):** Al finalizar el examen, recopila todas las respuestas y llama a `database_manager.save_exam_results(...)` con los datos.
6.  **`database_manager.py` (Lógica):** Inicia una transacción en la base de datos para:
    *   Crear una nueva fila en la tabla `examenes`.
    *   Crear múltiples filas en la tabla `resultados` (una por cada pregunta).
    *   Actualizar los contadores (`veces_preguntada`, `veces_acertada`, etc.) en la tabla `preguntas`.
7.  **`database_manager.py` (Lógica):** Devuelve un mensaje de éxito a la UI.
8.  **`1_Nuevo_Examen.py` (UI):** Muestra al usuario la pantalla de resultados.

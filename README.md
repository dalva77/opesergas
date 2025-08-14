# Proyecto Opesergas

## Tabla de Contenidos

1. [Descripción](#1-descripción)
2. [Finalidad del Proyecto](#2-finalidad-del-proyecto)
3. [Estructura de carpetas](#3-estructura-de-carpetas)
4. [Características Clave](#4-características-clave)
5. [Instalación](#5-instalación)
6. [Uso Básico](#6-uso-básico)

---

## 1. Descripción

**Opesergas** es una aplicación de escritorio diseñada para ayudar en la preparación de exámenes de oposición. Permite a los usuarios generar y realizar tests personalizados a partir de un extenso banco de preguntas reales extraídas de convocatorias anteriores del SERGAS (Servicio Gallego de Salud).

Los siguientes ficheros, ubicados en la carpeta `docs/`, describen el proyecto en profundidad y deben ser consultados para obtener una visión completa de su estado y evolución:

* **ARCHITECTURE.md:** Descripción de alto nivel de los componentes del proyecto, sus responsabilidades y las relaciones entre ellos.
* **BACKLOG.md:** Lista ordenada de tareas planificadas en el desarrollo del proyecto.
* **DECISIONS.md:** Compendio de decisiones de diseño tomadas durante el desarrollo, junto con sus motivaciones.
* **CHANGELOG.md:** Histórico de cambios relevantes en el proyecto.
* **AI_CONTEXT.md**: Resumen del contexto de la última sesión de trabajo para facilitar la continuidad.

## 2. Finalidad del Proyecto

El objetivo principal es ofrecer una herramienta de estudio interactiva y eficaz. La aplicación permite a los opositores:

* Practicar con preguntas oficiales y actualizadas.
* Generar exámenes a medida, eligiendo el número de preguntas.
* Recibir feedback inmediato al finalizar cada test.
* Realizar un seguimiento de su progreso a través de estadísticas de aciertos y fallos por pregunta.

## 3. Estructura de carpetas

A continuación se muestra la estructura de ficheros y carpetas del proyecto. La carpeta `sources/`, que contiene los ficheros originales de los exámenes, ha sido omitida por no ser relevante para el funcionamiento de la aplicación final.

```
opesergas/
├── .flake8               # Fichero de configuración para el linter Flake8.
├── .gitignore            # Especifica los ficheros que Git debe ignorar.
├── GEMINI.md             # Instrucciones específicas para la IA durante el desarrollo.
├── README.md             # Este fichero.
├── requirements.txt      # Lista de dependencias de Python para el proyecto.
│
├── database/             # Carpeta donde residirá la base de datos activa de la aplicación.
│
├── backup_database/
│   ├── backup_description.txt # Descripción del contenido de la BBDD de backup.
│   └── questions.db      # BBDD inicial con la tabla 'preguntas' ya poblada.
│
├── docs/                 # Carpeta con toda la documentación del proyecto.
│   ├── AI_CONTEXT.MD
│   ├── ARCHITECTURE.md
│   ├── BACKLOG.md
│   ├── CHANGELOG.md
│   ├── DECISIONS.md
│   └── TEMPLATE_AI_CONTEXT.md
│
└── utils/                # Scripts de apoyo para el pipeline de datos (no son parte de la app).
    ├── add_answers.py    # Script para añadir respuestas correctas a los JSON.
    ├── json2db.py        # Script para migrar los datos de JSON a la BBDD SQLite.
    ├── ocr.py            # Script para extraer texto de los PDFs de exámenes.
    ├── ocr2json.py       # Script para limpiar el texto OCR y estructurarlo en JSON.
    └── tests/            # Carpeta para tests de los scripts de utilidades.
```

## 4. Características Clave

El desarrollo del proyecto se ha planificado en las siguientes fases o hitos (milestones):

* **Fase 1: Lógica de Negocio y Preparación del Entorno**
  * **Objetivo:** Construir y verificar el núcleo de la aplicación, asegurando que la lógica de la base de datos sea robusta y fiable antes de desarrollar cualquier interfaz de usuario.

* **Fase 2: Implementación del Producto Mínimo Viable (MVP)**
  * **Objetivo:** Desarrollar la interfaz de usuario con Streamlit que permita a un usuario realizar un examen completo (configuración, ejecución y revisión de resultados).

* **Fase 3: Documentación y Refinamiento**
  * **Objetivo:** Completar toda la documentación del proyecto y planificar futuras mejoras sobre el MVP, como un panel de estadísticas avanzadas o filtros de preguntas.

## 5. Instalación

Siga los siguientes pasos para poner en marcha la aplicación:

1. **Prerrequisitos:** Asegúrese de tener instalado Python 3.8 o superior.

2. **Clonar el Repositorio (si aplica):**

    ```bash
    git clone <url-del-repositorio>
    cd opesergas
    ```

3. **Instalar Dependencias:** Instale todas las librerías necesarias ejecutando:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configuración de la Base de Datos:**
    * El banco inicial de preguntas se encuentra en `backup_database/questions.db`. Copie este fichero a la carpeta `database/`.
    * **Importante:** La base de datos inicial solo contiene la tabla `preguntas`. La aplicación está diseñada para comprobar, en su primer arranque, si las tablas `examenes` y `resultados` existen. Si no existen, las creará automáticamente sin alterar la tabla `preguntas` existente.

## 6. Uso Básico

Una vez completada la instalación, puede lanzar la aplicación ejecutando el siguiente comando desde la raíz del proyecto:

```bash
streamlit run app.py
```

Esto abrirá una nueva pestaña en su navegador web con la interfaz de la aplicación. Desde allí, podrá navegar a la sección "Nuevo Examen" para comenzar a practicar.

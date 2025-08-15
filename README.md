# Proyecto Opesergas

**Versión actual: 0.3.0**

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
├── app.py                # Punto de entrada principal de la aplicación Streamlit.
├── GEMINI.md             # Instrucciones específicas para la IA durante el desarrollo.
├── README.md             # Este fichero.
├── requirements.txt      # Lista de dependencias de Python para el proyecto.
│
├── backup_database/
│   └── questions.db      # BBDD inicial con la tabla 'preguntas' ya poblada.
│
├── database/             # Carpeta donde reside la base de datos activa de la aplicación.
│   └── questions.db      # (Ignorado por Git)
│
├── docs/                 # Carpeta con toda la documentación del proyecto.
│   ├── AI_CONTEXT.MD
│   ├── ARCHITECTURE.md
│   └── ...
│
├── pages/                # Páginas de la aplicación Streamlit (ej. Nuevo Examen).
│
├── src/                  # Código fuente principal de la aplicación.
│   └── database_manager.py # Módulo con toda la lógica de negocio y BBDD.
│
├── tests/                # Tests unitarios para el código de la aplicación.
│   └── test_database_manager.py
│
└── utils/                # Scripts de apoyo para el pipeline de datos (no son parte de la app).
    └── ...
```

## 4. Características Clave

El desarrollo del proyecto se ha planificado en las siguientes fases o hitos (milestones):

* **Fase 1: Lógica de Negocio y Preparación del Entorno (Completada)**
  * **Objetivo:** Construir y verificar el núcleo de la aplicación, asegurando que la lógica de la base de datos sea robusta y fiable antes de desarrollar cualquier interfaz de usuario.

* **Fase 2: Implementación del Producto Mínimo Viable (MVP) (Completada)**
  * **Objetivo:** Desarrollar la interfaz de usuario con Streamlit que permita a un usuario realizar un examen completo y ver sus resultados. La aplicación ya es funcional.

* **Fase 3: Validación y Refinamiento (En curso)**
  * **Objetivo:** Realizar pruebas exhaustivas sobre el MVP, completar la documentación y planificar futuras mejoras, como un panel de estadísticas avanzadas o filtros de preguntas.

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
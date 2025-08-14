"""
Módulo de gestión de la base de datos.

Este módulo centraliza todas las operaciones de la base de datos (lectura, escritura,
actualización) para la aplicación Opesergas. Actúa como una capa de abstracción
entre la lógica de la aplicación y la base de datos SQLite.
"""

import sqlite3
import os

# --- Configuración ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(ROOT_DIR, 'database', 'questions.db')


# --- Funciones de Gestión de la Base de Datos ---

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos SQLite.

    La conexión se configura para devolver filas que se comportan como diccionarios
    (claves de columna como nombres), lo que facilita el manejo de los datos.

    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _initialize_database(conn: sqlite3.Connection):
    """
    Inicializa la base de datos. (Función interna)

    Verifica la existencia de las tablas 'examenes' y 'resultados'. Si no existen,
    las crea. Esta función espera recibir un objeto de conexión activo.
    """
    cursor = conn.cursor()

    # Crear tabla 'examenes' si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS examenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finalizado BOOLEAN NOT NULL DEFAULT 0,
            total_preguntas INTEGER NOT NULL,
            aciertos INTEGER
        )
    ''')

    # Crear tabla 'resultados' si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            examen_id INTEGER NOT NULL,
            pregunta_id INTEGER NOT NULL,
            respuesta_usuario TEXT,
            es_correcta BOOLEAN,
            FOREIGN KEY (examen_id) REFERENCES examenes (id),
            FOREIGN KEY (pregunta_id) REFERENCES preguntas (id)
        )
    ''')


def initialize_database():
    """
    Inicializa la base de datos. (Función pública)

    Obtiene una conexión y crea las tablas de la aplicación si no existen.
    """
    conn = get_db_connection()
    try:
        with conn:
            _initialize_database(conn)
    finally:
        conn.close()


def _get_questions(conn: sqlite3.Connection, num_questions: int) -> list[sqlite3.Row]:
    """
    Obtiene un número específico de preguntas aleatorias. (Función interna)

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        num_questions (int): El número de preguntas a obtener.

    Returns:
        list[sqlite3.Row]: Una lista de objetos de fila (pregunta).
    """
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM preguntas ORDER BY RANDOM() LIMIT ?', (num_questions,))
    return cursor.fetchall()


def get_questions(num_questions: int) -> list[sqlite3.Row]:
    """
    Obtiene un número específico de preguntas aleatorias. (Función pública)

    Args:
        num_questions (int): El número de preguntas a obtener.

    Returns:
        list[sqlite3.Row]: Una lista de objetos de fila (pregunta).
    """
    conn = get_db_connection()
    try:
        return _get_questions(conn, num_questions)
    finally:
        conn.close()

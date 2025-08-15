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


def _create_exam_session(conn: sqlite3.Connection, total_preguntas: int) -> int:
    """
    Crea una nueva sesión de examen en la base de datos. (Función interna)

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        total_preguntas (int): Número de preguntas del examen.

    Returns:
        int: El ID de la nueva fila de examen creada.
    """
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO examenes (total_preguntas) VALUES (?)',
        (total_preguntas,)
    )
    exam_id = cursor.lastrowid
    if exam_id is None:
        raise RuntimeError("No se pudo crear la sesión de examen y obtener un ID.")
    return exam_id


def create_exam_session(total_preguntas: int) -> int:
    """
    Crea una nueva sesión de examen en la base de datos. (Función pública)

    Args:
        total_preguntas (int): Número de preguntas del examen.

    Returns:
        int: El ID de la nueva fila de examen creada.
    """
    conn = get_db_connection()
    try:
        with conn:
            exam_id = _create_exam_session(conn, total_preguntas)
        return exam_id
    finally:
        conn.close()


def _save_result(conn: sqlite3.Connection, examen_id: int, pregunta_id: int, respuesta_usuario: str, es_correcta: bool):
    """
    Guarda el resultado de una única pregunta en la base de datos. (Función interna)
    """
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO resultados (examen_id, pregunta_id, respuesta_usuario, es_correcta)
        VALUES (?, ?, ?, ?)
        ''',
        (examen_id, pregunta_id, respuesta_usuario, es_correcta)
    )


def save_result(examen_id: int, pregunta_id: int, respuesta_usuario: str, es_correcta: bool):
    """
    Guarda el resultado de una única pregunta en la base de datos. (Función pública)
    """
    conn = get_db_connection()
    try:
        with conn:
            _save_result(conn, examen_id, pregunta_id, respuesta_usuario, es_correcta)
    finally:
        conn.close()


def _update_question_stats(conn: sqlite3.Connection, pregunta_id: int, es_correcta: bool):
    """
    Actualiza las estadísticas de una pregunta. (Función interna)
    """
    cursor = conn.cursor()
    if es_correcta:
        cursor.execute(
            '''
            UPDATE preguntas
            SET veces_preguntada = veces_preguntada + 1,
                veces_acertada = veces_acertada + 1
            WHERE id = ?
            ''',
            (pregunta_id,)
        )
    else:
        cursor.execute(
            '''
            UPDATE preguntas
            SET veces_preguntada = veces_preguntada + 1,
                veces_fallada = veces_fallada + 1
            WHERE id = ?
            ''',
            (pregunta_id,)
        )


def update_question_stats(pregunta_id: int, es_correcta: bool):
    """
    Actualiza las estadísticas de una pregunta. (Función pública)
    """
    conn = get_db_connection()
    try:
        with conn:
            _update_question_stats(conn, pregunta_id, es_correcta)
    finally:
        conn.close()


def _finalize_exam_session(conn: sqlite3.Connection, examen_id: int, aciertos: int):
    """
    Actualiza un examen para marcarlo como finalizado. (Función interna)
    """
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE examenes
        SET finalizado = 1,
            aciertos = ?
        WHERE id = ?
        ''',
        (aciertos, examen_id)
    )


def finalize_exam_session(examen_id: int, aciertos: int):
    """
    Actualiza un examen para marcarlo como finalizado. (Función pública)
    """
    conn = get_db_connection()
    try:
        with conn:
            _finalize_exam_session(conn, examen_id, aciertos)
    finally:
        conn.close()


def save_exam_flow(results: list[dict]) -> int:
    """
    Guarda una sesión de examen completa de forma transaccional.

    Esta función orquesta la creación del examen, el guardado de cada resultado
    y la actualización de las estadísticas de las preguntas, asegurando que
    todas las operaciones se completen con éxito o ninguna lo haga (atomicidad).

    Args:
        results (list[dict]): Una lista de diccionarios, donde cada uno
            representa un resultado y contiene: 'question_id', 'selected_option'
            y 'is_correct'.

    Returns:
        int: El ID del examen creado y guardado.
    """
    conn = get_db_connection()
    total_preguntas = len(results)

    try:
        with conn:
            # 1. Crear la sesión de examen
            exam_id = _create_exam_session(conn, total_preguntas)

            # 2. Guardar cada resultado y actualizar estadísticas
            aciertos = 0
            for result in results:
                es_correcta = result['is_correct']
                if es_correcta:
                    aciertos += 1

                _save_result(
                    conn,
                    examen_id=exam_id,
                    pregunta_id=result['question_id'],
                    respuesta_usuario=result['selected_option'],
                    es_correcta=es_correcta
                )
                _update_question_stats(
                    conn,
                    pregunta_id=result['question_id'],
                    es_correcta=es_correcta
                )

            # 3. Finalizar el examen
            _finalize_exam_session(conn, exam_id, aciertos)

        return exam_id
    finally:
        conn.close()

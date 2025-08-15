"""
Tests para el módulo de gestión de la base de datos (database_manager.py).

Estos tests utilizan una base de datos en memoria para garantizar un entorno
limpio y aislado para cada prueba, evitando cualquier efecto secundario en la
base de datos real de la aplicación.
"""

import pytest
import sqlite3
from src import database_manager as db_manager

# --- Fixtures de Pytest ---


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """
    Fixture para crear y configurar una base de datos de prueba en un fichero temporal.

    Esta fixture realiza las siguientes acciones:
    1. Crea un fichero de base de datos temporal usando la fixture `tmp_path` de pytest.
    2. Usa `monkeypatch` para que `database_manager.DB_PATH` apunte a este fichero.
    3. Puebla la BBDD temporal con la tabla `preguntas` y datos de prueba.
    4. Cede el control al test.
    5. `tmp_path` se encarga de la limpieza automática del fichero después del test.
    """
    # 1. Crear el fichero de BBDD temporal
    db_path = tmp_path / "test_questions.db"

    # 2. Redirigir la constante DB_PATH del módulo
    monkeypatch.setattr(db_manager, 'DB_PATH', str(db_path))

    # 3. Conectar y poblar la BBDD con datos iniciales
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE preguntas (
            id INTEGER PRIMARY KEY,
            texto TEXT NOT NULL,
            opcion_a TEXT,
            opcion_b TEXT,
            opcion_c TEXT,
            opcion_d TEXT,
            respuesta_correcta TEXT,
            veces_preguntada INTEGER DEFAULT 0,
            veces_acertada INTEGER DEFAULT 0,
            veces_fallada INTEGER DEFAULT 0
        )
    ''')
    sample_questions = [
        (1, '¿Capital de Francia?', 'Madrid', 'París', 'Londres', 'Berlín', 'B', 10, 5, 5),
        (2, '¿2 + 2?', '3', '4', '5', '6', 'B', 20, 15, 5),
        (3, '¿Color del cielo?', 'Verde', 'Rojo', 'Azul', 'Amarillo', 'C', 5, 5, 0)
    ]
    cursor.executemany(
        'INSERT INTO preguntas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        sample_questions
    )
    conn.commit()
    conn.close()

    # Ceder el control al test (no necesitamos devolver nada)
    yield


# --- Tests para initialize_database ---

def test_initialize_database_crea_tablas_si_no_existen(temp_db):
    """
    Verifica que initialize_database() crea las tablas 'examenes' y 'resultados'
    en una base de datos que no las tiene.
    """
    # Act: Ejecutar la función de inicialización.
    # Esta se conectará a la BBDD temporal gracias al monkeypatch.
    db_manager.initialize_database()

    # Assert: Verificar que las tablas han sido creadas conectándonos de nuevo.
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examenes'")
    assert cursor.fetchone() is not None, "La tabla 'examenes' no fue creada."

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resultados'")
    assert cursor.fetchone() is not None, "La tabla 'resultados' no fue creada."
    conn.close()


def test_initialize_database_no_altera_datos_existentes(temp_db):
    """
    Verifica que ejecutar initialize_database() una segunda vez no borra ni
    altera los datos que ya existen en las tablas.
    """
    # Arrange: Ejecutar la inicialización una vez y añadir datos de prueba.
    db_manager.initialize_database()

    conn_setup = db_manager.get_db_connection()
    cursor_setup = conn_setup.cursor()
    cursor_setup.execute(
        "INSERT INTO examenes (id, total_preguntas, aciertos) VALUES (?, ?, ?)",
        (1, 10, 8)
    )
    conn_setup.commit()
    conn_setup.close()

    # Act: Ejecutar la inicialización por segunda vez.
    db_manager.initialize_database()

    # Assert: Verificar que los datos insertados previamente siguen intactos.
    conn_assert = db_manager.get_db_connection()
    cursor_assert = conn_assert.cursor()
    cursor_assert.execute("SELECT total_preguntas, aciertos FROM examenes WHERE id = 1")
    examen = cursor_assert.fetchone()
    conn_assert.close()

    assert examen is not None, "El examen de prueba fue eliminado."
    assert examen['total_preguntas'] == 10, "El valor de 'total_preguntas' fue alterado."
    assert examen['aciertos'] == 8, "El valor de 'aciertos' fue alterado."


# --- Tests para get_questions ---

def test_get_questions_devuelve_numero_correcto(temp_db):
    """
    Verifica que get_questions() devuelve el número exacto de preguntas solicitado.
    """
    # Act
    questions = db_manager.get_questions(num_questions=2)

    # Assert
    assert len(questions) == 2, "No se devolvió el número correcto de preguntas."


def test_get_questions_devuelve_formato_correcto(temp_db):
    """
    Verifica que los objetos devueltos son de tipo sqlite3.Row (diccionarios)
    y contienen las columnas esperadas.
    """
    # Act
    questions = db_manager.get_questions(num_questions=1)

    # Assert
    assert len(questions) > 0, "No se devolvieron preguntas."
    question = questions[0]
    assert isinstance(question, sqlite3.Row), "El formato de la pregunta no es sqlite3.Row."
    # Comprobar que se puede acceder a los campos por nombre de columna
    assert 'texto' in question.keys()
    assert 'opcion_a' in question.keys()
    assert question['texto'] == '¿Capital de Francia?' or \
        question['texto'] == '¿2 + 2?' or \
        question['texto'] == '¿Color del cielo?'


# --- Tests para el Flujo de Examen ---

def test_create_exam_session_crea_fila_y_devuelve_id(temp_db):
    """
    Verifica que create_exam_session() inserta una nueva fila en la tabla 'examenes'
    con los valores por defecto correctos y devuelve el ID del nuevo examen.
    """
    # Arrange: Asegurarse de que las tablas existen
    db_manager.initialize_database()

    # Act
    num_preguntas = 15
    exam_id = db_manager.create_exam_session(total_preguntas=num_preguntas)

    # Assert: Verificar que se devolvió un ID válido
    assert isinstance(exam_id, int)
    assert exam_id > 0

    # Assert: Verificar que la fila fue creada correctamente en la BBDD
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM examenes WHERE id = ?", (exam_id,))
    examen = cursor.fetchone()
    conn.close()

    assert examen is not None, "No se encontró la sesión de examen en la BBDD."
    assert examen['total_preguntas'] == num_preguntas
    assert examen['finalizado'] == 0, "El examen no debería estar finalizado."
    assert examen['aciertos'] is None, "Los aciertos deberían ser NULL al inicio."


def test_save_result_crea_fila_en_resultados(temp_db):
    """
    Verifica que save_result() inserta correctamente una fila en la tabla
    'resultados' con los datos proporcionados.
    """
    # Arrange: Crear las tablas y una sesión de examen de prueba
    db_manager.initialize_database()
    exam_id = db_manager.create_exam_session(total_preguntas=1)

    # Datos del resultado a guardar
    result_data = {
        "examen_id": exam_id,
        "pregunta_id": 1,  # ID de una de las preguntas de prueba
        "respuesta_usuario": "B",
        "es_correcta": True
    }

    # Act
    db_manager.save_result(**result_data)

    # Assert: Verificar que la fila fue creada en la BBDD
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resultados WHERE examen_id = ?", (exam_id,))
    resultado = cursor.fetchone()
    conn.close()

    assert resultado is not None, "No se encontró el resultado en la BBDD."
    assert resultado['pregunta_id'] == result_data['pregunta_id']
    assert resultado['respuesta_usuario'] == result_data['respuesta_usuario']
    assert resultado['es_correcta'] == result_data['es_correcta']


def test_update_question_stats_incrementa_contadores_acierto(temp_db):
    """
    Verifica que update_question_stats() incrementa 'veces_preguntada' y
    'veces_acertada' en caso de un acierto.
    """
    # Arrange: Los valores iniciales para la pregunta 1 son 10, 5, 5
    pregunta_id = 1

    # Act
    db_manager.update_question_stats(pregunta_id=pregunta_id, es_correcta=True)

    # Assert
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM preguntas WHERE id = ?", (pregunta_id,))
    stats = cursor.fetchone()
    conn.close()

    assert stats['veces_preguntada'] == 11
    assert stats['veces_acertada'] == 6
    assert stats['veces_fallada'] == 5


def test_update_question_stats_incrementa_contadores_fallo(temp_db):
    """
    Verifica que update_question_stats() incrementa 'veces_preguntada' y
    'veces_fallada' en caso de un fallo.
    """
    # Arrange: Los valores iniciales para la pregunta 2 son 20, 15, 5
    pregunta_id = 2

    # Act
    db_manager.update_question_stats(pregunta_id=pregunta_id, es_correcta=False)

    # Assert
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM preguntas WHERE id = ?", (pregunta_id,))
    stats = cursor.fetchone()
    conn.close()

    assert stats['veces_preguntada'] == 21
    assert stats['veces_acertada'] == 15
    assert stats['veces_fallada'] == 6


def test_finalize_exam_session_actualiza_examen(temp_db):
    """
    Verifica que finalize_exam_session() actualiza correctamente la fila
    del examen con el número de aciertos y lo marca como finalizado.
    """
    # Arrange: Crear las tablas y una sesión de examen de prueba
    db_manager.initialize_database()
    exam_id = db_manager.create_exam_session(total_preguntas=10)

    # Act
    aciertos = 8
    db_manager.finalize_exam_session(examen_id=exam_id, aciertos=aciertos)

    # Assert
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM examenes WHERE id = ?", (exam_id,))
    examen = cursor.fetchone()
    conn.close()

    assert examen is not None, "No se encontró el examen."
    assert examen['finalizado'] == 1, "El examen no se marcó como finalizado."
    assert examen['aciertos'] == aciertos, "El número de aciertos no se guardó correctamente."


# --- Tests para Flujo Transaccional ---

def test_save_exam_flow_guarda_todo_atomicamente(temp_db):
    """
    Test de integración para save_exam_flow.

    Verifica que la función:
    1. Crea la sesión de examen.
    2. Guarda todos los resultados individuales.
    3. Actualiza las estadísticas de cada pregunta.
    4. Finaliza el examen con el recuento de aciertos.
    5. Realiza todas las operaciones dentro de una única transacción.
    """
    # Arrange
    db_manager.initialize_database()
    questions = db_manager.get_questions(3)
    user_answers = [
        {"pregunta_id": questions[0]['id'], "respuesta_usuario": "B", "es_correcta": True},
        {"pregunta_id": questions[1]['id'], "respuesta_usuario": "A", "es_correcta": False},
        {"pregunta_id": questions[2]['id'], "respuesta_usuario": "C", "es_correcta": True},
    ]

    # Leer los valores iniciales de la pregunta que se va a acertar
    conn_setup = db_manager.get_db_connection()
    cursor_setup = conn_setup.cursor()
    cursor_setup.execute("SELECT * FROM preguntas WHERE id = ?", (questions[0]['id'],))
    initial_stats_q1 = cursor_setup.fetchone()
    conn_setup.close()

    # Act
    exam_id = db_manager.save_exam_flow(
        total_preguntas=len(questions),
        results_data=user_answers
    )

    # Assert
    assert isinstance(exam_id, int)

    conn = db_manager.get_db_connection()
    cursor = conn.cursor()

    # 1. Verificar que el examen se finalizó correctamente
    cursor.execute("SELECT * FROM examenes WHERE id = ?", (exam_id,))
    examen = cursor.fetchone()
    assert examen is not None
    assert examen['finalizado'] == 1
    assert examen['aciertos'] == 2
    assert examen['total_preguntas'] == 3

    # 2. Verificar que los resultados se guardaron
    cursor.execute("SELECT * FROM resultados WHERE examen_id = ?", (exam_id,))
    resultados = cursor.fetchall()
    assert len(resultados) == 3

    # 3. Verificar que las estadísticas de una pregunta se actualizaron
    cursor.execute("SELECT * FROM preguntas WHERE id = ?", (questions[0]['id'],))
    stats_q1 = cursor.fetchone()
    assert stats_q1['veces_preguntada'] == initial_stats_q1['veces_preguntada'] + 1
    assert stats_q1['veces_acertada'] == initial_stats_q1['veces_acertada'] + 1

    conn.close()

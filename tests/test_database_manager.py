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
            respuesta_correcta TEXT
        )
    ''')
    sample_questions = [
        (1, '¿Capital de Francia?', 'Madrid', 'París', 'Londres', 'Berlín', 'B'),
        (2, '¿2 + 2?', '3', '4', '5', '6', 'B'),
        (3, '¿Color del cielo?', 'Verde', 'Rojo', 'Azul', 'Amarillo', 'C')
    ]
    cursor.executemany(
        'INSERT INTO preguntas VALUES (?, ?, ?, ?, ?, ?, ?)',
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

import sqlite3
import json
import os

DB_FILENAME = 'dummy_questions.db'

# Datos de las preguntas triviales
dummy_data = [
    (1, '1', '¿Cuánto son 2 + 2?', json.dumps({'a': '3', 'b': '4', 'c': '5', 'd': '6'}), 'b', 'DUMMY_TEST', 2025, json.dumps(['matemáticas'])),
    (2, '2', '¿De qué color es el cielo en un día despejado?', json.dumps({'a': 'Verde', 'b': 'Azul', 'c': 'Rojo', 'd': 'Amarillo'}), 'b', 'DUMMY_TEST', 2025, json.dumps(['cultura general'])),
    (3, '3', '¿Cuál es la capital de España?', json.dumps({'a': 'Barcelona', 'b': 'Lisboa', 'c': 'París', 'd': 'Madrid'}), 'd', 'DUMMY_TEST', 2025, json.dumps(['geografía'])),
    (4, '4', '¿Qué sonido hace un gato?', json.dumps({'a': 'Guau', 'b': 'Miau', 'c': 'Oinc', 'd': 'Muu'}), 'b', 'DUMMY_TEST', 2025, json.dumps(['animales'])),
    (5, '5', 'Selecciona la opción correcta:', json.dumps({'a': 'Esta no', 'b': 'Esta tampoco', 'c': '¡Esta sí!', 'd': 'Esta seguro que no'}), 'c', 'DUMMY_TEST', 2025, json.dumps(['lógica'])),
    (6, '6', '¿Cuántos días tiene una semana?', json.dumps({'a': '5', 'b': '6', 'c': '7', 'd': '8'}), 'c', 'DUMMY_TEST', 2025, json.dumps(['cultura general'])),
    (7, '7', '¿Qué es lo contrario de "caliente"?', json.dumps({'a': 'Frío', 'b': 'Tibia', 'c': 'Picante', 'd': 'Húmedo'}), 'a', 'DUMMY_TEST', 2025, json.dumps(['lengua'])),
    (8, '8', '¿Qué planeta es conocido como el Planeta Rojo?', json.dumps({'a': 'Tierra', 'b': 'Júpiter', 'c': 'Marte', 'd': 'Venus'}), 'c', 'DUMMY_TEST', 2025, json.dumps(['ciencia'])),
    (9, '9', '¿Qué producen las abejas?', json.dumps({'a': 'Leche', 'b': 'Seda', 'c': 'Miel', 'd': 'Pan'}), 'c', 'DUMMY_TEST', 2025, json.dumps(['animales'])),
    (10, '10', '¿Cuántas ruedas tiene una bicicleta?', json.dumps({'a': '1', 'b': '2', 'c': '3', 'd': '4'}), 'b', 'DUMMY_TEST', 2025, json.dumps(['cultura general']))
]

def create_dummy_database():
    """Crea y puebla la base de datos dummy."""
    # Borra la BBDD si ya existe para empezar de cero
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)

    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    # Crear la tabla 'preguntas' con la misma estructura
    cursor.execute('''
    CREATE TABLE preguntas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero INTEGER NOT NULL,
        numero_original TEXT,
        enunciado TEXT NOT NULL,
        opciones TEXT NOT NULL,
        raw_ocr TEXT,
        fuente TEXT NOT NULL,
        anno INTEGER NOT NULL,
        respuesta_correcta TEXT,
        tags TEXT,
        veces_preguntada INTEGER NOT NULL DEFAULT 0,
        veces_acertada INTEGER NOT NULL DEFAULT 0,
        veces_fallada INTEGER NOT NULL DEFAULT 0,
        UNIQUE(numero, fuente, anno)
    )
    ''')

    # Insertar los datos
    for item in dummy_data:
        cursor.execute('''
        INSERT INTO preguntas (numero, numero_original, enunciado, opciones, respuesta_correcta, fuente, anno, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', item)

    # Crear las tablas 'examenes' y 'resultados' para que la app no falle
    cursor.execute('''
    CREATE TABLE examenes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        finalizado BOOLEAN NOT NULL DEFAULT 0,
        total_preguntas INTEGER NOT NULL,
        aciertos INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE resultados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        examen_id INTEGER NOT NULL,
        pregunta_id INTEGER NOT NULL,
        respuesta_usuario TEXT,
        es_correcta INTEGER,
        FOREIGN KEY (examen_id) REFERENCES examenes (id),
        FOREIGN KEY (pregunta_id) REFERENCES preguntas (id)
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Base de datos '{DB_FILENAME}' creada con éxito con {len(dummy_data)} preguntas.")

if __name__ == '__main__':
    create_dummy_database()

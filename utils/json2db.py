import sqlite3
import json
import argparse
from pathlib import Path
import sys

# ==============================================================================
# SCRIPT DE MIGRACIÓN DE PREGUNTAS JSON A BASE DE DATOS SQLITE
#
# DESCRIPCIÓN:
# Este script lee ficheros JSON de preguntas y los importa a una base de datos
# SQLite. Puede operar sobre un único fichero o sobre un directorio completo.
#
# FUNCIONALIDADES:
# - Acepta la ruta a la BBDD y la ruta a la fuente de datos (fichero/directorio).
# - Crea la base de datos y la tabla 'preguntas' si no existen.
# - Utiliza 'INSERT OR IGNORE' para evitar duplicados al re-ejecutarlo.
# - Proporciona feedback claro sobre el proceso, incluyendo preguntas añadidas
#   por fichero.
#
# ------------------------------------------------------------------------------
# INSTRUCCIONES DE USO:
#
# 1. PARA IMPORTAR UN ÚNICO FICHERO:
#    > python json2db.py mi_base.db examenes/ope_2021.json
#
# 2. PARA IMPORTAR TODOS LOS FICHEROS DE UN DIRECTORIO:
#    > python json2db.py mi_base.db examenes/
#
# ==============================================================================

# Constante con la definición de la tabla para mantener el código limpio.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS preguntas (
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
    UNIQUE(numero, fuente, anno)  -- Clave única para evitar duplicados
);
"""


def import_from_json(cursor, json_path: Path) -> int:
    """
    Importa preguntas desde un único fichero JSON a la base de datos.

    Args:
        cursor: El cursor de la base de datos para ejecutar comandos.
        json_path: La ruta al fichero JSON.

    Returns:
        El número de preguntas nuevas añadidas desde este fichero.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except json.JSONDecodeError:
        print(f"  -> ERROR: El fichero '{json_path.name}' no contiene un JSON válido. Se omite.")
        return 0
    except Exception as e:
        print(f"  -> ERROR: No se pudo leer el fichero '{json_path.name}': {e}. Se omite.")
        return 0

    added_count = 0
    for q in questions:
        # Serializar campos complejos a string JSON para guardarlos en la BBDD
        opciones_str = json.dumps(q.get('opciones', {}))
        tags_str = json.dumps(q.get('tags', []))

        # Insertar en la BBDD. 'OR IGNORE' es clave: si la clave única
        # (numero, fuente, anno) ya existe, simplemente no hace nada y no da error.
        cursor.execute("""
            INSERT OR IGNORE INTO preguntas (
                numero, numero_original, enunciado, opciones, raw_ocr,
                fuente, anno, respuesta_correcta, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q.get('numero'), q.get('numero_original'), q.get('enunciado'),
            opciones_str, q.get('raw_ocr'), q.get('fuente'), q.get('anno'),
            q.get('respuesta_correcta'), tags_str
        ))

        # cursor.rowcount nos dice si la inserción tuvo efecto (1) o fue ignorada (0)
        if cursor.rowcount > 0:
            added_count += 1

    return added_count


def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Importa preguntas de examen desde ficheros JSON a una base de datos SQLite.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "db_path",
        type=Path,
        help="Ruta al fichero de la base de datos SQLite (ej: 'oposiciones.db')."
    )
    parser.add_argument(
        "source_path",
        type=Path,
        help="Ruta a un fichero .json o a un directorio con ficheros .json."
    )
    args = parser.parse_args()

    db_path: Path = args.db_path
    source_path: Path = args.source_path

    # --- Comprobación de la ruta de origen ---
    if not source_path.exists():
        print(f"ERROR: La ruta de origen '{source_path}' no existe.")
        sys.exit(1)

    # --- Conexión y configuración de la BBDD ---
    db_existed = db_path.exists()
    try:
        # connect() crea el fichero si no existe
        con = sqlite3.connect(db_path)
        cur = con.cursor()
    except sqlite3.Error as e:
        print(f"ERROR: No se pudo conectar a la base de datos en '{db_path}': {e}")
        sys.exit(1)

    if not db_existed:
        print(f"INFO: La base de datos no existía en '{db_path}'. Creándola ahora.")

    # Crear la tabla si no existe. Es seguro ejecutarlo siempre.
    cur.execute(CREATE_TABLE_SQL)

    # --- Lógica principal de importación ---
    total_added = 0

    if source_path.is_file():
        if source_path.suffix.lower() == '.json':
            print(f"Procesando fichero: {source_path.name}")
            added = import_from_json(cur, source_path)
            total_added += added
            print(f"  -> Se han añadido {added} nuevas preguntas de '{source_path.name}'.")
        else:
            print(f"ERROR: El fichero de entrada debe ser un .json. Recibido: '{source_path.name}'")

    elif source_path.is_dir():
        print(f"Procesando directorio: {source_path}")
        json_files = sorted(list(source_path.glob('*.json')))
        if not json_files:
            print("  -> No se encontraron ficheros .json en el directorio.")

        for json_file in json_files:
            added = import_from_json(cur, json_file)
            total_added += added
            print(f"  -> Se han añadido {added} nuevas preguntas de '{json_file.name}'.")

    # --- Finalización ---
    if total_added > 0:
        print("\nGuardando cambios en la base de datos...")
        con.commit()
    else:
        print("\nNo se han añadido nuevas preguntas a la base de datos.")

    con.close()
    print("¡Proceso de importación finalizado!")


if __name__ == "__main__":
    main()

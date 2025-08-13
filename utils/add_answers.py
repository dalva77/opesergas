import json
import argparse
from pathlib import Path
import sys
import logging

# flake8: noqa: E501


# ==============================================================================
# SCRIPT PARA AÑADIR RESPUESTAS CORRECTAS A FICHEROS JSON DE PREGUNTAS
#
# DESCRIPCIÓN:
# Este script lee un fichero JSON de preguntas (generado por el script anterior)
# y un fichero de texto con las respuestas correctas, y fusiona ambos en un
# nuevo fichero JSON con el campo 'respuesta_correcta' actualizado.
#
# FUNCIONALIDADES:
# - Opera sobre un solo fichero JSON o en modo lote sobre un directorio.
# - Detección automática de ficheros de respuestas si no se especifica.
# - Nomenclatura automática para ficheros de salida si no se especifica.
# - Validación de datos y avisos sobre preguntas/respuestas huérfanas.
# - Validación del formato de las respuestas (A, B, C, D).
# - Normalización de respuestas a mayúsculas.
#
# ------------------------------------------------------------------------------
# INSTRUCCIONES DE USO:
#
# 1. MODO FICHERO ÚNICO (con valores por defecto):
#    (Asume que examen.txt existe en el mismo directorio que examen.json)
#    > python add_answers.py examen.json
#    -> Genera: examen_ANS.json
#
# 2. MODO FICHERO ÚNICO (especificando rutas):
#    > python add_answers.py C:\data\examen.json --answers C:\data\resp.txt --output C:\data\final.json
#
# 3. MODO LOTE (procesa todos los .json de la carpeta 'examenes'):
#    > python add_answers.py ./examenes/
#    -> Para cada 'prueba.json', buscará 'prueba.txt' y generará 'prueba_ANS.json'
#
# ==============================================================================

# --- Configuración del Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)


def process_file_pair(json_path: Path, answers_path: Path, output_path: Path):
    """
    Procesa un único par de ficheros JSON de preguntas y TXT de respuestas.
    """
    logging.info(f"--- Procesando '{json_path.name}' ---")

    # --- 1. Validar existencia de ficheros de entrada ---
    if not json_path.is_file():
        logging.error(f"El fichero de preguntas no existe: {json_path}")
        return False
    if not answers_path.is_file():
        logging.error(f"El fichero de respuestas no existe: {answers_path}")
        return False

    # --- 2. Leer y parsear el fichero de respuestas ---
    answers_map = {}
    try:
        with open(answers_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue  # Ignorar líneas vacías

                parts = line.split()
                if len(parts) != 2:
                    logging.warning(f"  - Línea mal formada en '{answers_path.name}' (línea {i}): '{line}'. Se ignora.")
                    continue

                num_str, answer = parts
                try:
                    q_num = int(num_str)
                    answer_upper = answer.strip().upper()

                    if answer_upper not in ['A', 'B', 'C', 'D']:
                        logging.warning(
                            f"  - Respuesta inválida en '{answers_path.name}' para pregunta {q_num}: '{answer}'. Se ignora.")
                        continue

                    answers_map[q_num] = answer_upper
                except ValueError:
                    logging.warning(
                        f"  - Número de pregunta no válido en '{answers_path.name}' (línea {i}): '{num_str}'. Se ignora.")
    except Exception as e:
        logging.error(f"No se pudo leer el fichero de respuestas '{answers_path}': {e}")
        return False

    # --- 3. Leer el fichero JSON de preguntas ---
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except json.JSONDecodeError:
        logging.error(f"El fichero '{json_path}' no es un JSON válido.")
        return False
    except Exception as e:
        logging.error(f"No se pudo leer el fichero de preguntas '{json_path}': {e}")
        return False

    # --- 4. Fusionar datos y validar ---
    updated_count = 0
    json_q_nums = set()

    for question in questions_data:
        q_num = question.get('numero')
        if q_num is None:
            logging.warning(f"  - Se encontró una pregunta sin campo 'numero' en '{json_path.name}'. Se ignora.")
            continue

        json_q_nums.add(q_num)

        if q_num in answers_map:
            question['respuesta_correcta'] = answers_map[q_num]
            updated_count += 1
        else:
            logging.warning(
                f"  - AVISO: La pregunta #{q_num} en '{json_path.name}' no tiene una respuesta correspondiente en '{answers_path.name}'.")

    # Comprobar si hay respuestas huérfanas (respuestas para preguntas que no existen)
    answer_q_nums = set(answers_map.keys())
    orphaned_answers = answer_q_nums - json_q_nums
    if orphaned_answers:
        for q_num in sorted(list(orphaned_answers)):
            logging.warning(
                f"  - AVISO: La respuesta para la pregunta #{q_num} en '{answers_path.name}' no tiene una pregunta correspondiente en '{json_path.name}'.")

    # --- 5. Guardar el fichero de salida ---
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        logging.info(f"✅ Proceso completado. {updated_count} preguntas actualizadas.")
        logging.info(f"   -> Fichero de salida guardado en: {output_path}\n")
        return True
    except Exception as e:
        logging.error(f"No se pudo escribir el fichero de salida '{output_path}': {e}")
        return False


def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Añade respuestas correctas a ficheros JSON de preguntas de examen.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Ruta al fichero .json de preguntas o a un directorio para procesar en lote."
    )
    parser.add_argument(
        "-a", "--answers",
        type=Path,
        default=None,
        help="Ruta al fichero .txt con las respuestas. (Por defecto: busca un .txt con el mismo nombre que el .json)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Ruta para el fichero .json de salida. (Por defecto: [nombre_original]_ANS.json)"
    )
    args = parser.parse_args()

    input_path: Path = args.input_path

    if not input_path.exists():
        logging.error(f"La ruta de entrada no existe: {input_path}")
        sys.exit(1)

    # --- MODO LOTE: Si la entrada es un directorio ---
    if input_path.is_dir():
        logging.info(f"Modo lote activado. Buscando ficheros .json en el directorio: {input_path}")
        if args.answers or args.output:
            logging.warning("Los argumentos --answers y --output se ignoran en modo lote.")

        json_files = sorted(list(input_path.glob('*.json')))
        if not json_files:
            logging.warning(f"No se encontraron ficheros .json en '{input_path}'.")
            sys.exit(0)

        processed_count = 0
        for json_file in json_files:
            # Ignorar ficheros que ya parecen ser de salida
            if json_file.stem.endswith('_ANS'):
                continue

            # Usar valores por defecto para los ficheros de respuestas y salida
            default_answers_path = json_file.with_suffix('.txt')
            default_output_path = json_file.with_name(f"{json_file.stem}_ANS.json")

            if process_file_pair(json_file, default_answers_path, default_output_path):
                processed_count += 1

        logging.info(f"--- Fin del modo lote. Se han procesado {processed_count} ficheros. ---")

    # --- MODO FICHERO ÚNICO: Si la entrada es un fichero ---
    elif input_path.is_file():
        if input_path.suffix.lower() != '.json':
            logging.error("El fichero de entrada debe ser un fichero .json")
            sys.exit(1)

        # Determinar rutas de ficheros de respuestas y de salida usando los valores por defecto si es necesario
        answers_path = args.answers if args.answers else input_path.with_suffix('.txt')
        output_path = args.output if args.output else input_path.with_name(f"{input_path.stem}_ANS.json")

        process_file_pair(input_path, answers_path, output_path)


if __name__ == "__main__":
    main()

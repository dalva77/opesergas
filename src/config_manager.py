# src/config_manager.py

import toml
import os

# Definir los nombres de fichero para cada modo
_DB_FILES = {
    "production": "questions.db",
    "dummy": "dummy_questions.db"
}

# Ruta base donde se encuentra el fichero de configuración
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_PATH = os.path.join(_BASE_DIR, "config.toml")


def get_database_path() -> str:
    """
    Lee el fichero config.toml y devuelve la ruta completa a la base de datos
    seleccionada.

    Si el fichero no existe o la clave es inválida, usa "production" por defecto.

    Returns:
        str: La ruta absoluta al fichero de la base de datos.
    """
    try:
        config = toml.load(_CONFIG_PATH)
        mode = config.get("database", {}).get("mode", "production")
    except FileNotFoundError:
        mode = "production"

    db_filename = _DB_FILES.get(mode, _DB_FILES["production"])
    db_path = os.path.join(_BASE_DIR, "database", db_filename)

    return db_path

def get_current_mode() -> str:
    """
    Devuelve el modo actual de la base de datos ("production" o "dummy").
    """
    try:
        config = toml.load(_CONFIG_PATH)
        mode = config.get("database", {}).get("mode", "production")
        return mode if mode in _DB_FILES else "production"
    except FileNotFoundError:
        return "production"

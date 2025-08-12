import argparse
import sys
from pathlib import Path
from typing import Optional

import pytesseract
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

# Mapeo simple de códigos de langdetect a Tesseract
# Ampliado con catalán, ya que estamos por aquí ;)
LANG_MAP = {
    "es": "spa",
    "ca": "cat",
    "en": "eng",
    "fr": "fra",
    "de": "deu",
    "it": "ita",
}


def detectar_idioma_en_muestra(texto_muestra: str) -> str:
    """Detecta el idioma de un texto y lo mapea a un código de Tesseract."""
    try:
        lang_code = detect(texto_muestra)
        # Por defecto español si no está mapeado
        return LANG_MAP.get(lang_code, "spa")
    except LangDetectException:
        print("   ⚠️ No se pudo detectar el idioma, usando español por defecto.")
        return "spa"


# MODIFICADO: La función ahora recibe la ruta de salida completa.
def procesar_pdf(pdf_path: Path, output_path: Path, lang: Optional[str], dpi: int):
    """
    Realiza OCR en un único fichero PDF y guarda el resultado como Markdown.
    Procesa el PDF página por página para conservar memoria.
    """
    print(f"\nProcessing: {pdf_path.name}")
    try:
        pdf_reader = PdfReader(pdf_path)
        num_paginas = len(pdf_reader.pages)
    except Exception as e:
        print(f"  ❌ Error al leer el PDF: {e}. Abortando.")
        return

    # --- Detección de idioma (si no se especifica) ---
    if not lang:
        print("  Detectando idioma en la primera página...")
        # Convierte solo la primera página para la muestra de texto
        pagina_muestra_img = convert_from_path(
            pdf_path, dpi=dpi, first_page=1, last_page=1)[0]
        texto_muestra = pytesseract.image_to_string(
            pagina_muestra_img, lang="spa")  # Intento inicial con español

        if texto_muestra.strip():
            lang = detectar_idioma_en_muestra(texto_muestra)
            print(f"  🌍 Idioma detectado: '{lang}'")
        else:
            print("  ⚠️ La primera página no contiene texto detectable. Usando 'spa'.")
            lang = "spa"

    # --- Procesamiento OCR página por página ---
    texto_completo = []
    print(f"  Realizando OCR en {num_paginas} páginas con idioma '{lang}'...")
    for i in range(1, num_paginas + 1):
        try:
            # Convierte una sola página a la vez para ahorrar RAM
            pagina_img = convert_from_path(
                pdf_path, dpi=dpi, first_page=i, last_page=i)[0]

            print(f"    📄 Procesando página {i}/{num_paginas}...")
            texto_pagina = pytesseract.image_to_string(pagina_img, lang=lang)
            texto_completo.append(texto_pagina)

        except Exception as e:
            print(
                f"    ❌ Error procesando la página {i}: {e}. Se incluirá en blanco.")
            texto_completo.append(
                f"\n\n--- ERROR AL PROCESAR ESTA PÁGINA: {e} ---\n\n")

    # --- Guardado del fichero ---
    # MODIFICADO: Se usa directamente output_path, que ya es la ruta completa.
    print(f"  ✅ Guardando resultado en: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        # Usamos un separador claro entre páginas en el Markdown
        f.write("\n\n---\n\n".join(texto_completo))


def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Realiza OCR en un fichero PDF y lo convierte a Markdown.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # MODIFICADO: Acepta un fichero en lugar de una carpeta.
    parser.add_argument("input_file", type=Path,
                        help="Ruta al fichero PDF a procesar.")
    # MODIFICADO: Argumento opcional para el nombre del fichero de salida.
    parser.add_argument(
        "-o", "--output_file", type=Path,
        help="Ruta del fichero de salida .md. \n"
             "Si no se especifica, se crea un fichero .md con el mismo nombre\n"
             "que el fichero de entrada en la misma carpeta."
    )
    parser.add_argument(
        "-l", "--lang", type=str,
        help="Código de idioma de Tesseract (ej. spa, eng, cat). \n"
             "Si no se especifica, se autodetecta."
    )
    parser.add_argument(
        "-d", "--dpi", type=int, default=300,
        help="Resolución en puntos por pulgada (DPI) para el escaneo (por defecto: 300)."
    )
    args = parser.parse_args()

    # --- Validación y configuración inicial ---
    # MODIFICADO: Se valida que el fichero de entrada exista y sea un fichero.
    if not args.input_file.is_file():
        print(f"❌ Error: El fichero de entrada no existe o no es un fichero: {args.input_file}")
        sys.exit(1)

    # AÑADIDO: Lógica para determinar la ruta de salida.
    if args.output_file:
        # Si el usuario especifica un fichero de salida, lo usamos.
        output_path = args.output_file
    else:
        # Si no, creamos el nombre por defecto junto al fichero de entrada.
        output_path = args.input_file.with_suffix(".md")

    # AÑADIDO: Asegurarse de que el directorio de salida exista.
    # Esto es útil si el usuario especifica una ruta como "nueva_carpeta/salida.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # MODIFICADO: Mensajes de inicio adaptados al nuevo funcionamiento.
    print(f"Fichero a procesar: '{args.input_file}'")
    print(f"El resultado se guardará en: '{output_path}'")

    # MODIFICADO: Se elimina el bucle y se llama a la función una sola vez.
    procesar_pdf(args.input_file, output_path, args.lang, args.dpi)

    print("\n🎉 Proceso completado.")


if __name__ == "__main__":
    main()

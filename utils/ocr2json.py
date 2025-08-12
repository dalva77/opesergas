import httpx
from pathlib import Path
import sys
import os
import logging
import json
import argparse
import asyncio

# flake8: noqa: E501


# ==============================================================================
# SCRIPT DE LIMPIEZA DE PREGUNTAS OCR CON LLM (VERSIÓN 3)
#
# NUEVAS FUNCIONALIDADES:
# - Se añade el campo `numero_original` para conservar el número tal cual aparece en el OCR.
# - Se añade el argumento `--fuente` para etiquetar el origen de las preguntas.
# - Se incluyen campos `stats` para futuro seguimiento de rendimiento.
#
# ------------------------------------------------------------------------------
# INSTRUCCIONES DE USO:
#
# 1. INSTALAR DEPENDENCIAS:
#    pip install httpx
#
# 2. CONFIGURAR VARIABLES DE ENTORNO:
#    - Para Gemini:
#      export GEMINI_API_KEY="TU_API_KEY_DE_GEMINI"
#    - Para OpenAI:
#      export OPENAI_API_KEY="TU_API_KEY_DE_OPENAI"
#
# 3. EJECUTAR EL SCRIPT:
#    python tu_script.py preguntas_sergas.txt --fuente "OPE SERGAS 2021" --provider openai
#
# ==============================================================================


# --- Configuración del Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# ... (Las funciones call_gemini_api y call_openai_api no necesitan cambios) ...


async def call_gemini_api(client: httpx.AsyncClient, prompt_text: str, max_retries: int = 5) -> str | None:
    """Hace una llamada a la API de Gemini con reintentos y backoff exponencial."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("La variable de entorno GEMINI_API_KEY no está configurada.")
        return None

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 4096,
        }
    }

    for attempt in range(max_retries):
        try:
            response = await client.post(api_url, json=payload, timeout=90.0)
            response.raise_for_status()

            result = response.json()
            if result.get("candidates"):
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                logging.warning(f"Respuesta OK de Gemini pero sin 'candidates'. Info: {response.text}")
                return None
        except httpx.HTTPStatusError as e:
            logging.error(
                f"Error de API Gemini (Intento {attempt + 1}/{max_retries}): Status {e.response.status_code}. Info: {e.response.text}")
        except httpx.RequestError as e:
            logging.error(f"Error de Red/Timeout (Intento {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logging.info(f"Reintentando en {wait_time} segundos...")
            await asyncio.sleep(wait_time)

    logging.error(f"Fallo al contactar la API de Gemini después de {max_retries} intentos.")
    return None


async def call_openai_api(client: httpx.AsyncClient, prompt_text: str, max_retries: int = 5) -> str | None:
    """Hace una llamada a la API de OpenAI con reintentos y backoff exponencial."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("La variable de entorno OPENAI_API_KEY no está configurada.")
        return None

    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    instructions, user_data = prompt_text.split("Ahora procesa el siguiente bloque:")

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": instructions.strip()},
            {"role": "user", "content": user_data.strip()}
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"}
    }

    for attempt in range(max_retries):
        try:
            response = await client.post(api_url, json=payload, headers=headers, timeout=90.0)
            response.raise_for_status()

            result = response.json()
            if result.get("choices"):
                return result["choices"][0]["message"]["content"]
            else:
                logging.warning(f"Respuesta OK de OpenAI pero sin 'choices'. Info: {response.text}")
                return None
        except httpx.HTTPStatusError as e:
            logging.error(
                f"Error de API OpenAI (Intento {attempt + 1}/{max_retries}): Status {e.response.status_code}. Info: {e.response.text}")
        except httpx.RequestError as e:
            logging.error(f"Error de Red/Timeout (Intento {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logging.info(f"Reintentando en {wait_time} segundos...")
            await asyncio.sleep(wait_time)

    logging.error(f"Fallo al contactar la API de OpenAI después de {max_retries} intentos.")
    return None

# ==============================================================================
# LÓGICA PRINCIPAL DEL SCRIPT
# ==============================================================================


def build_prompt(raw_question_block: str) -> str:
    """
    Construye el prompt detallado para enviar al LLM.
    AHORA INCLUYE INSTRUCCIONES PARA 'numero_original'.
    """
    return f"""
Actúa como un asistente experto en la limpieza y estructuración de datos para exámenes de oposición de sanidad en España. Tu tarea es corregir los errores de OCR de un bloque de texto y formatearlo en una estructura JSON precisa.

**Instrucciones Clave:**
1.  **Analiza** el bloque de texto de entrada, que representa una única pregunta de opción múltiple.
2.  **Corrige** errores ortográficos, gramaticales y de formato. Usa tu conocimiento del dominio de la sanidad para interpretar abreviaturas y términos técnicos.
3.  **Extrae la siguiente información**:
    - `numero`: El número de la pregunta como un entero (integer).
    - `numero_original`: El texto del número tal como aparece en el original (ej. "102.", "Pregunta: 99").
    - `enunciado`: El texto completo de la pregunta.
    - `opciones`: Un objeto con las claves "A", "B", "C", y "D".
4.  **Reconstruye** las opciones A, B, C y D, asegurando que cada una tenga su letra correcta, incluso si en el original faltan o están mal.
5.  **Genera** una salida EXCLUSIVAMENTE en formato JSON válido. No añadas explicaciones ni la palabra "json" antes o después del código.
6.  **No inventes** información. Si algo es ilegible, márcalo como `[ILEGIBLE]`.
7.  **Incluye** el texto original sin modificar en el campo `raw_ocr`.

**Ejemplo de la Tarea:**

---
**INPUT (Texto en bruto):**
```
102. Se le programa una cita a un paciente con varios estudios en el mismo dia. ¿En qué orden se realizarían?
A)Rx simple de abdomen. esofagoygastroduodenal, urografia inlrivenosa.
B) Urografía intravenosa, rx simple de abdomen, esofacocastroduouenal.
C¡Rx simple de abdomen, urografía intravenosa, esofagogastroduodenal,

D;) Ninguna de lis respuestas anteriores es correcta,
```

**OUTPUT (JSON Estricto):**
```json
{{
  "numero": 102,
  "numero_original": "102.",
  "enunciado": "Se le programa una cita a un paciente con varios estudios en el mismo día. ¿En qué orden se realizarían?",
  "opciones": {{
    "A": "Rx simple de abdomen, esofagogastroduodenal, urografía intravenosa.",
    "B": "Urografía intravenosa, rx simple de abdomen, esofagogastroduodenal.",
    "C": "Rx simple de abdomen, urografía intravenosa, esofagogastroduodenal.",
    "D": "Ninguna de las respuestas anteriores es correcta."
  }},
  "raw_ocr": "102. Se le programa una cita a un paciente con varios estudios en el mismo dia. ¿En qué orden se realizarían?\\nA)Rx simple de abdomen. esofagoygastroduodenal, urografia inlrivenosa.\\nB) Urografía intravenosa, rx simple de abdomen, esofacocastroduouenal.\\nC¡Rx simple de abdomen, urografía intravenosa, esofagogastroduodenal,\\n\\nD;) Ninguna de lis respuestas anteriores es correcta,"
}}
```
---

Ahora procesa el siguiente bloque:

**INPUT:**
```
{raw_question_block}
```
"""


async def process_block(sem: asyncio.Semaphore, client: httpx.AsyncClient, block: str, provider: str) -> str | None:
    """Función wrapper para procesar un bloque con control de concurrencia."""
    async with sem:
        prompt = build_prompt(block)
        if provider == 'gemini':
            return await call_gemini_api(client, prompt)
        elif provider == 'openai':
            return await call_openai_api(client, prompt)
        return None


async def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Limpia y estructura preguntas de un fichero OCR usando una API de LLM.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_file", type=Path, help="Fichero de texto con las preguntas OCR en bruto.")
    # <-- MODIFICADO: Argumento 'fuente' para identificar el origen. Es requerido.
    parser.add_argument("--fuente", type=str, required=True,
                        help="Identificador y fuente del examen (ej. 'OPE SERGAS 2021').")
    parser.add_argument("--provider", type=str, choices=['gemini',
                        'openai'], required=True, help="Proveedor de LLM a utilizar.")
    parser.add_argument("-o", "--output_file", type=Path,
                        help="Fichero JSON de salida. Por defecto: [input_file_name].json")
    parser.add_argument("-s", "--separator", type=str, default="---",
                        help="Cadena separadora entre preguntas (por defecto: '---').")
    parser.add_argument("-c", "--concurrency", type=int, default=10,
                        help="Número de peticiones concurrentes a la API (por defecto: 10).")

    args = parser.parse_args()

    if not args.output_file:
        args.output_file = args.input_file.with_suffix(".json")

    # --- Lectura y preparación de datos ---
    try:
        raw_text = args.input_file.read_text(encoding="utf-8")
        question_blocks = [block.strip() for block in raw_text.split(args.separator) if block.strip()]
        if not question_blocks:
            logging.warning(
                f"No se encontraron bloques de preguntas en '{args.input_file}' usando el separador '{args.separator}'.")
            sys.exit(0)
    except FileNotFoundError:
        logging.error(f"El fichero de entrada no existe: {args.input_file}")
        sys.exit(1)

    logging.info(
        f"📄 Encontrados {len(question_blocks)} bloques de preguntas para procesar de la fuente '{args.fuente}'.")

    # --- Bucle de procesamiento CONCURRENTE ---
    processed_questions = []
    semaphore = asyncio.Semaphore(args.concurrency)

    async with httpx.AsyncClient() as client:
        tasks = [process_block(semaphore, client, block, args.provider) for block in question_blocks]
        logging.info(
            f"⚙️  Enviando {len(tasks)} preguntas a la API '{args.provider}' con una concurrencia de {args.concurrency}...")
        api_responses = await asyncio.gather(*tasks, return_exceptions=True)

    logging.info("✅ Todas las respuestas de la API han sido recibidas. Procediendo a parsear.")

    # --- Parseo y validación de las respuestas (VERSIÓN A PRUEBA DE PYLANCE) ---
    for i, response in enumerate(api_responses):
        # Usamos una "Type Guard". Solo si 'response' es un string, entramos al bloque.
        if isinstance(response, str) and response:  # Comprobamos que es string y no está vacío
            try:
                # DENTRO DE ESTE BLOQUE, PYLANCE SABE AL 100% QUE 'response' ES UN 'str'.
                # La queja desaparecerá.
                clean_json_str = response.strip().removeprefix("```json").removesuffix("```").strip()

                if not clean_json_str:
                    logging.warning(f"La respuesta para el bloque {i + 1} estaba vacía después de limpiar. Saltando.")
                    continue

                data = json.loads(clean_json_str)

                # Añadimos los metadatos
                data["fuente"] = args.fuente
                data["respuesta_correcta"] = None
                data["tags"] = []
                data["stats"] = {
                    "veces_preguntada": 0,
                    "veces_acertada": 0,
                    "veces_fallada": 0
                }

                processed_questions.append(data)
                logging.info(f"👍 Pregunta {data.get('numero', 'N/A')} (Bloque {i + 1}) procesada y estructurada.")

            except json.JSONDecodeError:
                logging.error(f"La respuesta para el bloque {i + 1} no es un JSON válido.")
                logging.debug(f"Respuesta recibida (bloque {i + 1}):\n{response}")
            except Exception as e:
                logging.error(f"Error inesperado al procesar la respuesta del bloque {i + 1}: {e}")

        else:
            # Si no es un string, es un error (Excepción) o una respuesta vacía (None).
            # Lo manejamos aquí fuera.
            if isinstance(response, Exception):
                logging.error(f"Error en la tarea para el bloque {i + 1}: {response}")
            else:
                # Esto cubre el caso de 'None' o un string vacío inicial.
                logging.warning(f"Respuesta inválida o vacía para el bloque {i + 1}. Saltando.")

    # --- Guardado del resultado final ---
    if not processed_questions:
        logging.warning("No se procesó ninguna pregunta con éxito. No se generará fichero de salida.")
        sys.exit(0)

    try:
        # Ordenamos las preguntas por su número antes de guardarlas
        processed_questions.sort(key=lambda q: q.get('numero', 0))
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(processed_questions, f, ensure_ascii=False, indent=2)
        logging.info(f"\n🎉 ¡Proceso completado! {len(processed_questions)} preguntas guardadas en: {args.output_file}")
    except Exception as e:
        logging.error(f"Error al guardar el fichero de salida: {e}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Análisis Big Five (OCEAN) de perfiles de TikTok usando la API de Groq.

Uso:
    python analisis_bigfive.py                       # pregunta el usuario
    python analisis_bigfive.py danielvalencia365     # por nombre de usuario
    python analisis_bigfive.py datos_ana.json        # por archivo
    python analisis_bigfive.py usuario1 usuario2     # varios a la vez
    python analisis_bigfive.py --todos               # todos los datos_*.json de la carpeta
    python analisis_bigfive.py --listar-modelos      # muestra los modelos disponibles en tu cuenta

Configuración (variables de entorno o archivo .env):
    GROQ_API_KEY   -> tu clave de Groq (obligatoria)
    GROQ_MODEL     -> modelo a usar (opcional)
"""
import argparse
import glob
import json
import os
import re

import requests

# Si está instalado python-dotenv, carga automáticamente el archivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO_POR_DEFECTO = "qwen/qwen3.8-27b"  # el que funciona en tu cuenta
RASGOS = ["Apertura", "Responsabilidad", "Extraversion", "Amabilidad", "Neuroticismo"]
SIN_DESCRIPCION = "Sin descripción disponible"
MAX_CARACTERES = 6000  # límite de texto enviado a la IA
CATEGORIAS_MARCA = [
    "Moda y accesorios", "Belleza y cuidado personal", "Tecnología y gadgets",
    "Deportes y fitness", "Alimentos y bebidas", "Viajes y turismo",
    "Educación y cursos", "Entretenimiento y gaming", "Hogar y decoración",
    "Finanzas y emprendimiento", "Salud y bienestar", "Mascotas", "Automotriz",
]


def obtener_api_key():
    """Lee la API key desde la variable de entorno GROQ_API_KEY."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit(
            "Error: no se encontró la variable de entorno GROQ_API_KEY.\n"
            "  Windows (CMD):  set GROQ_API_KEY=tu_clave\n"
            "  Mac / Linux:    export GROQ_API_KEY=\"tu_clave\"\n"
            "  O crea un archivo .env con: GROQ_API_KEY=tu_clave"
        )
    return api_key


def listar_modelos(api_key):
    """Muestra los modelos a los que tiene acceso tu cuenta de Groq."""
    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        r.raise_for_status()
        print("Modelos disponibles en tu cuenta:")
        for m in sorted(x["id"] for x in r.json().get("data", [])):
            print(f"  - {m}")
    except requests.RequestException as e:
        print(f"No se pudo obtener la lista de modelos: {e}")


def resolver_archivo(entrada):
    """Acepta 'usuario', '@usuario' o 'datos_usuario.json' y devuelve el nombre del archivo."""
    entrada = entrada.strip().lstrip("@")
    if entrada.lower().endswith(".json"):
        return entrada
    return f"datos_{entrada}.json"


def extraer_json(texto):
    """Obtiene el objeto JSON de la respuesta, ignorando bloques <think> y markdown."""
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL)
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fin == -1:
        raise ValueError("La respuesta de la IA no contiene un JSON.")
    return json.loads(texto[inicio:fin + 1])


def normalizar_a_100(puntajes):
    """Reparte los puntajes para que sumen exactamente 100 (método del mayor resto)."""
    total = sum(puntajes.values())
    if total == 0:
        return {k: 100 // len(puntajes) for k in puntajes}
    exactos = {k: v * 100 / total for k, v in puntajes.items()}
    enteros = {k: int(v) for k, v in exactos.items()}
    faltan = 100 - sum(enteros.values())
    # Los puntos que sobran van a los rasgos con mayor parte decimal
    for k in sorted(exactos, key=lambda k: exactos[k] - enteros[k], reverse=True)[:faltan]:
        enteros[k] += 1
    return enteros


def validar_resultado(resultado):
    """Valida la respuesta de la IA. Devuelve (bigfive, perfil_comercial)."""
    brutos = {r: max(0.0, min(100.0, float(resultado[r]))) for r in RASGOS}
    bigfive = normalizar_a_100(brutos)  # suman exactamente 100
    bigfive["resumen"] = str(resultado.get("resumen", "")).strip()

    afines = []
    for item in resultado.get("afinidad_marcas", []):
        if isinstance(item, dict) and item.get("categoria") in CATEGORIAS_MARCA:
            afines.append({
                "categoria": item["categoria"],
                "motivo": str(item.get("motivo", "")).strip(),
            })

    intereses = resultado.get("intereses", [])
    if not isinstance(intereses, list):
        intereses = []

    comercial = {
        "tono_comunicacion": str(resultado.get("tono_comunicacion", "")).strip(),
        "intereses": [str(i).strip() for i in intereses if str(i).strip()][:5],
        "afinidad_marcas": afines[:3],
    }
    return bigfive, comercial


def analizar_perfil(archivo_json, api_key=None, modelo=None):
    """Analiza un archivo JSON de perfil y guarda 'analisis_bigfive' dentro de él.
    Devuelve True si el análisis fue exitoso."""
    api_key = api_key or obtener_api_key()
    modelo = modelo or os.getenv("GROQ_MODEL", MODELO_POR_DEFECTO)

    print(f"\nLeyendo datos de {archivo_json}...")
    try:
        with open(archivo_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo {archivo_json}.")
        return False
    except json.JSONDecodeError:
        print(f"Error: {archivo_json} no es un JSON válido.")
        return False

    descripciones = [
        v.get("descripcion", "").strip()
        for v in datos.get("videos_recientes", [])
    ]
    descripciones = [d for d in descripciones if d and d != SIN_DESCRIPCION]
    if not descripciones:
        print("Error: el perfil no tiene descripciones de videos para analizar.")
        return False

    textos = " ".join(descripciones)[:MAX_CARACTERES]

    prompt = f"""
    Actúa como un analista de marketing con conocimientos de psicología computacional.
    Analiza el siguiente texto extraído de los últimos videos de una cuenta de TikTok (descripciones y hashtags).
    Tu objetivo es estimar su personalidad con el modelo Big Five (O.C.E.A.N.) y determinar con qué tipo de
    productos o servicios podría estar alineada, para ayudar a una marca a decidir si colabora con esta persona.

    Devuelve ÚNICAMENTE un objeto JSON válido con exactamente 9 claves:
    1. "Apertura" (número entero 0-100)
    2. "Responsabilidad" (número entero 0-100)
    3. "Extraversion" (número entero 0-100)
    4. "Amabilidad" (número entero 0-100)
    5. "Neuroticismo" (número entero 0-100)
    6. "resumen" (un párrafo de máximo 3 líneas describiendo la personalidad general y el estilo de esta persona).
    7. "tono_comunicacion" (máximo 8 palabras, por ejemplo: cercano, humorístico y espontáneo).
    8. "intereses" (lista de 3 a 5 temas principales que aparecen en su contenido).
    9. "afinidad_marcas" (lista de exactamente 3 objetos, ordenados de mayor a menor afinidad; cada objeto tiene
       la clave "categoria" y la clave "motivo", una frase corta que explique la afinidad basándose en el texto).
       El valor de "categoria" debe ser exactamente una de estas opciones: {", ".join(CATEGORIAS_MARCA)}.


    Texto a analizar: {textos}
    """

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": "You output only valid JSON without markdown formatting."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

    print(f"Enviando datos a Groq (modelo: {modelo})...")
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    except requests.RequestException as e:
        print(f"Error de conexión con la API: {e}")
        return False

    if response.status_code != 200:
        print(f"Error en la API. Código: {response.status_code}\n{response.text}")
        return False

    try:
        contenido = response.json()["choices"][0]["message"]["content"]
        bigfive, comercial = validar_resultado(extraer_json(contenido))
    except (KeyError, IndexError, TypeError, ValueError) as e:
        print(f"Error procesando la respuesta de la IA: {e}")
        return False

    datos["analisis_bigfive"] = bigfive
    datos["perfil_comercial"] = comercial
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    print("¡Análisis completado exitosamente!")
    print(json.dumps({"analisis_bigfive": bigfive, "perfil_comercial": comercial}, indent=4, ensure_ascii=False))
    return True


def main():
    parser = argparse.ArgumentParser(description="Análisis Big Five de perfiles de TikTok.")
    parser.add_argument("perfiles", nargs="*", help="Usuarios o archivos .json a analizar")
    parser.add_argument("--todos", action="store_true", help="Analiza todos los datos_*.json de la carpeta")
    parser.add_argument("--modelo", help="Modelo de Groq a utilizar")
    parser.add_argument("--listar-modelos", action="store_true", help="Muestra los modelos disponibles y sale")
    args = parser.parse_args()

    if args.listar_modelos:
        listar_modelos(obtener_api_key())
        return

    if args.todos:
        archivos = sorted(glob.glob("datos_*.json"))
    elif args.perfiles:
        archivos = [resolver_archivo(p) for p in args.perfiles]
    else:
        usuario = input("Usuario de TikTok o archivo .json a analizar: ")
        archivos = [resolver_archivo(usuario)]

    if not archivos:
        print("No se encontraron archivos datos_*.json para analizar.")
        return

    api_key = obtener_api_key()
    exitosos = sum(analizar_perfil(a, api_key, args.modelo) for a in archivos)
    print(f"\nResumen: {exitosos} de {len(archivos)} perfiles analizados correctamente.")


if __name__ == "__main__":
    main()
import json
import requests

def analizar_perfil(archivo_json):
    api_key = "TU_API_KEY_GROQ_AQUI"
    
    modelo_elegido = "qwen/qwen3.8-27b"
    print(f"Usando el modelo confirmado: {modelo_elegido}")
    
    print(f"Leyendo datos de {archivo_json}...")
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_json}.")
        return

    textos = " ".join([video.get("descripcion", "") for video in datos.get("videos_recientes", [])])
    
    prompt = f"""
    Actúa como un psicólogo computacional. Analiza el siguiente texto extraído de TikTok basándote en el modelo Big Five (O.C.E.A.N.).
    Devuelve ÚNICAMENTE un objeto JSON válido con exactamente 6 claves:
    1. "Apertura" (número entero 0-100)
    2. "Responsabilidad" (número entero 0-100)
    3. "Extraversion" (número entero 0-100)
    4. "Amabilidad" (número entero 0-100)
    5. "Neuroticismo" (número entero 0-100)
    6. "resumen" (un párrafo de máximo 3 líneas describiendo el tipo de personalidad general de esta persona).
    Cero texto adicional, solo el JSON estructurado.
    
    Texto a analizar: {textos}
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": modelo_elegido,
        "messages": [
            {"role": "system", "content": "You output only valid JSON without markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    print("Enviando datos a la API de Groq para análisis Big Five...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            resultado = response.json()
            texto_respuesta = resultado['choices'][0]['message']['content']
            
            texto_limpio = texto_respuesta.strip().removeprefix("```json").removesuffix("```").strip()
            resultado_json = json.loads(texto_limpio)
            
            datos["analisis_bigfive"] = resultado_json
            
            with open(archivo_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
                
            print("\n¡Análisis completado exitosamente!")
            print(json.dumps(resultado_json, indent=4, ensure_ascii=False))
            
        else:
            print(f"\nError en la API. Código: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error parseando el resultado: {e}\nRevisa que el texto extraído no esté vacío.")

if __name__ == "__main__":
    analizar_perfil("datos_danielvalencia365.json")
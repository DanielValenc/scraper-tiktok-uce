# Importamos la librería json para guardar los datos en formato JSON
import json
# Importamos time para hacer pausas y evitar bloqueos por parte de TikTok
import time
# Importamos sync_playwright, nuestra herramienta para automatizar el navegador
from playwright.sync_api import sync_playwright

def scrape_tiktok_profile(username):
    print(f"\nIniciando extracción para: @{username}")
    
    # 1. Estructura de Datos
    # Diccionario que almacenará toda la información estructurada que luego irá al JSON
    datos_descarga = {
        "usuario": username,
        "perfil": {},
        "videos_recientes": []
    }
    
    # Iniciamos el controlador del navegador
    with sync_playwright() as p:
        # 2. Configuración del Navegador (Persistencia de Sesión)
        # Usamos una carpeta local (perfil_tiktok) para guardar cookies y sesión, 
        # esto ayuda a evadir Captchas repetitivos.
        context = p.chromium.launch_persistent_context(
            user_data_dir="perfil_tiktok",
            headless=False, # Mantenemos el navegador visible para evitar detección de bots
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0]
        
        try:
            # 3. Navegación al Perfil
            # Navegamos a la URL y esperamos a que el contenido principal cargue
            page.goto(f"https://www.tiktok.com/@{username}", wait_until="domcontentloaded", timeout=60000)
            
            print("Verificando conexión...")
            time.sleep(4) 
            
            # 4. Extracción de Estadísticas
            print("Extrayendo estadísticas principales y foto de perfil...")
            # Esperamos hasta 60s por si aparece un Captcha inicial
            page.wait_for_selector('strong[title="Seguidores"]', timeout=60000)
            
            # Extraemos siguiendo, seguidores y likes usando selectores estables
            siguiendo = page.locator('strong[title="Siguiendo"]').text_content()
            seguidores = page.locator('strong[title="Seguidores"]').text_content()
            likes = page.locator('strong[title="Me gusta"]').text_content()
            
            # 5. Extracción de la Foto de Perfil
            try:
                # Buscamos la imagen asociada a la clase universal "Avatar" de TikTok
                foto_perfil = page.locator('img[class*="Avatar"]').first.get_attribute('src', timeout=5000)
            except:
                # Imagen de fallback si falla el selector
                foto_perfil = "https://via.placeholder.com/150?text=Sin+Foto"
            
            # Guardamos los metadatos del perfil
            datos_descarga["perfil"] = {
                "foto_perfil": foto_perfil,
                "siguiendo": siguiendo,
                "seguidores": seguidores,
                "me_gusta": likes
            }
            
            # 6. Scroll Simulado (Bypass de Lazy Loading)
            print("Haciendo scroll simulado para cargar las publicaciones...")
            # Simulamos el giro de la rueda del mouse para forzar la carga de los videos inferiores
            for _ in range(4):
                page.mouse.wheel(0, 800)
                time.sleep(1.5)
            
            # 7. Extracción de Videos
            print("Capturando los enlaces y descripciones de los videos...")
            page.wait_for_selector('a[href*="/video/"]', timeout=60000)
            videos_links = page.locator('a[href*="/video/"]')
            
            # Diccionario temporal para filtrar videos duplicados y almacenar sus datos
            videos_extraidos = {}
            cantidad = videos_links.count()
            
            for i in range(cantidad):
                elemento = videos_links.nth(i)
                href = elemento.get_attribute('href') 
                
                # Validamos que el enlace pertenezca a un video
                if href and "/video/" in href:
                    if href.startswith("/"):
                        href = "https://www.tiktok.com" + href
                    
                    if href not in videos_extraidos:
                        try:
                            # NUEVO: Extraemos la miniatura y el texto alternativo (descripción y hashtags)
                            img_locator = elemento.locator('img').first
                            miniatura = img_locator.get_attribute('src', timeout=2000)
                            descripcion = img_locator.get_attribute('alt', timeout=2000)
                        except:
                            miniatura = "https://via.placeholder.com/300x400?text=Video"
                            descripcion = "Sin descripción disponible"
                            
                        videos_extraidos[href] = {
                            "miniatura": miniatura,
                            "descripcion": descripcion if descripcion else "Sin descripción disponible"
                        }
            
            # 8. Limitación y Formateo
            # Cortamos la lista a los últimos 10 videos extraídos
            lista_final = list(videos_extraidos.items())[:10]
            
            # Añadimos la información al diccionario principal
            for i, (enlace, datos_video) in enumerate(lista_final):
                datos_descarga["videos_recientes"].append({
                    "posicion": i + 1,
                    "enlace": enlace,
                    "miniatura": datos_video["miniatura"],
                    "descripcion": datos_video["descripcion"], # Nuevo campo para análisis Big Five (NLP)
                    "estado": "Extraído exitosamente"
                })
                
            # 9. Exportación de Datos
            nombre_archivo = f"datos_{username}.json"
            # Guardamos el JSON asegurando codificación UTF-8 para emojis y tildes
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(datos_descarga, f, ensure_ascii=False, indent=4)
                
            print(f"\n¡ÉXITO! Se extrajeron {len(lista_final)} videos con descripciones para el análisis. Revisa el archivo: {nombre_archivo}")
            
        except Exception as e:
            # 10. Manejo de Errores de Conexión y Seguridad
            print(f"\nError: TikTok bloqueó la conexión o saltó un Captcha. Borra la carpeta 'perfil_tiktok', espera unos minutos y reintenta.")
            print(f"Detalle técnico: {e}")
            
        finally:
            # Cerramos el contexto para liberar memoria
            context.close()

if __name__ == "__main__":
    target_user = input("Ingresa el username de TikTok (sin el @): ")
    scrape_tiktok_profile(target_user)
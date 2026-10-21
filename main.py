# Importamos la librería json para poder guardar nuestros datos extraídos en un archivo .json
import json
# Importamos time para hacer pequeñas pausas y simular que somos un usuario humano leyendo la página
import time
# Importamos sync_playwright que es nuestro "motor" para abrir y controlar el navegador web de forma automática
from playwright.sync_api import sync_playwright

def scrape_tiktok_profile(username):
    print(f"\nIniciando extracción para: @{username}")
    
    # 1. Estructura de Datos
    # Creamos un diccionario vacío que servirá como "molde" para organizar la información
    # que vamos a extraer. Al final, este diccionario se convertirá en nuestro archivo JSON.
    datos_descarga = {
        "usuario": username,
        "perfil": {},
        "videos_recientes": []
    }
    
    # Iniciamos Playwright (el controlador del navegador)
    with sync_playwright() as p:
        # 2. Configuración del Navegador (El Pase VIP)
        # launch_persistent_context crea una carpeta "perfil_tiktok" donde guarda las cookies y sesión.
        # Esto evita que TikTok nos pida resolver el Captcha cada vez que ejecutamos el código.
        # headless=False hace que el navegador sea visible.
        context = p.chromium.launch_persistent_context(
            user_data_dir="perfil_tiktok",
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Tomamos la primera pestaña que se abre en el navegador
        page = context.pages[0]
        
        try:
            # 3. Navegación
            # Le decimos al navegador que vaya al perfil de TikTok del usuario ingresado.
            # wait_until="domcontentloaded" le dice que no espere a que carguen los anuncios, solo el código principal.
            page.goto(f"https://www.tiktok.com/@{username}", wait_until="domcontentloaded", timeout=60000)
            
            print("Verificando conexión...")
            time.sleep(4) # Pausa de 4 segundos para dejar que la página "respire" y cargue
            
            # 4. Extracción de Estadísticas Principales
            print("Extrayendo estadísticas principales y foto de perfil...")
            # Esperamos pacientemente (hasta 60 seg) a que aparezca la palabra "Seguidores" en pantalla
            page.wait_for_selector('strong[title="Seguidores"]', timeout=60000)
            
            # Buscamos los textos exactos de las estadísticas usando sus etiquetas HTML 'title'
            siguiendo = page.locator('strong[title="Siguiendo"]').text_content()
            seguidores = page.locator('strong[title="Seguidores"]').text_content()
            likes = page.locator('strong[title="Me gusta"]').text_content()
            
            # 5. Extracción de la Foto de Perfil
            try:
                # Buscamos la imagen que tenga la clase "Avatar" (que es la que usa TikTok para la foto circular)
                # y extraemos su atributo 'src' (el enlace real de la imagen).
                foto_perfil = page.locator('img[class*="Avatar"]').first.get_attribute('src', timeout=5000)
            except:
                # Si el usuario no tiene foto o el diseño cambió, ponemos una imagen gris de repuesto
                foto_perfil = "https://via.placeholder.com/150?text=Sin+Foto"
            
            # Guardamos todos estos datos del perfil en nuestro diccionario principal
            datos_descarga["perfil"] = {
                "foto_perfil": foto_perfil,
                "siguiendo": siguiendo,
                "seguidores": seguidores,
                "me_gusta": likes
            }
            
            # 6. Scroll Simulado (Lazy Loading)
            print("Haciendo scroll simulado para cargar las publicaciones...")
            # Simulamos 4 giros de la rueda del ratón hacia abajo. 
            # Esto es vital porque TikTok no carga los videos hasta que el usuario baja la pantalla.
            for _ in range(4):
                page.mouse.wheel(0, 800)
                time.sleep(1.5)
            
            # 7. Extracción de Videos
            print("Capturando los enlaces y miniaturas de los videos...")
            # Esperamos a que aparezcan los enlaces de las publicaciones
            page.wait_for_selector('a[href*="/video/"]', timeout=60000)
            videos_links = page.locator('a[href*="/video/"]')
            
            # Usamos un diccionario temporal para guardar los videos.
            # Esto sirve como filtro automático para no guardar enlaces duplicados.
            videos_extraidos = {}
            cantidad = videos_links.count()
            
            # Recorremos todos los elementos de video que encontramos en la pantalla
            for i in range(cantidad):
                elemento = videos_links.nth(i)
                href = elemento.get_attribute('href') # Extraemos el enlace del video
                
                # Verificamos que sea un enlace válido de video
                if href and "/video/" in href:
                    # Si el enlace está incompleto (ej. /@user/video/123), le pegamos el dominio completo
                    if href.startswith("/"):
                        href = "https://www.tiktok.com" + href
                    
                    # Si este video es nuevo (no lo hemos guardado antes), extraemos su imagen de miniatura
                    if href not in videos_extraidos:
                        try:
                            # Buscamos la etiqueta 'img' dentro de la tarjeta del video para sacar la portada
                            miniatura = elemento.locator('img').first.get_attribute('src', timeout=2000)
                        except:
                            miniatura = "https://via.placeholder.com/300x400?text=Video"
                            
                        # Guardamos el enlace y su miniatura en el filtro temporal
                        videos_extraidos[href] = miniatura
            
            # 8. Límite y Guardado Final
            # Convertimos nuestro diccionario filtrado en una lista y cortamos solo los primeros 10 elementos
            lista_final = list(videos_extraidos.items())[:10]
            
            # Recorremos esos 10 videos finales y los metemos al diccionario maestro de descarga
            for i, (enlace, miniatura) in enumerate(lista_final):
                datos_descarga["videos_recientes"].append({
                    "posicion": i + 1,
                    "enlace": enlace,
                    "miniatura": miniatura,
                    "estado": "Extraído exitosamente"
                })
                
            # 9. Exportación a JSON
            # Nombramos el archivo dinámicamente según el usuario que buscamos
            nombre_archivo = f"datos_{username}.json"
            # Abrimos el archivo en modo escritura ("w") asegurando que soporte tildes y caracteres latinos (utf-8)
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                # Volcamos todo nuestro diccionario 'datos_descarga' dentro del archivo con una indentación bonita de 4 espacios
                json.dump(datos_descarga, f, ensure_ascii=False, indent=4)
                
            print(f"\n¡ÉXITO! Se extrajeron {len(lista_final)} videos con sus miniaturas. Revisa el archivo: {nombre_archivo}")
            
        except Exception as e:
            # 10. Manejo de Errores
            # Si el internet falla, o TikTok lanza un Captcha que no se resuelve a tiempo, el programa cae aquí
            # en lugar de romperse violentamente.
            print(f"\nError: TikTok bloqueó la conexión o saltó un Captcha. Borra la carpeta 'perfil_tiktok', espera unos minutos y reintenta.")
            print(f"Detalle técnico: {e}")
            
        finally:
            # Pase lo que pase (éxito o error), nos aseguramos de cerrar el navegador para liberar la memoria de la computadora
            context.close()

# Este es el punto de inicio del programa. 
# Si ejecutamos el archivo directamente en la terminal, nos pedirá ingresar el usuario.
if __name__ == "__main__":
    target_user = input("Ingresa el username de TikTok (sin el @): ")
    scrape_tiktok_profile(target_user)
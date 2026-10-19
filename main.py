import json
import time
from playwright.sync_api import sync_playwright

def scrape_tiktok_profile(username):
    print(f"\nIniciando extracción para: @{username}")
    
    datos_descarga = {
        "usuario": username,
        "perfil": {},
        "videos_recientes": []
    }
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="perfil_tiktok",
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0]
        
        try:
            # wait_until="domcontentloaded" evita que Playwright espere eternamente si algún anuncio de TikTok no carga
            page.goto(f"https://www.tiktok.com/@{username}", wait_until="domcontentloaded", timeout=60000)
            
            print("Verificando conexión...")
            time.sleep(4) 
            
            print("Extrayendo estadísticas principales...")
            page.wait_for_selector('strong[title="Seguidores"]', timeout=60000)
            
            siguiendo = page.locator('strong[title="Siguiendo"]').text_content()
            seguidores = page.locator('strong[title="Seguidores"]').text_content()
            likes = page.locator('strong[title="Me gusta"]').text_content()
            
            datos_descarga["perfil"] = {
                "siguiendo": siguiendo,
                "seguidores": seguidores,
                "me_gusta": likes
            }
            
            print("Haciendo scroll simulado para cargar las publicaciones...")
            for _ in range(4):
                page.mouse.wheel(0, 800)
                time.sleep(1.5)
            
            print("Capturando los enlaces de los videos...")
            page.wait_for_selector('a[href*="/video/"]', timeout=60000)
            videos_links = page.locator('a[href*="/video/"]')
            
            enlaces_unicos = set()
            cantidad = videos_links.count()
            
            for i in range(cantidad):
                href = videos_links.nth(i).get_attribute('href')
                if href and "/video/" in href:
                    if href.startswith("/"):
                        href = "https://www.tiktok.com" + href
                    enlaces_unicos.add(href)
            
            lista_final = list(enlaces_unicos)[:10]
            
            for i, enlace in enumerate(lista_final):
                datos_descarga["videos_recientes"].append({
                    "posicion": i + 1,
                    "enlace": enlace,
                    "estado": "Extraído exitosamente"
                })
                
            nombre_archivo = f"datos_{username}.json"
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(datos_descarga, f, ensure_ascii=False, indent=4)
                
            print(f"\n¡ÉXITO! Se extrajeron {len(lista_final)} videos. Revisa el archivo: {nombre_archivo}")
            
        except Exception as e:
            print(f"\nError: TikTok bloqueó la conexión o saltó un Captcha. Borra la carpeta 'perfil_tiktok', espera unos minutos y reintenta.")
            print(f"Detalle técnico: {e}")
            
        finally:
            context.close()

if __name__ == "__main__":
    target_user = input("Ingresa el username de TikTok (sin el @): ")
    scrape_tiktok_profile(target_user)
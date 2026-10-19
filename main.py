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
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state="state.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(f"https://www.tiktok.com/@{username}")
        
        try:
            print("Extrayendo estadísticas principales...")
            page.wait_for_selector('strong[title="Seguidores"]', timeout=15000)
            
            siguiendo = page.locator('strong[title="Siguiendo"]').text_content()
            seguidores = page.locator('strong[title="Seguidores"]').text_content()
            likes = page.locator('strong[title="Me gusta"]').text_content()
            
            datos_descarga["perfil"] = {
                "siguiendo": siguiendo,
                "seguidores": seguidores,
                "me_gusta": likes
            }
            
            print("Haciendo scroll simulado para cargar las publicaciones...")
            # Simulamos giros en la rueda del ratón en lugar de saltos bruscos de JavaScript
            for _ in range(4):
                page.mouse.wheel(0, 800)
                time.sleep(1.5)
            
            print("Capturando los enlaces de los videos...")
            # Buscamos cualquier enlace en la web que contenga "/video/"
            page.wait_for_selector('a[href*="/video/"]', timeout=15000)
            videos_links = page.locator('a[href*="/video/"]')
            
            enlaces_unicos = set()
            cantidad = videos_links.count()
            
            # Limpiamos duplicados (TikTok pone 2 enlaces por cada video en el DOM) y completamos la URL
            for i in range(cantidad):
                href = videos_links.nth(i).get_attribute('href')
                if href and "/video/" in href:
                    if href.startswith("/"):
                        href = "https://www.tiktok.com" + href
                    enlaces_unicos.add(href)
            
            # Seleccionamos hasta un máximo de 10 videos
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
            print(f"\nError durante la extracción. Detalle técnico: {e}")
        
        browser.close()

if __name__ == "__main__":
    target_user = input("Ingresa el username de TikTok (sin el @): ")
    scrape_tiktok_profile(target_user)
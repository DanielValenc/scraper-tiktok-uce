"""
Extracción de datos de un perfil de TikTok y análisis Big Five.

Uso:
    python main.py                      # pregunta el usuario
    python main.py danielvalencia365    # usuario por argumento
    python main.py usuario --sin-analisis   # solo extrae, no analiza
"""
import argparse
import json
import time

from playwright.sync_api import sync_playwright

PLACEHOLDER_FOTO = "https://via.placeholder.com/150?text=Sin+Foto"
PLACEHOLDER_VIDEO = "https://via.placeholder.com/300x400?text=Video"
SIN_DESCRIPCION = "Sin descripción disponible"
MAX_VIDEOS = 10


def scrape_tiktok_profile(username):
    """Extrae el perfil y guarda datos_<usuario>.json. Devuelve el nombre del archivo o None si falla."""
    print(f"\nIniciando extracción para: @{username}")

    datos_descarga = {"usuario": username, "perfil": {}, "videos_recientes": []}
    nombre_archivo = None

    with sync_playwright() as p:
        # Carpeta local que guarda cookies/sesión para reducir Captchas
        context = p.chromium.launch_persistent_context(
            user_data_dir="perfil_tiktok",
            headless=False,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.pages[0]

        try:
            page.goto(f"https://www.tiktok.com/@{username}", wait_until="domcontentloaded", timeout=60000)
            print("Verificando conexión...")
            time.sleep(4)

            print("Extrayendo estadísticas principales y foto de perfil...")
            # Espera hasta 60 s por si aparece un Captcha inicial
            page.wait_for_selector('strong[title="Seguidores"]', timeout=60000)

            siguiendo = page.locator('strong[title="Siguiendo"]').text_content()
            seguidores = page.locator('strong[title="Seguidores"]').text_content()
            likes = page.locator('strong[title="Me gusta"]').text_content()

            try:
                foto_perfil = page.locator('img[class*="Avatar"]').first.get_attribute("src", timeout=5000)
            except Exception:
                foto_perfil = PLACEHOLDER_FOTO

            datos_descarga["perfil"] = {
                "foto_perfil": foto_perfil,
                "siguiendo": siguiendo,
                "seguidores": seguidores,
                "me_gusta": likes,
            }

            print("Haciendo scroll simulado para cargar las publicaciones...")
            for _ in range(4):
                page.mouse.wheel(0, 800)
                time.sleep(1.5)

            print("Capturando los enlaces y descripciones de los videos...")
            page.wait_for_selector('a[href*="/video/"]', timeout=60000)
            videos_links = page.locator('a[href*="/video/"]')

            videos_extraidos = {}  # evita duplicados
            for i in range(videos_links.count()):
                elemento = videos_links.nth(i)
                href = elemento.get_attribute("href")
                if not href or "/video/" not in href:
                    continue
                if href.startswith("/"):
                    href = "https://www.tiktok.com" + href
                if href in videos_extraidos:
                    continue

                try:
                    img = elemento.locator("img").first
                    miniatura = img.get_attribute("src", timeout=2000)
                    descripcion = img.get_attribute("alt", timeout=2000)
                except Exception:
                    miniatura, descripcion = PLACEHOLDER_VIDEO, SIN_DESCRIPCION

                videos_extraidos[href] = {
                    "miniatura": miniatura,
                    "descripcion": descripcion or SIN_DESCRIPCION,
                }

            for i, (enlace, v) in enumerate(list(videos_extraidos.items())[:MAX_VIDEOS]):
                datos_descarga["videos_recientes"].append({
                    "posicion": i + 1,
                    "enlace": enlace,
                    "miniatura": v["miniatura"],
                    "descripcion": v["descripcion"],
                    "estado": "Extraído exitosamente",
                })

            nombre_archivo = f"datos_{username}.json"
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(datos_descarga, f, ensure_ascii=False, indent=4)

            print(f"\n¡ÉXITO! Se extrajeron {len(datos_descarga['videos_recientes'])} videos. Archivo: {nombre_archivo}")

        except Exception as e:
            print("\nError: TikTok bloqueó la conexión o saltó un Captcha. "
                  "Borra la carpeta 'perfil_tiktok', espera unos minutos y reintenta.")
            print(f"Detalle técnico: {e}")
            nombre_archivo = None

        finally:
            context.close()

    return nombre_archivo


def main():
    parser = argparse.ArgumentParser(description="Extrae datos de TikTok y analiza Big Five.")
    parser.add_argument("usuario", nargs="?", help="Username de TikTok (sin @)")
    parser.add_argument("--sin-analisis", action="store_true", help="Solo extraer, sin análisis Big Five")
    args = parser.parse_args()

    usuario = args.usuario or input("Ingresa el username de TikTok (sin el @): ")
    usuario = usuario.strip().lstrip("@")

    archivo = scrape_tiktok_profile(usuario)

    if archivo and not args.sin_analisis:
        # Se importa aquí para no exigir GROQ_API_KEY si solo se quiere extraer
        from analisis_bigfive import analizar_perfil
        analizar_perfil(archivo)


if __name__ == "__main__":
    main()
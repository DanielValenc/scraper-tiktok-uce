from playwright.sync_api import sync_playwright

def guardar_sesion():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.tiktok.com/")
        
        print("Navegador abierto. Resuelve el rompecabezas o Captcha si aparece.")
        input("Presiona ENTER en esta terminal cuando la página haya cargado por completo...")
        
        context.storage_state(path="state.json")
        print("¡Sesión guardada exitosamente en state.json!")
        
        browser.close()

if __name__ == "__main__":
    guardar_sesion()
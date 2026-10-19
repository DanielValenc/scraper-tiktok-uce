from playwright.sync_api import sync_playwright

def scrape_tiktok_profile(username):
    print(f"\nIniciando extracción automática para: @{username}")
    
    with sync_playwright() as p:
        # El navegador ya no se mostrará visualmente
        browser = p.chromium.launch(headless=False)
        
        # Inyectamos el archivo state.json generado en el paso anterior
        context = browser.new_context(
            storage_state="state.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        page.goto(f"https://www.tiktok.com/@{username}")
        
        try:
            page.wait_for_selector('strong[title="Seguidores"]', timeout=10000)
            
            siguiendo = page.locator('strong[title="Siguiendo"]').text_content()
            seguidores = page.locator('strong[title="Seguidores"]').text_content()
            likes = page.locator('strong[title="Me gusta"]').text_content()
            
            print("\n--- DATOS DEL PERFIL ---")
            print(f"Siguiendo: {siguiendo}")
            print(f"Seguidores: {seguidores}")
            print(f"Me Gusta: {likes}")
            print("------------------------\n")
            
        except Exception as e:
            print("Error: No se encontraron los datos. El usuario no existe o las cookies caducaron.")
        
        browser.close()

if __name__ == "__main__":
    target_user = input("Ingresa el username de TikTok (sin el @): ")
    scrape_tiktok_profile(target_user)
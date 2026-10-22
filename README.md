# 📱 TikTok Data Extractor - UCE

Este proyecto es un scraper automatizado desarrollado para la asignatura de **Dispositivos Móviles (10mo Semestre)** de la **Universidad Central del Ecuador (UCE)**. Permite extraer información pública de perfiles de TikTok y visualizarla en un dashboard interactivo, sin utilizar APIs de terceros ni extensiones prefabricadas.

## ✨ Características

* **Extracción de Perfil:** Obtiene la foto de perfil, cantidad de seguidores, cuentas seguidas y total de "Me gusta".
* **Extracción de Feed:** Captura los enlaces directos y las imágenes de miniatura de las últimas 10 publicaciones simulando el comportamiento humano (scroll).
* **Evasión de Seguridad Nativa:** Utiliza un contexto persistente de Chrome para guardar la sesión localmente y superar los Captchas de TikTok de forma manual en la primera ejecución, automatizando las siguientes.
* **Exportación JSON:** Guarda toda la información extraída de forma estructurada en un archivo `.json`.
* **Dashboard Frontend:** Interfaz gráfica moderna y responsiva construida con HTML5, Tailwind CSS y Vanilla JS para visualizar los datos extraídos.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.x
* **Web Scraping:** Playwright (Sync API)
* **Frontend:** HTML5, Tailwind CSS (CDN), Vanilla JavaScript
* **Almacenamiento:** Archivos `.json` nativos
* **Control de Versiones:** Git & GitHub

## 🚀 Instalación y Configuración

Sigue estos pasos para clonar y ejecutar el proyecto en tu entorno local:

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
   cd scraper-tiktok-uce
# 📊 TikTok Data Extractor + Análisis de Personalidad Big Five

Proyecto que **extrae datos públicos de un perfil de TikTok**, los guarda en un archivo JSON, los analiza con **Inteligencia Artificial** para estimar los rasgos del modelo de personalidad **Big Five (OCEAN)** y los muestra en un **dashboard web** fácil de leer.

> **Proyecto académico – UCE.** Los resultados son una estimación automática con fines educativos, no un diagnóstico psicológico.

---

## 📑 Tabla de contenidos

1. [¿Qué hace este proyecto?](#-qué-hace-este-proyecto)
2. [Flujo de trabajo](#-flujo-de-trabajo)
3. [Estructura del proyecto](#-estructura-del-proyecto)
4. [Tecnologías utilizadas](#-tecnologías-utilizadas)
5. [Instalación](#-instalación)
6. [Configuración](#-configuración)
7. [Cómo usarlo (paso a paso)](#-cómo-usarlo-paso-a-paso)
8. [Explicación de cada archivo](#-explicación-de-cada-archivo)
9. [Ejemplo del JSON generado](#-ejemplo-del-json-generado)
10. [¿Qué es el modelo Big Five?](#-qué-es-el-modelo-big-five)
11. [Problemas comunes](#-problemas-comunes)
12. [Limitaciones y consideraciones éticas](#-limitaciones-y-consideraciones-éticas)

---

## 🎯 ¿Qué hace este proyecto?

El sistema trabaja en **tres etapas**:

| Etapa | Archivo | ¿Qué hace? |
|-------|---------|------------|
| 1. Extracción | `scraper_tiktok.py` | Abre un navegador automatizado, entra al perfil de TikTok y guarda estadísticas, foto y los últimos 10 videos con sus descripciones. |
| 2. Análisis | `analisis_bigfive.py` | Toma las descripciones de los videos y le pide a una IA (vía API de Groq) que estime los 5 rasgos de personalidad. |
| 3. Visualización | `index.html` | Dashboard web que lee el JSON y muestra perfil, barras de personalidad y videos. |

---

## 🔄 Flujo de trabajo

```
 Usuario de TikTok
        │
        ▼
┌─────────────────────┐
│  scraper_tiktok.py  │  Playwright abre TikTok y extrae los datos
└─────────┬───────────┘
          ▼
   datos_<usuario>.json      (perfil + 10 videos)
          │
          ▼
┌─────────────────────┐
│ analisis_bigfive.py │  Envía las descripciones a la IA (Groq)
└─────────┬───────────┘
          ▼
   datos_<usuario>.json      (ahora incluye "analisis_bigfive")
          │
          ▼
┌─────────────────────┐
│     index.html      │  Dashboard con barras y resumen
└─────────────────────┘
```

---

## 📁 Estructura del proyecto

```
tiktok-bigfive/
├── scraper_tiktok.py        # Extracción de datos con Playwright
├── analisis_bigfive.py      # Análisis de personalidad con IA
├── index.html               # Dashboard web
├── datos_<usuario>.json     # Archivo generado automáticamente
├── perfil_tiktok/           # Carpeta de sesión del navegador (se crea sola)
└── README.md
```

> Si tus archivos tienen otros nombres, ajusta los nombres en los comandos de este documento.

---

## 🛠 Tecnologías utilizadas

- **Python 3.9+**
- **Playwright**: automatiza el navegador Chromium para leer TikTok.
- **Requests**: envía la petición a la API de IA.
- **Groq API**: ejecuta el modelo de lenguaje que hace el análisis.
- **HTML + JavaScript + Tailwind CSS**: dashboard visual (Tailwind se carga por CDN).

---

## ⚙️ Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <URL-de-tu-repositorio>
cd tiktok-bigfive
```

### 2. (Recomendado) Crear un entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install playwright requests
playwright install chromium
```

El último comando descarga el navegador Chromium que usa Playwright.

---

## 🔑 Configuración

El análisis necesita una **API Key de Groq** (puedes crear una gratis en [console.groq.com](https://console.groq.com)).

En `analisis_bigfive.py` reemplaza el valor de la variable:

```python
api_key = "TU_API_KEY_GROQ_AQUI"
```

> ⚠️ **Importante:** nunca subas tu API Key a GitHub. Si el repositorio es público, usa una variable de entorno:
>
> ```python
> import os
> api_key = os.getenv("GROQ_API_KEY")
> ```
>
> y define la variable antes de ejecutar (`export GROQ_API_KEY="tu_clave"` en Mac/Linux, `set GROQ_API_KEY=tu_clave` en Windows).

También puedes cambiar el modelo en la variable `modelo_elegido`. Verifica en la [lista de modelos de Groq](https://console.groq.com/docs/models) que el nombre exista y esté disponible para tu cuenta.

---

## 🚀 Cómo usarlo (paso a paso)

### Paso 1: Extraer los datos del perfil

```bash
python scraper_tiktok.py
```

El programa pedirá el usuario (sin el `@`):

```
Ingresa el username de TikTok (sin el @): danielvalencia365
```

Se abrirá una ventana de Chrome. Si TikTok muestra un **Captcha**, resuélvelo manualmente; el programa espera hasta 60 segundos. Al terminar se crea el archivo `datos_<usuario>.json`.

### Paso 2: Analizar la personalidad (Big Five)

En `analisis_bigfive.py`, la última línea indica qué archivo se analiza:

```python
analizar_perfil("datos_danielvalencia365.json")
```

Cámbiala por el archivo del usuario que acabas de extraer y ejecuta:

```bash
python analisis_bigfive.py
```

El resultado se **agrega al mismo JSON** bajo la clave `analisis_bigfive`.

### Paso 3: Ver el dashboard

El dashboard lee el JSON con `fetch()`, por lo que **no funciona abriendo el HTML con doble clic**. Debes servirlo desde un servidor local, desde la carpeta del proyecto:

```bash
python -m http.server 8000
```

Luego abre en tu navegador: **http://localhost:8000/index.html**, escribe el usuario (el mismo que usaste en el paso 1) y presiona **Cargar Datos**.

---

## 📖 Explicación de cada archivo

### 1. `scraper_tiktok.py` – Extracción de datos

Usa **Playwright** para controlar un navegador real, como si fuera una persona navegando. Pasos principales:

1. **Abre el navegador con sesión persistente.** Guarda cookies en la carpeta `perfil_tiktok/` para reducir los Captchas repetidos.
2. **Entra al perfil** `https://www.tiktok.com/@usuario`.
3. **Extrae las estadísticas:** siguiendo, seguidores y me gusta.
4. **Obtiene la foto de perfil.** Si falla, usa una imagen de reemplazo.
5. **Hace scroll simulado** para que TikTok cargue los videos (carga diferida o *lazy loading*).
6. **Captura los videos:** enlace, miniatura y descripción (texto + hashtags), eliminando duplicados.
7. **Se queda con los 10 primeros** y los guarda en `datos_<usuario>.json` (UTF-8, con tildes y emojis).

> Los selectores como `strong[title="Seguidores"]` están en **español**, por lo que TikTok debe mostrarse en ese idioma. Si lo usas en otro idioma, ajusta esos textos.

### 2. `analisis_bigfive.py` – Análisis con IA

1. Lee el JSON generado por el scraper.
2. **Une las descripciones** de los 10 videos en un solo texto.
3. Construye un *prompt* que le pide a la IA actuar como psicólogo computacional y devolver **solo un JSON** con:
   - `Apertura`, `Responsabilidad`, `Extraversion`, `Amabilidad`, `Neuroticismo` (números de 0 a 100)
   - `resumen` (párrafo corto sobre la personalidad)
4. Envía la petición a la API de Groq con `temperature: 0.3` (respuestas más estables y menos aleatorias).
5. Limpia la respuesta (por si viene con formato Markdown), la convierte a JSON y la **guarda dentro del archivo original**.

### 3. `index.html` – Dashboard

Interfaz web con Tailwind CSS que muestra:

- Foto de perfil y nombre de usuario.
- Tarjetas con **siguiendo, seguidores y me gusta**.
- **Barras de progreso** para cada rasgo Big Five y el **resumen de personalidad** (solo aparece si el JSON ya tiene el análisis).
- **Cuadrícula de videos** con miniatura, descripción y enlace al video original.

---

## 🧾 Ejemplo del JSON generado

```json
{
    "usuario": "ejemplo",
    "perfil": {
        "foto_perfil": "https://...",
        "siguiendo": "120",
        "seguidores": "15.3K",
        "me_gusta": "230K"
    },
    "videos_recientes": [
        {
            "posicion": 1,
            "enlace": "https://www.tiktok.com/@ejemplo/video/123456789",
            "miniatura": "https://...",
            "descripcion": "Mi nuevo video #viral #baile",
            "estado": "Extraído exitosamente"
        }
    ],
    "analisis_bigfive": {
        "Apertura": 72,
        "Responsabilidad": 55,
        "Extraversion": 80,
        "Amabilidad": 65,
        "Neuroticismo": 30,
        "resumen": "Persona creativa y sociable, con tendencia a expresarse abiertamente..."
    }
}
```

---

## 🧠 ¿Qué es el modelo Big Five?

También conocido como **OCEAN**, es uno de los modelos más usados en psicología para describir la personalidad en cinco dimensiones:

| Rasgo | Significa… | Puntaje alto | Puntaje bajo |
|-------|-----------|--------------|--------------|
| **O**penness (Apertura) | Curiosidad y creatividad | Imaginativo, abierto a nuevas ideas | Práctico, prefiere lo conocido |
| **C**onscientiousness (Responsabilidad) | Organización y disciplina | Ordenado, cumplido | Espontáneo, flexible |
| **E**xtraversion (Extraversión) | Energía social | Sociable, expresivo | Reservado, tranquilo |
| **A**greeableness (Amabilidad) | Empatía y cooperación | Cálido, colaborador | Directo, competitivo |
| **N**euroticism (Neuroticismo) | Sensibilidad emocional | Más ansioso o reactivo | Calmado, estable |

---

## 🩺 Problemas comunes

| Problema | Posible causa | Solución |
|----------|---------------|----------|
| *"TikTok bloqueó la conexión o saltó un Captcha"* | Detección de bot o página que no cargó | Borra la carpeta `perfil_tiktok/`, espera unos minutos y reintenta. Resuelve el Captcha manualmente. |
| No encuentra los selectores de estadísticas | TikTok cambió su HTML o el idioma no es español | Actualiza los selectores en el scraper. |
| *"No se encontró el archivo JSON"* en el análisis | Aún no ejecutaste el scraper o el nombre no coincide | Ejecuta el paso 1 y revisa el nombre en `analizar_perfil(...)`. |
| Error de la API (401) | API Key inválida | Revisa tu clave de Groq. |
| Error de la API (404 / modelo no encontrado) | Nombre de modelo incorrecto | Verifica el modelo en la documentación de Groq. |
| *"Error parseando el resultado"* | La IA no devolvió un JSON válido o no había descripciones | Vuelve a ejecutar; revisa que los videos tengan texto. |
| El dashboard dice que no encuentra el archivo | Abriste el HTML directamente o el usuario no coincide | Usa `python -m http.server` y escribe el usuario exacto. |

---

## ⚖️ Limitaciones y consideraciones éticas

- **No es un test psicológico validado.** La IA estima rasgos a partir de unas pocas descripciones y hashtags, que muestran solo una parte de la persona. Los porcentajes son orientativos.
- **Muestra pequeña:** solo se analizan 10 videos, y las descripciones suelen ser cortas.
- **Privacidad:** analiza únicamente cuentas públicas, con fines educativos, y con consentimiento de la persona cuando sea posible. No uses los resultados para tomar decisiones sobre nadie.
- **Términos de uso:** el scraping puede ir contra los términos de servicio de TikTok y su estructura cambia con frecuencia, por lo que el código puede requerir mantenimiento.
- **Datos enviados a terceros:** el texto de los videos se envía a la API de Groq para ser procesado.

---

## 👤 Autor

**[Tu nombre]** – Universidad Central del Ecuador (UCE)
📧 [tu-correo@ejemplo.com]

---

## 📄 Licencia

Proyecto con fines académicos. Agrega aquí la licencia que prefieras (por ejemplo, MIT).

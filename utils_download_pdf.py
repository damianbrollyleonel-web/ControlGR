# utils_download_pdf.py
import os
import requests
from datetime import datetime
import time

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def setup_selenium_headless():
    chrome_options = Options()
    # headless "new" es más compatible; si falla prueba "--headless"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1200,800")
    # Evitar detección básica
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def cookies_dict_from_driver(driver):
    cookies = driver.get_cookies()
    cookie_dict = {}
    for c in cookies:
        cookie_dict[c['name']] = c['value']
    return cookie_dict

def download_pdf(url, wait_seconds=3, timeout=60):
    """
    Intenta descargar el PDF de la URL usando Selenium para 'abrir' la URL
    y luego requests.get() con el user-agent y cookies obtenidas del navegador.
    Devuelve la ruta local del PDF guardado en pdfs/.
    Lanza Exception si no puede descargar (para que la app pueda informar).
    """
    # Normalizar url (admite que el usuario pegue ya la url completa o solo el hash)
    url = url.strip()

    # 1) Levantar Selenium y abrir URL
    driver = None
    try:
        driver = setup_selenium_headless()
        driver.get(url)
        # esperar un poco a que el servidor responda y se establezcan cookies
        time.sleep(wait_seconds)

        # Obtener user-agent y cookies desde el driver
        user_agent = driver.execute_script("return navigator.userAgent;")
        cookies = cookies_dict_from_driver(driver)

    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        raise Exception(f"Error inicializando Selenium: {e}")

    # 2) Hacer petición final con requests con headers + cookies de Selenium
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
        "Referer": url
    }

    try:
        # Convertir dict cookies a requests cookie format
        s = requests.Session()
        for k, v in cookies.items():
            s.cookies.set(k, v)

        r = s.get(url, headers=headers, timeout=timeout, stream=True)
        if r.status_code != 200:
            raise Exception(f"Status {r.status_code}")

        # Guardar PDF con formato acordado: <timestamp> o intenta inferir correlativo después
        filename = f"GR_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        path = os.path.join(PDF_DIR, filename)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return path

    except Exception as e:
        raise Exception(f"Error al descargar PDF (requests): {e}")

    finally:
        try:
            driver.quit()
        except:
            pass


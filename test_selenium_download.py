import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

# URL del QR
url = "https://e-factura.sunat.gob.pe/v1/contribuyente/gre/comprobantes/descargaqr?hashqr=r6yMzG0GZ3Opf8hbeMWUs4SA/eWv0dtU/EXnJXG6dNoWxv0FKwDJqLF3yU/24762SSN7NPzVlv7XIAW6TREt0hknQJqMj8iobsKxiJRbjJ4="

# Carpeta destino
download_dir = os.path.join(os.getcwd(), "pdfs")
os.makedirs(download_dir, exist_ok=True)

# Configuración de Chrome en modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True
})

# Inicializa Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

print("Abriendo enlace en navegador virtual...")
driver.get(url)

# Esperar unos segundos para que se descargue
time.sleep(10)

driver.quit()

print(f"✅ Proceso completado. Verifica la carpeta: {download_dir}")

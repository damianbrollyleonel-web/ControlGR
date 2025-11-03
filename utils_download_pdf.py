import os
import requests
from datetime import datetime

def download_pdf(url):
    os.makedirs("pdfs", exist_ok=True)

    nombre_pdf = f"GR_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_pdf = os.path.join("pdfs", nombre_pdf)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=60)
    if r.status_code != 200:
        raise Exception(f"Error al descargar PDF: {r.status_code}")

    with open(ruta_pdf, "wb") as f:
        f.write(r.content)

    return ruta_pdf

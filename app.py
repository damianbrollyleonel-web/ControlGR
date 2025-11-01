import streamlit as st
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner
import os
from datetime import datetime
import pdfplumber
import re
import tempfile
import shutil
from PIL import Image
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ==============================
# 📌 CONFIG STREAMLIT
# ==============================
st.set_page_config(page_title="Control de Entregas GR", page_icon="📦")

# ==============================
# 📌 CARPETAS
# ==============================
CARPETA_PDFS = "pdfs"
CARPETA_FOTOS = "fotos"
CARPETA_EXCEL = "registros"
EXCEL_PATH = os.path.join(CARPETA_EXCEL, "registro_entregas.xlsx")

os.makedirs(CARPETA_PDFS, exist_ok=True)
os.makedirs(CARPETA_FOTOS, exist_ok=True)
os.makedirs(CARPETA_EXCEL, exist_ok=True)

# ==============================
# 📌 FUNCIONES
# ==============================
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def descargar_pdf(url):
    """Descarga PDF desde URL del QR usando Selenium"""
    try:
        driver = setup_driver()
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        driver.get(url)
        st.write("📥 Descargando PDF desde SUNAT...")

        # Espera breve para carga del documento
        st.info("⏳ Esperando la descarga del PDF...")
        driver.implicitly_wait(10)

        # Descargar PDF con request directo después del load Selenium
        r = requests.get(url, timeout=20)
        with open(temp.name, "wb") as f:
            f.write(r.content)

        driver.quit()
        return temp.name

    except Exception as e:
        st.error(f"❌ Error descargando PDF: {e}")
        return None

def extraer_datos(pdf_path):
    """Extrae Correlativo y Cliente desde el PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # ✅ Extraer correlativo (T003 - 00002092)
    correlativo = re.search(r"(T00\d)\s*-\s*(\d{5})", text)
    correlativo = f"{correlativo.group(1)} - {correlativo.group(2)}" if correlativo else ""

    # ✅ Cliente (solo nombre)
    cliente_match = re.search(r"Datos del destinatario:(.*?)Datos del traslado:", text, re.DOTALL)
    cliente = ""
    if cliente_match:
        bloque_dest = cliente_match.group(1).strip().split("\n")
        if bloque_dest:
            primera_linea = bloque_dest[0].strip()
            cliente = re.sub(r"\s*-\s*RUC.*", "", primera_linea)

    return correlativo, cliente

def guardar_registro(data):
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(EXCEL_PATH, index=False)

# ==============================
# 📌 UI — INTERFAZ
# ==============================
st.title("📦 Control de Entregas — GR")

st.subheader("1️⃣ Escanear QR de la Guía de Remisión")
qr_data = qrcode_scanner(key="qr1")

correlativo = st.text_input("📌 Correlativo", value="", disabled=True)
cliente = st.text_input("🏢 Cliente", value="", disabled=True)
transporte = st.selectbox("🚚 Transporte", [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
])

if qr_data:
    st.success("✅ QR Detectado")
    pdf_temp = descargar_pdf(qr_data)

    if pdf_temp:
        correlativo_ex, cliente_ex = extraer_datos(pdf_temp)
        if correlativo_ex:
            correlativo = correlativo_ex
            st.session_state["correlativo"] = correlativo_ex
        if cliente_ex:
            cliente = cliente_ex
            st.session_state["cliente"] = cliente_ex

# ✅ Sin edición si ya están cargados
correlativo = st.text_input("📌 Correlativo", value=st.session_state.get("correlativo", correlativo), disabled=True)
cliente = st.text_input("🏢 Cliente", value=st.session_state.get("cliente", cliente), disabled=True)

st.subheader("2️⃣ Datos de Entrega")
fecha_entrega = st.date_input("📅 Fecha de entrega", datetime.now())

motivo_estado = st.selectbox("⚠ Motivo del estado", [
    "Entrega Conforme",
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
])

estado_entrega = st.selectbox("📍 Estado", [
    "Entregado",
    "Entregado Parcial",
    "Rechazado"
])

observaciones = st.text_area("📝 Observaciones", "")

foto = st.camera_input("📷 Foto del comprobante firmado")

# ==============================
# 📌 GUARDAR
# ==============================
if st.button("💾 Guardar registro"):
    if not correlativo:
        st.error("❌ Falta correlativo (QR no válido)")
    else:
        ruta_pdf = os.path.join(CARPETA_PDFS, f"{correlativo.replace(' ', '_')}.pdf")
        shutil.copy(pdf_temp, ruta_pdf)

        ruta_foto = ""
        if foto:
            ruta_foto = os.path.join(CARPETA_FOTOS, f"FOTO_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
            image = Image.open(foto)
            image.save(ruta_foto)

        data = {
            "Fecha_de_Registro": datetime.now(),
            "Guia_de_Remision": correlativo,
            "Cliente": cliente,
            "Transporte": transporte,
            "Fecha_de_Entrega": fecha_entrega,
            "Motivo_Estado": motivo_estado,
            "Estado_Entrega": estado_entrega,
            "Observaciones": observaciones,
            "Ruta_PDF": ruta_pdf,
            "Ruta_Foto": ruta_foto
        }

        guardar_registro(data)
        st.success("✅ Registro guardado correctamente")
        st.balloons()

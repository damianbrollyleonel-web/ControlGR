import streamlit as st
from datetime import datetime
import pandas as pd
import os
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import requests
import tempfile
import pdfplumber
import re
from PIL import Image

# =============================================================
# CONFIGURACIÓN INICIAL
# =============================================================
st.set_page_config(page_title="Control GR - Entregas", layout="centered")

if "correlativo" not in st.session_state:
    st.session_state["correlativo"] = ""
if "cliente" not in st.session_state:
    st.session_state["cliente"] = ""

# Rutas
EXCEL_PATH = "registro_entregas.xlsx"
PDF_DIR = "pdfs"
FOTOS_DIR = "fotos"

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(FOTOS_DIR, exist_ok=True)

# =============================================================
# EXTRAER DATOS DEL PDF DE SUNAT
# =============================================================
def extraer_datos_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        correlativo = "No encontrado"
        cliente = "No encontrado"

        match_corr = re.search(r"(T00\d)\s*-\s*(\d+)", text)
        if match_corr:
            correlativo = f"{match_corr.group(1)} - {match_corr.group(2)}"

        match_dest = re.search(r"Datos del destinatario:(.*?)Datos del traslado:", text, re.DOTALL)
        if match_dest:
            cliente = match_dest.group(1).strip().split("\n")[0]

        return correlativo, cliente

    except:
        return None, None

# =============================================================
# TÍTULO
# =============================================================
st.title("📦 Registro de Entregas - GR")

st.write("**Sube una foto del QR** para procesar la guía de remisión")

# =============================================================
# ESCANEO QR DESDE FOTO
# =============================================================
qr_file = st.file_uploader("📸 Foto del QR", type=["png", "jpg", "jpeg"], key="qr_uploader")

qr_url = None

if qr_file:
    file_bytes = np.asarray(bytearray(qr_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    decoded = decode(img)

    if decoded:
        qr_url = decoded[0].data.decode("utf-8")
        st.success("✅ QR detectado correctamente")
        st.write("🔗 URL detectada:", qr_url)

        # Descarga del PDF
        try:
            r = requests.get(qr_url, timeout=30)
            if r.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(r.content)
                    pdf_path = tmp_pdf.name

                # Extraemos datos del PDF
                correlativo, cliente = extraer_datos_pdf(pdf_path)

                st.session_state["correlativo"] = correlativo or "No encontrado"
                st.session_state["cliente"] = cliente or "No encontrado"

                st.success("📄 PDF procesado correctamente ✅")

            else:
                st.error("❌ No se pudo descargar el PDF desde la URL del QR")

        except Exception as e:
            st.error(f"⚠️ Error al descargar el PDF: {e}")

    else:
        st.error("❌ No se pudo leer el QR. Intenta otra foto.")

# =============================================================
# DATOS CARGADOS AUTOMÁTICAMENTE
# =============================================================
st.subheader("📑 Datos identificados automáticamente")

correlativo = st.text_input("📌 Correlativo", value=st.session_state["correlativo"], disabled=True)
cliente = st.text_input("🏬 Cliente", value=st.session_state["cliente"], disabled=True)

# Transporte seleccionado manualmente
transporte = st.selectbox("🚚 Transporte", [
    "",
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
])

# Fecha entrega
fecha_entrega = st.date_input("📅 Fecha de entrega", datetime.now())

# Foto del comprobante firmado
st.subheader("📷 Foto del Comprobante Firmado")
foto_comprobante = st.camera_input("Toma la foto")

# Estado de entrega
estado_entrega = st.selectbox("📦 Estado de entrega", ["Entregado", "Rechazado", "Entregado Parcialmente"])

# Motivo (si hay problema)
motivo_estado = st.selectbox("⚠️ Motivo de Estado", [
    "",
    "Entrega Conforme",
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
])

observaciones = st.text_area("📝 Observaciones adicionales")

# =============================================================
# GUARDAR REGISTRO
# =============================================================
if st.button("✅ Guardar Registro"):

    if not correlativo or correlativo == "No encontrado":
        st.error("⚠️ Primero debes subir el QR correctamente.")
    else:
        foto_name = None
        if foto_comprobante:
            img = Image.open(foto_comprobante)
            foto_name = os.path.join(FOTOS_DIR, f"FOTO_{correlativo.replace(' ', '_')}.jpg")
            img.save(foto_name)

        new_row = {
            "Fecha_de_Registro": datetime.now(),
            "Correlativo": correlativo,
            "Cliente": cliente,
            "Transporte": transporte,
            "Fecha_de_Entrega": fecha_entrega,
            "Estado_Entrega": estado_entrega,
            "Motivo_Estado": motivo_estado,
            "Observaciones": observaciones,
            "Ruta_Foto": foto_name
        }

        if os.path.exists(EXCEL_PATH):
            df = pd.read_excel(EXCEL_PATH)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])

        df.to_excel(EXCEL_PATH, index=False)
        st.success("✅ Registro guardado exitosamente ✅")


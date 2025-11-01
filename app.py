import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pdfplumber
import requests
import os
import re
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Control de Entregas", layout="centered")

# --- Sesión ---
if "correlativo" not in st.session_state:
    st.session_state.correlativo = ""
if "cliente" not in st.session_state:
    st.session_state.cliente = ""

st.title("📦 Control de Entregas - GR")

st.subheader("1️⃣ Escanear QR del Comprobante")

# Scanner - Cámara trasera
qr_result = qrcode_scanner(key="qr_cam", label="Escanee el QR", camera="environment")

SUNAT_BASE = "https://e-factura.sunat.gob.pe/v1/contribuyente/gre/comprobantes/descargaqr?hashqr="

def extraer_datos_pdf(pdf_bytes):
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() + " "

        correlativo = ""
        cliente = ""

        cor_match = re.search(r"(\w{3}\s*-\s*\d+)", texto)
        cli_match = re.search(r"Cliente\s*:\s*([A-Za-z0-9\s\.\-&]+)", texto)

        if cor_match:
            correlativo = cor_match.group(1).replace(" ", "")
        if cli_match:
            cliente = cli_match.group(1).strip()

        return correlativo, cliente
    except:
        return "", ""

if qr_result:
    st.success("✅ QR detectado ✔")
    st.write("📄 Descargando PDF desde SUNAT...")

    try:
        url_pdf = SUNAT_BASE + qr_result
        response = requests.get(url_pdf, timeout=20)

        if response.status_code == 200:
            correlativo, cliente = extraer_datos_pdf(response.content)
            st.session_state.correlativo = correlativo
            st.session_state.cliente = cliente
            st.success("📥 PDF procesado correctamente ✅")
        else:
            st.error("⚠ No fue posible descargar el PDF")
    except:
        st.error("❌ Error al procesar el QR")

st.write("---")
st.subheader("2️⃣ Datos de la Entrega")

col1, col2 = st.columns(2)
with col1:
    st.text_input("📌 Correlativo", value=st.session_state.correlativo, disabled=True)
with col2:
    st.text_input("🏪 Cliente", value=st.session_state.cliente, disabled=True)

fecha_entrega = st.date_input("📅 Fecha de Entrega")

motivo_estado = st.selectbox("📍 Motivo de Estado", [
    "Entrega Conforme",
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
])

estado_entrega = st.radio("🚚 Estado de la Entrega", ["Entregado", "No Entregado"])

observaciones = st.text_area("📝 Observaciones")

foto = st.camera_input("📸 Foto del comprobante firmado")

if st.button("✅ Guardar Entrega"):
    if not st.session_state.correlativo:
        st.warning("⚠ Primero escanee un QR válido.")
    else:
        st.success("✅ Entrega registrada correctamente (almacenamiento pendiente a OneDrive)")


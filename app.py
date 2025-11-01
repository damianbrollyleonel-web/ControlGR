import streamlit as st
import pandas as pd
import requests
import pdfplumber
import re
import os
from io import BytesIO
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="ControlGR", page_icon="🚚", layout="centered")

st.title("📦 Control de Entrega - Guías de Remisión")

# ---- Carpetas locales ----
os.makedirs("pdfs", exist_ok=True)
os.makedirs("fotos", exist_ok=True)

def extract_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([p.extract_text() or "" for p in pdf.pages])

    correl = re.search(r"(T00\d)\s*-\s*(\d{5})", text)
    correlativo = f"{correl.group(1)} - {correl.group(2)}" if correl else "No encontrado"

    cliente_match = re.search(r"Datos del destinatario:(.*?)Datos del traslado:", text, re.DOTALL)
    cliente = "No encontrado"
    if cliente_match:
        bloque = cliente_match.group(1).strip().split("\n")
        if bloque:
            cliente = re.sub(r"\s*-\s*RUC.*", "", bloque[0].strip())

    return correlativo, cliente


st.subheader("1️⃣ Escanear QR de la Guía")
qr_image = st.camera_input("📷 Escanear QR", help="Enfoca el QR hasta que se lea automáticamente")

correlativo = ""
cliente = ""

if qr_image:
    with st.spinner("⏳ Decodificando QR..."):
        import cv2
        import numpy as np
        from pyzbar.pyzbar import decode

        img = Image.open(qr_image)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        decoded = decode(img_cv)

        if decoded:
            qr_url = decoded[0].data.decode("utf-8")
            st.success("✅ QR reconocido")
            st.write(qr_url)

            with st.spinner("📥 Descargando PDF..."):
                try:
                    r = requests.get(qr_url, timeout=60)
                    if r.status_code == 200:
                        pdf_name = f"pdfs/GR_{datetime.now().strftime('%H%M%S')}.pdf"
                        with open(pdf_name, "wb") as f:
                            f.write(r.content)

                        correlativo, cliente = extract_from_pdf(pdf_name)
                    else:
                        st.error("⚠ Error al descargar PDF")
                except Exception as e:
                    st.error(f"❌ Error obteniendo PDF: {e}")
        else:
            st.warning("⚠ No se detectó QR")


# ---- DATA FORM ----
st.subheader("2️⃣ Datos de la entrega")

col1, col2 = st.columns(2)
with col1:
    correlativo = st.text_input("Correlativo", value=correlativo, disabled=True)
with col2:
    cliente = st.text_input("Cliente", value=cliente, disabled=True)

fecha_entrega = st.date_input("📅 Fecha de entrega")

transporte = st.selectbox("🚚 Empresa de Transporte", [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
])

motivo_estado = st.selectbox("📌 Motivo de Estado", [
    "Entrega Conforme",
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
])

estado_entrega = st.selectbox("Estado de la entrega", [
    "Entregado",
    "Parcial",
    "Rechazado"
])

foto = st.camera_input("📸 Foto del comprobante firmado")
observaciones = st.text_area("📝 Observaciones")

if st.button("✅ Guardar Registro"):
    if not correlativo or not cliente:
        st.error("⚠ Escanee el QR primero")
    else:
        foto_path = ""
        if foto:
            img = Image.open(foto)
            foto_path = f"fotos/foto_{datetime.now().strftime('%H%M%S')}.jpg"
            img.save(foto_path)

        registro = {
            "Fecha_de_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Correlativo": correlativo,
            "Cliente": cliente,
            "Fecha_entrega": str(fecha_entrega),
            "Transporte": transporte,
            "Motivo_Estado": motivo_estado,
            "Estado_entrega": estado_entrega,
            "Observaciones": observaciones,
            "Ruta_foto": foto_path
        }

        df = pd.DataFrame([registro])

        excel_file = "registro_entregas.xlsx"
        if os.path.exists(excel_file):
            df.to_excel(excel_file, index=False, header=False, mode='a')
        else:
            df.to_excel(excel_file, index=False)

        st.success("✅ Registro Guardado correctamente")



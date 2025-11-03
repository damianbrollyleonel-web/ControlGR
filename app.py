import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import os
from datetime import datetime

# 📌 Carpeta donde guardamos PDFs y fotos dentro del servidor
PDF_FOLDER = "pdfs"
PHOTO_FOLDER = "fotos"

os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(PHOTO_FOLDER, exist_ok=True)

st.set_page_config(page_title="Control GR", layout="centered")

st.title("🚚 Control de Entrega GR - Chofer")

st.markdown("Escanee el **QR** o cargue una **foto** del mismo para procesar la Guía de Remisión.")

# =====================================================
# ✅ CAPTURA QR DESDE CÁMARA DEL MÓVIL
# =====================================================
qr_result = qrcode_scanner(key="scanner_qr", label="Escanear QR")

if qr_result:
    st.success("✅ QR detectado!")
    st.session_state["qr_url"] = qr_result
else:
    st.info("📌 Escanee el QR de la Guía de Remisión")

# =====================================================
# ✅ Mostrar campos auto-rellenados SOLO SI hay QR
# =====================================================
correlativo = st.session_state.get("correlativo", "")
cliente = st.session_state.get("cliente", "")

st.text_input("📌 Correlativo", value=correlativo, disabled=True)
st.text_input("🏢 Cliente", value=cliente, disabled=True)

# =====================================================
# ✅ Fecha de entrega (editable por el chofer)
# =====================================================
fecha_entrega = st.date_input("📅 Fecha de Entrega", datetime.today())

# =====================================================
# ✅ Foto del comprobante firmado
# =====================================================
uploaded_photo = st.camera_input("📸 Foto del Comprobante Firmado")

# =====================================================
# ✅ Lista de transportes (temporal mientras automatizamos extracción)
# =====================================================
transportes_opciones = [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
]
transporte = st.selectbox("🚛 Empresa de Transporte", transportes_opciones)

# =====================================================
# ✅ Estado de entrega
# =====================================================
estado_opciones = ["Entregado", "Entregado Parcialmente", "Rechazado"]
estado = st.selectbox("📦 Estado de la Entrega", estado_opciones)

# =====================================================
# ✅ Motivo del estado
# =====================================================
motivo_opciones = [
    "Entrega Conforme",
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
]
motivo_estado = st.selectbox("⚠ Motivo del Estado", motivo_opciones)

# ✅ Observaciones
observaciones = st.text_area("📝 Observaciones adicionales (opcional)")

# =====================================================
# ✅ Guardar datos en Excel + guardar foto
# =====================================================
def guardar_registro():
    # Guardar foto
    photo_path = ""
    if uploaded_photo:
        photo_filename = f"foto_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        photo_path = os.path.join(PHOTO_FOLDER, photo_filename)
        with open(photo_path, "wb") as f:
            f.write(uploaded_photo.getvalue())

    registro = {
        "Fecha_de_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Guia_de_Remision": correlativo,
        "Cliente": cliente,
        "Transporte": transporte,
        "Fecha_de_Entrega": fecha_entrega.strftime("%Y-%m-%d"),
        "Estado_Entrega": estado,
        "Motivo_Estado": motivo_estado,
        "Observaciones": observaciones,
        "Ruta_Foto": photo_path,
        "Ruta_PDF": ""
    }

    excel_path = "registro_entregas.xlsx"
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    else:
        df = pd.DataFrame([registro])

    df.to_excel(excel_path, index=False)
    st.success("✅ Registro guardado correctamente")

# Botón para guardar
if st.button("💾 Guardar Entrega"):
    guardar_registro()



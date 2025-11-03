import streamlit as st
import pandas as pd
import os
from datetime import datetime

PDF_FOLDER = "pdfs"
PHOTO_FOLDER = "fotos"

os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(PHOTO_FOLDER, exist_ok=True)

st.set_page_config(page_title="Control GR", layout="centered")

st.title("🚚 Control de Entrega GR - Chofer")

st.markdown("📌 Por favor ingrese la **URL del QR** (luego activaremos el escaneo directo).")

qr_url = st.text_input("🔗 Pega aquí el enlace del QR")

correlativo = st.session_state.get("correlativo", "")
cliente = st.session_state.get("cliente", "")

st.text_input("📌 Correlativo", value=correlativo, disabled=True)
st.text_input("🏢 Cliente", value=cliente, disabled=True)

fecha_entrega = st.date_input("📅 Fecha de Entrega", datetime.today())

uploaded_photo = st.camera_input("📸 Foto del Comprobante Firmado")

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

estado_opciones = ["Entregado", "Entregado Parcialmente", "Rechazado"]
estado = st.selectbox("📦 Estado de la Entrega", estado_opciones)

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

observaciones = st.text_area("📝 Observaciones adicionales (opcional)")

def guardar_registro():
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
        "Ruta_PDF": "",
        "URL_QR": qr_url
    }

    excel_path = "registro_entregas.xlsx"
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    else:
        df = pd.DataFrame([registro])

    df.to_excel(excel_path, index=False)
    st.success("✅ Registro guardado correctamente")

if st.button("💾 Guardar Entrega"):
    guardar_registro()

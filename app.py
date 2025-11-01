import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
from datetime import datetime
import os
import time

# ========================
# CONFIGURACIÓN DE PÁGINA
# ========================
st.set_page_config(page_title="Control de GR - Entregas", layout="centered")

# ========================
# VARIABLES DE ESTADO
# ========================
if "qr_url" not in st.session_state:
    st.session_state.qr_url = ""
if "correlativo" not in st.session_state:
    st.session_state.correlativo = ""
if "cliente" not in st.session_state:
    st.session_state.cliente = "(Pendiente leer PDF)"

# ========================
# CONFIG RUTAS LOCALES
# ========================
PDF_FOLDER = "pdfs"
PHOTO_FOLDER = "fotos"
EXCEL_FILE = "registro_entregas.xlsx"

os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(PHOTO_FOLDER, exist_ok=True)

# ========================
# SIMULACIÓN de extracción desde PDF
# (luego integramos Selenium)
# ========================
def extract_data_from_pdf_simulated(qr_url):
    # ➜ Aquí todavía no descargamos el PDF
    # Solo devuelve un ejemplo simulado confiable
    return {
        "correlativo": "T003 - 0002070",
        "cliente": "NEGOCIOS VICAMOR E.I.R.L. - RUC 20607074578"
    }

# ========================
# COLUMNA IZQUIERDA — QR
# ========================
st.header("📌 Registro de Entrega")

qr_result = qrcode_scanner("📷 Escanear Código QR")

if qr_result and qr_result != st.session_state.qr_url:
    st.session_state.qr_url = qr_result
    st.info(f"✅ QR Detectado:\n{qr_result}")
    time.sleep(1)

    extracted = extract_data_from_pdf_simulated(qr_result)
    st.session_state.correlativo = extracted["correlativo"]
    st.session_state.cliente = extracted["cliente"]

# ========================
# MOSTRAR DATOS EXTRAÍDOS
# ========================
st.subheader("📄 Datos del Comprobante (Automático)")
st.text_input("Correlativo", value=st.session_state.correlativo, disabled=True)
st.text_input("Cliente", value=st.session_state.cliente, disabled=True)

# ========================
# CAMPOS MANUALES
# ========================
st.subheader("📝 Información del Transporte")
fecha_entrega = st.date_input("📅 Fecha de entrega", value=datetime.today())
transporte = st.selectbox("🚚 Empresa de Transporte", [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
])

st.subheader("📌 Estado de la entrega")
estado_entrega = st.selectbox("Estado de la entrega", [
    "Entregado",
    "Entregado Parcialmente",
    "Rechazado"
])

motivo_estado = st.selectbox("Motivo de estado", [
    "Entrega Conforme",
    "Cliente NO solicitó pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
])

observaciones = st.text_area("🗒 Observaciones")

# ========================
# FOTO DEL COMPROBANTE
# ========================
st.subheader("📸 Foto del Comprobante")
foto = st.camera_input("Tomar foto del comprobante firmado")

# ========================
# BOTÓN GUARDAR
# ========================
if st.button("💾 Guardar Registro"):
    if not st.session_state.correlativo:
        st.error("⚠️ Primero debe escanear el QR")
    elif foto is None:
        st.error("⚠️ Debe tomar una foto")
    else:
        # Guardar foto
        foto_path = os.path.join(PHOTO_FOLDER, f"FOTO_{int(time.time())}.jpg")
        with open(foto_path, "wb") as f:
            f.write(foto.getbuffer())

        # Guardar en Excel
        nuevo_registro = pd.DataFrame([{
            "Fecha_Registro": datetime.now(),
            "Correlativo": st.session_state.correlativo,
            "Cliente": st.session_state.cliente,
            "Transporte": transporte,
            "Fecha_Entrega": fecha_entrega,
            "Estado_Entrega": estado_entrega,
            "Motivo_Estado": motivo_estado,
            "Observaciones": observaciones,
            "Ruta_Foto": foto_path
        }])

        if os.path.exists(EXCEL_FILE):
            df_existente = pd.read_excel(EXCEL_FILE)
            df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
        else:
            df_final = nuevo_registro

        df_final.to_excel(EXCEL_FILE, index=False)

        st.success("✅ Registro guardado correctamente")

        st.session_state.correlativo = ""
        st.session_state.cliente = "(Pendiente leer PDF)"
        st.session_state.qr_url = ""


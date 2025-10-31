import streamlit as st
import pandas as pd
import os
import datetime
from streamlit_qrcode_scanner import qrcode_scanner
import re

EXCEL_FILE = "registro_entregas.xlsx"
SHEET_NAME = "Entregas"

# -----------------------
# 📌 Función para extraer datos desde URL del QR
# -----------------------
def extract_data_from_qr_url(url):
    # Extraer correlativo ejemplo -> "T003-00002092"
    correlativo = "No detectado"
    cliente = "No detectado"

    # Regex para correlativo
    corr_match = re.search(r"(T00\d)[-/](\d{5})", url)
    if corr_match:
        correlativo = f"{corr_match.group(1)} - {corr_match.group(2)}"

    # Simulación de cliente mientras no usemos PDF
    # ⚠ Más adelante conectaremos a BD real / API
    cliente = "CLIENTE POR DEFINIR (QR sin PDF)"

    return correlativo, cliente


# -----------------------
# 📌 Crear archivo Excel si no existe
# -----------------------
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            "Fecha_de_Registro", "Correlativo", "Cliente", "Transporte",
            "Fecha_de_Entrega", "Estado", "Motivo_Estado", "Observaciones",
            "Ruta_PDF", "Ruta_Foto"
        ])
        df.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False)


# -----------------------
# 📌 Guardar registro
# -----------------------
def save_record(correlativo, cliente, transporte, fecha_entrega, estado, motivo, obs, ruta_pdf, ruta_foto):

    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

    nuevo = {
        "Fecha_de_Registro": datetime.datetime.now(),
        "Correlativo": correlativo,
        "Cliente": cliente,
        "Transporte": transporte,
        "Fecha_de_Entrega": fecha_entrega,
        "Estado": estado,
        "Motivo_Estado": motivo,
        "Observaciones": obs,
        "Ruta_PDF": ruta_pdf,
        "Ruta_Foto": ruta_foto
    }

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False)


# -----------------------
# ✅ INTERFAZ STREAMLIT
# -----------------------
st.set_page_config(page_title="Control GR", layout="wide")
st.title("📦 Control de Guías de Remisión")

st.subheader("1️⃣ Escanear QR")
qr_data = qrcode_scanner()

correlativo = st.text_input("Correlativo", disabled=True)
cliente = st.text_input("Cliente", disabled=True)

if qr_data:
    st.success("✅ QR detectado. Presiona el botón para extraer datos.")
    if st.button("Procesar QR y extraer datos"):
        corr, cli = extract_data_from_qr_url(qr_data)
        st.session_state["correlativo"] = corr
        st.session_state["cliente"] = cli

# Mostrar los datos guardados en sesión (si existen)
if "correlativo" in st.session_state:
    correlativo = st.session_state["correlativo"]
    st.text_input("Correlativo", correlativo, disabled=True)

if "cliente" in st.session_state:
    cliente = st.session_state["cliente"]
    st.text_input("Cliente", cliente, disabled=True)

# -----------------------
# 2️⃣ Completar datos
# -----------------------
st.subheader("2️⃣ Completar Datos")

transportes_lista = [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
]
transporte = st.selectbox("Transporte", transportes_lista)

fecha_entrega = st.date_input("Fecha de entrega")

estado = st.selectbox("Estado entrega", ["Entregado", "Entregado Parcial", "Rechazado"])

motivos = [
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
]
motivo = st.selectbox("Motivo de Estado", motivos)

obs = st.text_area("Observaciones")

# Foto comprobante
foto = st.camera_input("Foto del comprobante firmado")

# ✅ Guardar
if st.button("Guardar Registro"):
    ruta_foto = None
    if foto:
        foto_path = f"fotos/{correlativo.replace(' ','_')}_{datetime.datetime.now().timestamp()}.jpg"
        os.makedirs("fotos", exist_ok=True)
        with open(foto_path, "wb") as f:
            f.write(foto.getbuffer())
        ruta_foto = foto_path

    save_record(correlativo, cliente, transporte, fecha_entrega, estado, motivo, obs, None, ruta_foto)

    st.success("✅ Registro guardado correctamente")
    st.balloons()


# Inicializar excel si no existe
init_excel()



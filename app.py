import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import os, uuid
from datetime import datetime

# --- Config ---
st.set_page_config(page_title="ControlGR - Entregas", layout="centered")

EXCEL_FILE = "registro_entregas.xlsx"
SHEET_NAME = "Entregas"
FOTOS_DIR = "fotos"
os.makedirs(FOTOS_DIR, exist_ok=True)

# Init excel file if not exists
if not os.path.exists(EXCEL_FILE):
    df_init = pd.DataFrame(columns=[
        "Fecha_de_Registro", "Correlativo", "Cliente", "Transporte",
        "Fecha_de_Entrega", "Estado", "Motivo_Estado", "Observaciones",
        "Ruta_PDF", "Ruta_Foto"
    ])
    df_init.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False)

st.title("📦 ControlGR — Registro de Entregas (GR)")
st.write("Escanea el QR (o pega la URL) para autocompletar Correlativo y Cliente.")

# ---------------- QR Scanner ----------------
st.subheader("1) Escanear QR")
qr_result = qrcode_scanner(key="qr-scanner")

# campo manual alternativo (opcional)
qr_manual = st.text_input("O pega aquí la URL del QR (opcional)")

# preferencia: qr_result primero, sino qr_manual
qr_url = qr_result if qr_result else (qr_manual.strip() if qr_manual else "")

# session storage for extracted values
if "correlativo" not in st.session_state:
    st.session_state["correlativo"] = ""
if "cliente" not in st.session_state:
    st.session_state["cliente"] = ""

# función simple para extraer correlativo y cliente desde la URL (si viene codificado)
import re
def extract_from_qr_url(url):
    corr = ""
    cli = ""
    if not url:
        return corr, cli
    # intentar extraer correlativo tipo T003-00002092 o T003 - 00002092
    m = re.search(r"(T0?\d{2,3})\s*[-/]\s*(\d{4,10})", url, flags=re.IGNORECASE)
    if m:
        corr = f"{m.group(1).upper()} - {m.group(2)}"
    # cliente temporal (puede mejorarse con lookup)
    cli = "CLIENTE POR DEFINIR (QR)"
    return corr, cli

if qr_url:
    corr, cli = extract_from_qr_url(qr_url)
    # guardar en sesión (solo si se extrajo algo)
    if corr:
        st.session_state["correlativo"] = corr
    if cli:
        st.session_state["cliente"] = cli
    st.success("✅ QR procesado (si el QR contiene datos). Verifica abajo.")

# ---------------- Datos extraídos (NO editables) ----------------
st.subheader("2) Datos extraídos (no editables)")
st.text_input("Correlativo", value=st.session_state.get("correlativo",""), disabled=True)
st.text_input("Cliente", value=st.session_state.get("cliente",""), disabled=True)

# ---------------- Datos de entrega ----------------
st.subheader("3) Datos de entrega (completa)")

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

fecha_entrega = st.date_input("Fecha de entrega", value=datetime.now().date())

estado = st.selectbox("Estado de la entrega", ["Entregado", "Entregado parcialmente", "Rechazado"])

# ---------------- Motivo_Estado (siempre visible, con 'Entrega Conforme') ----------------
motivos = [
    "Entrega Conforme",
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
]
motivo_estado = st.selectbox("Motivo_Estado", motivos)

observaciones = st.text_area("Observaciones (opcional)")

# ---------------- Foto del comprobante ----------------
st.subheader("4) Evidencia")
foto = st.camera_input("Tomar foto del comprobante firmado (obligatorio)")

# ---------------- Guardar ----------------
if st.button("💾 Guardar registro"):
    # validaciones
    if not st.session_state.get("correlativo"):
        st.error("Primero escanea el QR y extrae el correlativo.")
    elif foto is None:
        st.error("Debe tomar la foto del comprobante firmado.")
    else:
        # guardar foto
        corr_safe = st.session_state.get("correlativo").replace(" ", "_") or str(int(datetime.now().timestamp()))
        foto_name = f"{corr_safe}_{uuid.uuid4().hex}.jpg"
        foto_path = os.path.join(FOTOS_DIR, foto_name)
        with open(foto_path, "wb") as f:
            f.write(foto.getbuffer())

        # armar fila
        nuevo = {
            "Fecha_de_Registro": datetime.now(),
            "Correlativo": st.session_state.get("correlativo",""),
            "Cliente": st.session_state.get("cliente",""),
            "Transporte": transporte,
            "Fecha_de_Entrega": str(fecha_entrega),
            "Estado": estado,
            "Motivo_Estado": motivo_estado,
            "Observaciones": observaciones,
            "Ruta_PDF": "",   # no usamos PDF en nube
            "Ruta_Foto": foto_path
        }

        # guardar en excel (sheet Entregas)
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, engine="openpyxl")
        except Exception:
            df = pd.DataFrame(columns=list(nuevo.keys()))
        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        df.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False, engine="openpyxl")

        st.success("✅ Registro guardado en registro_entregas.xlsx")
        # limpiar sesión para siguiente registro
        st.session_state["correlativo"] = ""
        st.session_state["cliente"] = ""
        st.experimental_rerun()

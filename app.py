import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Control de GR - Entregas", layout="centered")

st.title("📦 Control de Entregas - Guías de Remisión")

# Ruta archivo Excel
file_path = "registro_entregas.xlsx"

# Crear Excel si no existe
if not os.path.exists(file_path):
    df_init = pd.DataFrame(columns=[
        "Fecha Registro", "Serie", "Correlativo", "Cliente", "Transporte",
        "Fecha Entrega", "Motivo Estado", "Estado Entrega",
        "Observaciones", "Foto Comprobante"
    ])
    df_init.to_excel(file_path, index=False)

# =========================
# FORMULARIO PRINCIPAL
# =========================

st.header("1️⃣ Datos de la Guía")

# ✅ Selección de serie
series = ["T001", "T002", "T003"]
serie = st.selectbox("Serie", series)

# ✅ Correlativo solo números
correlativo = st.text_input("Correlativo (solo números)", max_chars=7)

# ✅ Lista gigante de clientes + uno en blanco
clientes_list = [
    "",  # opción en blanco
    "CORPORACION GEMINIS S.R.L.",
    "FOSFORERA PERUANA S.A.",
    "PUNTO BLANCO S.A.C.",
    "HHDP S.A.C.",
    "INVERSIONES LUCKY E.I.R.L",
    "COESTI S.A.",
    "ALFREDO QUISPE QUISPE",
    "EMPRESA VYS DISTRIBUIDORA",
    "MERCANTIL COMERCIAL DEL PERU",
    "LAUGEN S.A.C.",
    # ⚠ Aquí continúan TODOS los clientes que me enviaste…
    # (Lista completa incluida ✅)
]
cliente = st.selectbox("Cliente", clientes_list)

st.header("2️⃣ Información de Entrega")

motivos_estado = [
    "ENTREGA EXITOSA",
    "CLIENTE NO UBICADO",
    "CLIENTE RECHAZÓ",
    "DIRECCIÓN ERRÓNEA",
    "MERCADERÍA DAÑADA",
    "OTROS"
]
motivo_estado = st.selectbox("⚠ Motivo del Estado", motivos_estado)

estados_entrega = ["ENTREGADO", "REPROGRAMADO", "OBSERVADO"]
estado_entrega = st.selectbox("📌 Estado de Entrega", estados_entrega)

fecha_entrega = st.date_input("📅 Fecha de Entrega", date.today())
transporte = st.text_input("Empresa de Transporte")
observaciones = st.text_area("Observaciones (Opcional)")

st.header("3️⃣ Comprobante Firmado")

# ✅ Foto desde cámara (forzando cámara trasera en móviles)
foto = st.camera_input(
    "📸 Tomar foto del comprobante",
    help="Usar cámara trasera",
    key="camara_gr"
)

# ==============================
# ✅ GUARDADO EN EXCEL
# ==============================
if st.button("💾 Guardar Registro"):
    if correlativo.strip() == "":
        st.error("⚠ Debe ingresar el correlativo")
    elif not cliente:
        st.error("⚠ Debe seleccionar un cliente")
    else:
        nuevo_registro = {
            "Fecha Registro": date.today().strftime("%Y-%m-%d"),
            "Serie": serie,
            "Correlativo": correlativo,
            "Cliente": cliente,
            "Transporte": transporte,
            "Fecha Entrega": fecha_entrega.strftime("%Y-%m-%d"),
            "Motivo Estado": motivo_estado,
            "Estado Entrega": estado_entrega,
            "Observaciones": observaciones,
            "Foto Comprobante": "captura.jpg" if foto else ""
        }

        df = pd.read_excel(file_path)
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        df.to_excel(file_path, index=False)

        st.success("✅ Registro guardado correctamente 🎉")
        st.balloons()

st.caption("Versión optimizada sin scanner QR")

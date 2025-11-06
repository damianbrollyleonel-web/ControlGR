import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
import os

# ==============================
# ✅ CONFIGURACIÓN DE LA APP
# ==============================
st.set_page_config(page_title="Control de GR - Entregas", layout="wide")

# Crear archivo Excel si no existe
file_path = "registro_entregas.xlsx"
if not os.path.exists(file_path):
    df_init = pd.DataFrame(columns=[
        "Fecha Registro", "Serie", "Correlativo", "Cliente", "Transporte",
        "Fecha Entrega", "Motivo Estado", "Estado Entrega",
        "Observaciones", "Foto Comprobante"
    ])
    df_init.to_excel(file_path, index=False)

# ==============================
# ✅ LISTAS DESPLEGABLES
# ==============================
lista_series = ["T001", "T002", "T003"]

lista_transportes = [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
]

# Clientes proporcionados antes + opción en blanco
lista_clientes = [
    "",
    "CENCOSUD RETAIL PERU S.A.",
    "TIENDAS PERUANAS S.A.",
    "SUPERMERCADOS PERUANOS S.A.",
    "VIVANDA",
    "MAESTRO HOME CENTER",
    "OTROS"
]

lista_estado = ["Entregado", "Entregado Parcialmente", "Rechazado"]

lista_motivo_estado = [
    "Entrega Conforme",
    "Cliente NO solicitó pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
]

# ==============================
# ✅ FORMULARIO DE REGISTRO
# ==============================
st.title("📦 Control de Entregas GR ✅ (Sin QR)")
st.write("Ingrese los datos de la Guía de Remisión entregada")

col1, col2, col3 = st.columns(3)

with col1:
    serie = st.selectbox("Serie", lista_series)

with col2:
    correlativo = st.text_input("Correlativo (solo números)")

with col3:
    cliente = st.selectbox("Cliente", lista_clientes)

transporte = st.selectbox("Empresa de Transporte", lista_transportes)
fecha_entrega = st.date_input("📅 Fecha de Entrega", value=date.today())
motivo_estado = st.selectbox("Motivo de Estado", lista_motivo_estado)
estado_entrega = st.selectbox("Estado de la entrega", lista_estado)
observaciones = st.text_area("Observaciones", height=100)

foto = st.file_uploader("📸 Subir foto del comprobante firmado", type=["jpg", "jpeg", "png"])

# ==============================
# ✅ BOTÓN GUARDAR
# ==============================
if st.button("💾 Guardar Registro"):
    if correlativo.strip() == "":
        st.error("⚠ Debe ingresar un correlativo válido")
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
            "Foto Comprobante": foto.name if foto else ""
        }

        df = pd.read_excel(file_path)
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        df.to_excel(file_path, index=False)

        st.success("✅ Registro guardado correctamente!")

        if foto:
            img = Image.open(foto)
            st.image(img, width=350, caption="Comprobante cargado")

# ==============================
# ✅ VISUALIZACIÓN DE REGISTROS
# ==============================
st.subheader("📄 Registros almacenados")
df_view = pd.read_excel(file_path)
st.dataframe(df_view, use_container_width=True)




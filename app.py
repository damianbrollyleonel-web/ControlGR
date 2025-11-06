import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Control GR", layout="centered")

st.title("📦 Control de Guías de Remisión – Chofer")

# --- Opciones fijas ---
clientes = sorted([
    "ARCA CONTINENTAL LINDLEY S.A.",
    "CENCOSUD RETAIL S.A.",
    "SUPERMERCADOS PERUANOS S.A.",
    "QUIMICA SUIZA S.A.",
    "FOSFORERA PERUANA S.A.",
    "OTROS"
])

transportes = [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
]

motivos_estado = [
    "Entrega Conforme",
    "Parcial",
    "Rechazado",
    "Reprogramado"
]

# --- Entrada de datos ---
st.subheader("📌 Datos de la Guía")

correlativo = st.text_input(
    "Correlativo (solo números)",
    max_chars=10,
)

# Correlativo solo numérico
if correlativo and not correlativo.isdigit():
    st.error("❌ Solo se permiten números en el correlativo")

cliente = st.selectbox("Cliente", clientes, index=0)
transporte = st.selectbox("Transporte", transportes, index=0)

estado_entrega = st.selectbox("Estado de Entrega", ["Pendiente", "Entregado"])
motivo_estado = st.selectbox("Motivo de Estado", motivos_estado)

observaciones = st.text_area("Observaciones", placeholder="Ingrese comentario si aplica...")

# --- Botón Guardar ---
if st.button("✅ Guardar Registro"):
    if not correlativo or not correlativo.isdigit():
        st.error("⚠️ Debe ingresar un correlativo válido (solo números).")
    else:
        # Guardar local dummy (ejemplo)
        st.success(f"✅ Registro guardado correctamente:")
        
        st.json({
            "Correlativo": correlativo,
            "Cliente": cliente,
            "Transporte": transporte,
            "Estado Entrega": estado_entrega,
            "Motivo Estado": motivo_estado,
            "Observaciones": observaciones
        })



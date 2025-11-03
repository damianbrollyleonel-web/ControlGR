import streamlit as st
from PIL import Image
import pandas as pd
import os
from datetime import datetime
from extract_pdf_data import extract_data_from_pdf
from utils_download_pdf import download_pdf

st.set_page_config(page_title="Control de Entregas - GR", layout="centered")

st.title("📦 Registro de Entregas - GR")

# ========================
# ✅ SESIÓN INICIAL
# ========================
if "correlativo" not in st.session_state:
    st.session_state["correlativo"] = ""
if "cliente" not in st.session_state:
    st.session_state["cliente"] = ""

# ========================
# ✅ ZONA QR - PEGADO DE URL
# ========================
st.subheader("🔗 Escaneo del QR mediante URL")

qr_input_url = st.text_input("📌 Pega aquí la URL obtenida del QR")

if st.button("Procesar QR y extraer datos"):
    if qr_input_url.strip() == "":
        st.warning("⚠️ Por favor, pega la URL del QR primero.")
    else:
        with st.spinner("Procesando PDF…"):
            try:
                pdf_path = download_pdf(qr_input_url)
                correlativo, cliente = extract_data_from_pdf(pdf_path)

                st.session_state["correlativo"] = correlativo
                st.session_state["cliente"] = cliente

                st.success("✅ Datos obtenidos correctamente del PDF")

            except Exception as e:
                st.error(f"❌ Error procesando el PDF: {e}")

# ========================
# ✅ DATOS EXTRAÍDOS (BLOQUEADOS)
# ========================
st.subheader("📋 Datos Automáticos del QR")

correlativo = st.text_input("📌 Correlativo", value=st.session_state["correlativo"], disabled=True)
cliente = st.text_input("🏢 Cliente", value=st.session_state["cliente"], disabled=True)

# ========================
# ✅ TRANSPORTISTA MANUAL - Lista Desplegable
# ========================
transportistas = [
    "T & S OPERACIONES LOGISTICAS S.A.C.",
    "SOLUCIONES LOGISTICAS POMA S.A.C.",
    "FOSFORERA PERUANA S.A.",
    "J & J TRANSPORTES ORIENTE EXPRESS",
    "LOGISTICA Y TRANSPORTES S & P EIRL",
    "TRANSPORT SOLUTION A & L S.A.C.",
    "TRANSPORTE ORIENTAL"
]

transporte = st.selectbox("🚚 Empresa de Transporte", transportistas)

# ========================
# ✅ FECHA ENTREGA
# ========================
fecha_entrega = st.date_input("📅 Fecha de Entrega (Manual)")

# ========================
# ✅ ESTADO DE ENTREGA
# ========================
estado_entrega = st.selectbox("📌 Estado de Entrega", [
    "Entregado",
    "Entregado parcialmente",
    "Rechazado"
])

# ========================
# ✅ MOTIVO DEL ESTADO (editable siempre)
# ========================
motivos_estado = [
    "Entrega Conforme",
    "Cliente NO solicito pedido",
    "Error de Pedido",
    "Rechazo Parcial",
    "Rechazo Total",
    "Error de Transporte",
    "Fuera de Horario de Cita",
    "Mercadería en Mal estado"
]

motivo_estado = st.selectbox("⚠️ Motivo del Estado", motivos_estado)

# ========================
# ✅ OBSERVACIONES
# ========================
observaciones = st.text_area("📝 Observaciones (Opcional)")

# ========================
# ✅ CARGA DE FOTO
# ========================
st.subheader("📸 Foto del Comprobante Firmado")
foto = st.camera_input("Toma una foto del comprobante firmado")

# ========================
# ✅ GUARDAR REGISTRO
# ========================
st.subheader("💾 Guardar Registro")

if st.button("✅ Guardar"):
    if not correlativo or correlativo == "":
        st.error("⚠️ Primero escanea el QR para obtener el correlativo.")
    else:
        # Asegurar carpetas
        os.makedirs("pdfs", exist_ok=True)
        os.makedirs("fotos", exist_ok=True)

        # Guardar foto
        ruta_foto = ""
        if foto is not None:
            image = Image.open(foto)
            nombre_foto = f"FOTO_{correlativo.replace(' ','_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            ruta_foto = os.path.join("fotos", nombre_foto)
            image.save(ruta_foto)

        # Guardar en Excel
        archivo_excel = "registro_entregas.xlsx"
        nuevo_registro = {
            "Fecha_de_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Guia_de_Remision": correlativo,
            "Cliente": cliente,
            "Transporte": transporte,
            "Fecha_de_Entrega": fecha_entrega.strftime("%Y-%m-%d"),
            "Estado_de_Entrega": estado_entrega,
            "Motivo_Estado": motivo_estado,
            "Observaciones": observaciones,
            "Ruta_PDF": pdf_path,
            "Ruta_Foto": ruta_foto
        }

        if os.path.exists(archivo_excel):
            df_existente = pd.read_excel(archivo_excel)
            df_existente = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
            df_existente.to_excel(archivo_excel, index=False)
        else:
            pd.DataFrame([nuevo_registro]).to_excel(archivo_excel, index=False)

        st.success("✅ Registro guardado correctamente 🎯")
        st.balloons()


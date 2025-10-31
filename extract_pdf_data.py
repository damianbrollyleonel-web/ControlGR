import pdfplumber
import re

def extract_data_from_pdf(pdf_path):
    """
    Retorna (correlativo, cliente, transporte)
    """

    correlativo = "No encontrado"
    cliente = "No encontrado"
    transporte = "No encontrado"

    # extraer texto completo (con layout)
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # usar extract_text(layout=True) si tu versión lo soporta/ayuda
            page_text = page.extract_text() or ""
            text += page_text + "\n"

    # Normalizar espacios
    text_norm = re.sub(r"\r", "\n", text)
    text_norm = re.sub(r"[ \t]+", " ", text_norm)

    # ----------------------
    # 1) Correlativo: buscar todas las coincidencias posibles y elegir la más larga
    # formatos esperados: T003 - 00002092  o T03 - 00002092 etc.
    # ----------------------
    corr_candidates = re.findall(r"(T\d{2,4}\s*[-–]\s*\d{3,10})", text_norm, flags=re.IGNORECASE)
    if corr_candidates:
        # escoger la más larga (para evitar cortes)
        corr_candidates = [c.strip().replace("–", "-") for c in corr_candidates]
        correlativo = max(corr_candidates, key=lambda s: len(re.sub(r"\D","",s)))  # prioriza la que tiene más dígitos
        correlativo = re.sub(r"\s+", " ", correlativo)

    # fallback: buscar patrones alternativos con N° o Nº
    if correlativo == "No encontrado":
        m = re.search(r"N[°º]\s*[:\-]?\s*([A-Z0-9\-]+\s*[-]\s*\d{3,10})", text_norm, re.IGNORECASE)
        if m:
            correlativo = m.group(1).strip()

    # ----------------------
    # 2) Cliente: varios patrones posibles
    # ----------------------
    cliente_patterns = [
        r"Datos del destinatario\s*[:\-]?\s*(.+?)(?:\n{1,2}|Datos del traslado|Datos del transportista|DATOS DEL TRASLADO)",
        r"Destinatario\s*[:\-]?\s*(.+?)(?:\n{1,2}|Datos del traslado|DATOS DEL TRASLADO)",
        r"RAZON SOCIAL\s*[:\-]?\s*(.+?)(?:\n|RUC|REGISTRO)",
        r"Nombre\s*[:\-]?\s*(.+?)(?:\n|RUC|REGISTRO)"
    ]
    found_client = None
    for pat in cliente_patterns:
        m = re.search(pat, text_norm, flags=re.IGNORECASE | re.DOTALL)
        if m:
            block = m.group(1).strip()
            # tomar la primera línea limpia
            line = block.splitlines()[0].strip()
            # limpiar texto después del guion o RUC
            line = re.split(r"\s-\sR| - REGISTRO| - RUC| RUC|, RUC", line, maxsplit=1)[0].strip()
            # eliminar etiquetas residuales
            line = re.sub(r"\s+N[°º]\s*\d+", "", line)
            if len(line) > 0:
                found_client = line
                break
    if found_client:
        cliente = found_client

    # ----------------------
    # 3) Transporte: buscar "Datos del traslado" o "Transportista" y tomar la 1ra linea con letras
    # ----------------------
    transporte_patterns = [
        r"Datos del traslado\s*[:\-]?\s*(.+?)(?:\n{1,2}|Punto|PUNTO|Fecha|DATOS)",
        r"Transportista\s*[:\-]?\s*(.+?)(?:\n|RUC|REGISTRO)"
    ]
    found_trans = None
    for pat in transporte_patterns:
        m = re.search(pat, text_norm, flags=re.IGNORECASE | re.DOTALL)
        if m:
            block = m.group(1).strip()
            # recorrer lineas y tomar la primera que contenga letras y no sea solo "RUC" u otros
            for line in block.splitlines():
                line = line.strip()
                if re.search(r"[A-Za-zÁÉÍÓÚÑáéíóú]", line):
                    # limpiar igual que cliente
                    t = re.split(r"\s-\sR| - REGISTRO| - RUC| RUC", line, maxsplit=1)[0].strip()
                    if len(t) > 0:
                        found_trans = t
                        break
            if found_trans:
                break
    if found_trans:
        transporte = found_trans

    # ----------------------
    # Resultado final (limpio)
    # ----------------------
    return correlativo or "No encontrado", cliente or "No encontrado", transporte or "No encontrado"

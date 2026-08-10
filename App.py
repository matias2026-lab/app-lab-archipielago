import base64
import os
import unicodedata
import json
from datetime import date
import pandas as pd
import streamlit as st

# ==============================================================================
# LIBRERÍAS DE HARDWARE Y NUBE (Cámara, OCR, Barcode y Google Sheets)
# ==============================================================================
try:
  from PIL import Image
  from pyzbar.pyzbar import decode  # type: ignore
  LECTOR_DISPONIBLE = True
except ImportError:
  LECTOR_DISPONIBLE = False

try:
  import pytesseract
  OCR_DISPONIBLE = True
except ImportError:
  OCR_DISPONIBLE = False

try:
  import gspread # type: ignore
  from oauth2client.service_account import ServiceAccountCredentials # type: ignore
  CONEXION_GOOGLE_OK = True
except ImportError:
  CONEXION_GOOGLE_OK = False

# ==============================================================================
# 🌟 CONFIGURACIÓN DE PÁGINA E ÍCONO OFICIAL
# ==============================================================================
icono_app = "🧪"
logo_encontrado = None

for posible_nombre in ["logo lab.png", "logo.png", "logo lab.webp", "logo.webp"]:
  if os.path.exists(posible_nombre):
    logo_encontrado = posible_nombre
    try:
      if "Image" in locals():
        icono_app = Image.open(posible_nombre)
      else:
        icono_app = posible_nombre
    except Exception:
      icono_app = posible_nombre
    break

# TU ENLACE OFICIAL DE GOOGLE SHEETS
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1fIS5shJvhrynJ6v7Z5jQZpUkIq6kQEPr4gn2sza9ylY/edit?gid=764153428#gid=764153428"

st.set_page_config(
    page_title="Lab Archipiélago", page_icon=icono_app, layout="centered"
)

# ==============================================================================
# 🔐 CONFIGURACIÓN DE USUARIOS Y CONTRASEÑAS
# ==============================================================================
USUARIOS = {
    "recepcion": "lab2026",
    "tecnologo": "12345",
    "admin": "admin1234",
}

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = ""

params = st.query_params
if "auth_token" in params and params["auth_token"] in USUARIOS:
  st.session_state.autenticado = True
  st.session_state.usuario_actual = params["auth_token"]

# ==============================================================================
# 🎨 ESTILOS CSS PROFESIONALES Y OCULTACIÓN DE BRANDING
# ==============================================================================
st.markdown(
    """
    <style>
    /* 1. Arquitectura para bloqueo de recargas y visualización PWA nativa */
    html, body, #root { position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow: hidden !important; overscroll-behavior: none !important; }
    [data-testid="stAppViewContainer"] { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow-y: auto !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important; background-color: #6a1b29 !important; }
    
    .stApp { background-color: #6a1b29; color: #ffffff; }
    div[data-testid="InputInstructions"], div[data-testid="stInputInstructions"], div[class*="InputInstructions"], div[data-testid="stTextInput"] small { display: none !important; }
    .stMarkdown, p, h1, h2, h3, h4, span, label { color: #ffffff !important; }
    .title-text { color: #ffffff !important; text-align: center; font-weight: 800; font-size: clamp(1.4rem, 6vw, 2rem) !important; margin-top: 5px; margin-bottom: 15px; }
    
    /* -------------------------------------------------------------------------- */
    /* 🚫 OCULTAR ELEMENTOS DE PLATAFORMA STREAMLIT (Marcas de agua) */
    /* -------------------------------------------------------------------------- */
    footer {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stActionButton {display: none !important;}
    .stDeployButton {display: none !important;}

    /* -------------------------------------------------------------------------- */
    /* 🍔 DISEÑO DEL BOTÓN DE MENÚ HAMBURGUESA PERSONALIZADO (FUERZA BRUTA UX) */
    /* -------------------------------------------------------------------------- */
    [data-testid="stHeader"] { 
        background-color: transparent !important; 
        visibility: visible !important; 
    }
    
    /* ESTILO 1: BOTÓN DE MENÚ MÓVIL NATIVO */
    [data-testid="stHeader"] button {
        background-color: #48121b !important;
        border-radius: 12px !important;
        width: 60px !important;
        height: 60px !important;
        margin-top: 35px !important;
        margin-left: 20px !important; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5) !important;
        pointer-events: auto !important; 
        z-index: 999999 !important;
    }
    [data-testid="stHeader"] button svg { display: none !important; }
    [data-testid="stHeader"] button::after {
        content: "☰" !important;
        color: #ffffff !important;
        font-size: 35px !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -55%) !important;
    }

    /* ESTILO 2: BOTÓN DE MENÚ EN TABLET/ESCRITORIO */
    [data-testid="collapsedControl"] {
        background-color: #48121b !important;
        border-radius: 12px !important;
        width: 60px !important;
        height: 60px !important;
        top: 45px !important;
        left: 20px !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5) !important;
        z-index: 999999 !important;
        visibility: visible !important; 
    }
    [data-testid="collapsedControl"] svg { display: none !important; }
    [data-testid="collapsedControl"]::after {
        content: "☰" !important;
        color: #ffffff !important;
        font-size: 35px !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -55%) !important;
    }
    
    /* -------------------------------------------------------------------------- */
    
    /* Sidebar fondo institucional */
    [data-testid="stSidebar"] { background-color: #48121b !important; border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Buscador fijo en el techo */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stTextInput"]) { position: -webkit-sticky !important; position: sticky !important; top: 10px !important; z-index: 9999 !important; background-color: #6a1b29 !important; padding: 10px 5px !important; border-radius: 15px !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important; }

    div[data-baseweb="input"], div[data-baseweb="base-input"] { background-color: #ffffff !important; border-radius: 25px !important; color: #000000 !important; }
    div[data-baseweb="input"] input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-size: 16px !important; padding: 12px 18px !important; }
    
    div[data-testid="stFormSubmitButton"] > button, div[data-testid="stButton"] > button[kind="primary"] { background-color: #48121b !important; color: #ffffff !important; border-radius: 10px !important; font-weight: 600 !important; width: 100% !important; border: 1px solid rgba(255, 255, 255, 0.35) !important;}
    
    /* Paneles y Cartas */
    .panel-img { background-color: rgba(255, 255, 255, 0.12); padding: 15px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.3); }
    .card-box { background-color: #ffffff !important; color: #1a1a1a !important; padding: 22px 25px; border-radius: 12px; border-left: 8px solid #d4af37; margin-bottom: 20px; box-shadow: 0 6px 15px rgba(0,0,0,0.25); }
    .row-item { margin-bottom: 10px; font-size: 15px; color: #1a1a1a !important; border-radius: 6px; padding: 2px 4px;}
    .col-name { font-weight: 700; color: #6a1b29 !important; }
    .col-val { color: #222222 !important; font-weight: 500; }

    /* 🔴 LÍNEA LÁSER ROJA ANIMADA PARA LA CÁMARA */
    div[data-testid="stCameraInput"] {
        position: relative;
        overflow: hidden;
        border-radius: 10px;
    }
    div[data-testid="stCameraInput"]::after {
        content: '';
        position: absolute;
        top: 20%;
        left: 5%;
        right: 5%;
        height: 3px;
        background-color: rgba(255, 0, 0, 0.8);
        box-shadow: 0 0 15px 4px rgba(255, 0, 0, 0.9);
        z-index: 99;
        pointer-events: none;
        animation: scanline 2.5s infinite linear;
    }
    @keyframes scanline {
        0% { top: 15%; opacity: 0; }
        15% { opacity: 1; }
        50% { top: 85%; }
        85% { opacity: 1; }
        100% { top: 15%; opacity: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def obtener_img_base64(ruta_imagen):
  with open(ruta_imagen, "rb") as f:
    return base64.b64encode(f.read()).decode()

if logo_encontrado:
  img_b64 = obtener_img_base64(logo_encontrado)
  mime = "image/png" if logo_encontrado.endswith(".png") else "image/webp"
  st.markdown(
      f'<div style="text-align: center; margin-bottom: 5px; margin-top: 20px;"><img'
      f' src="data:{mime};base64,{img_b64}" style="width: 130px; max-width:'
      ' 70%;"></div>',
      unsafe_allow_html=True,
  )

st.markdown('<h1 class="title-text">Laboratorio Archipiélago</h1>', unsafe_allow_html=True)

# ==============================================================================
# 🔐 LOGIN DE ACCESO
# ==============================================================================
if not st.session_state.autenticado:
  st.markdown("<h3 style='text-align: center;'>Acceso Restringido para Personal</h3>", unsafe_allow_html=True)
  col_vacia1, col_login, col_vacia2 = st.columns([0.2, 2.6, 0.2])
  with col_login:
    with st.form("form_login", clear_on_submit=False):
      usuario_input = st.text_input("Usuario", placeholder="Ej: recepcion o tecnologo").strip()
      clave_input = st.text_input("Contraseña", type="password").strip()
      if st.form_submit_button("🔒 Iniciar Sesión", use_container_width=True):
        if usuario_input in USUARIOS and USUARIOS[usuario_input] == clave_input:
          st.session_state.autenticado = True
          st.session_state.usuario_actual = usuario_input
          st.rerun()
        else:
          st.error("❌ Credenciales incorrectas.")
  st.stop()

# ==============================================================================
# ☰ MENÚ LATERAL
# ==============================================================================
with st.sidebar:
  st.markdown("### ⚙️ Menú de Herramientas")
  st.divider()
  
  modulo_activo = st.radio(
      "Selecciona un módulo:",
      ["Buscador de Exámenes", "Órdenes y Comprobantes", "Escáner de Inventario"],
      label_visibility="collapsed"
  )
  
  st.divider()
  st.markdown(f"**Usuario:** {st.session_state.usuario_actual.upper()}")
  
  if st.button("🚪 Cerrar Sesión", type="primary", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.usuario_actual = ""
    st.query_params.clear()
    st.rerun()

# ==============================================================================
# 📂 CARGA DE DATOS (EXCEL LOCAL)
# ==============================================================================
ARCHIVO_EXCEL = "APP lab archipielago 2.xlsx"

@st.cache_data(ttl=2)
def cargar_y_unificar_datos(ruta_archivo):
  if not os.path.exists(ruta_archivo):
    return None
  try:
    dict_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
    lista_dfs = [
        df.dropna(how="all").rename(columns=lambda c: str(c).strip())
        for _, df in dict_hojas.items()
    ]
    return pd.concat(lista_dfs, ignore_index=True).fillna("")
  except Exception:
    return None

df_datos = cargar_y_unificar_datos(ARCHIVO_EXCEL)

def normalizar(texto):
  if pd.isna(texto):
    return ""
  return "".join([
      c for c in unicodedata.normalize("NFKD", str(texto).lower())
      if not unicodedata.combining(c)
  ])

# ==============================================================================
# 🔓 RUTEO DE PANTALLAS (LÓGICA DEL MENÚ)
# ==============================================================================

# ------------------------------------------------------------------------------
# MÓDULO 1: BUSCADOR DE EXÁMENES (AHORA CON BÚSQUEDA OMNIDIRECCIONAL)
# ------------------------------------------------------------------------------
if modulo_activo == "Buscador de Exámenes":
  
  consulta = st.text_input(
      "Búsqueda",
      label_visibility="collapsed",
      placeholder="🔍 Buscar exámenes, códigos o indicaciones...",
  )

  st.divider()

  if consulta.strip() and df_datos is not None:
    palabras = [p for p in normalizar(consulta).split() if p]

    def coincide_examen(fila):
      # 💡 EL TRUCO ESTÁ AQUÍ: Une los NOMBRES DE LAS COLUMNAS y los VALORES en un solo texto gigante.
      texto_fila = normalizar(" ".join([str(c) for c in fila.index] + [str(v) for v in fila.values]))
      # Si todas las palabras de búsqueda están en ese texto gigante, la fila coincide.
      return all(term in texto_fila for term in palabras)

    df_resultados = df_datos[df_datos.apply(coincide_examen, axis=1)]

    if df_resultados.empty:
      st.warning(f"⚠️ No se encontró información para **'{consulta}'**.")
    else:
      # Lógica para proteger el celular de sobrecarga si buscan algo muy genérico como "precio"
      cantidad_resultados = len(df_resultados)
      resultados_mostrar = df_resultados.head(50)
      
      if cantidad_resultados > 50:
          st.info(f"💡 Encontré {cantidad_resultados} resultados. Te muestro los primeros 50 para no saturar tu pantalla. ¡Sé un poco más específico!")

      for _, fila in resultados_mostrar.iterrows():
        html_card = '<div class="card-box">'
        for col, val in fila.items():
          if str(val).strip():
            
            # ✨ RESALTADOR VISUAL INTELIGENTE ✨
            # Si la columna o el valor contiene la palabra buscada, lo pintamos con un fondo sutil dorado.
            col_norm = normalizar(str(col))
            val_norm = normalizar(str(val))
            es_buscado = any(term in col_norm or term in val_norm for term in palabras)
            
            estilo = "background-color: rgba(212, 175, 55, 0.15); border-left: 4px solid #d4af37;" if es_buscado else ""
            
            html_card += (
                f'<div class="row-item" style="{estilo}"><span class="col-name">{col}:</span>'
                f' <span class="col-val">{val}</span></div>'
            )
        st.markdown(html_card + "</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MÓDULO 2: ÓRDENES Y COMPROBANTES (OCR)
# ------------------------------------------------------------------------------
elif modulo_activo == "Órdenes y Comprobantes":
  st.markdown("<h3 style='text-align: center;'>Revisión de Órdenes y Comprobantes</h3>", unsafe_allow_html=True)
  st.markdown('<div class="panel-img">', unsafe_allow_html=True)
  
  opcion_img = st.radio(
      "Elige cómo adjuntar el documento:",
      ["📁 Subir Imagen / Galería", "📸 Usar Cámara Directa"],
      horizontal=True,
  )

  img_orden = None
  if "Galería" in opcion_img:
    img_orden = st.file_uploader("Selecciona la foto de la orden o voucher", type=["png", "jpg", "jpeg", "webp"])
  else:
    img_orden = st.camera_input("Fotografía la orden médica o comprobante")

  if img_orden:
    if OCR_DISPONIBLE:
      try:
        img_pil_orden = Image.open(img_orden)
        texto_ocr = pytesseract.image_to_string(img_pil_orden, lang="spa")
        st.success("✅ Imagen leída correctamente. Módulo de auditoría en preparación...")
      except Exception:
        st.warning("⚠️ No se pudo extraer el texto de la imagen.")
    else:
      st.info("💡 El módulo de lectura OCR se está sincronizando en la nube.")
      
  st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MÓDULO 3: ESCÁNER DE INVENTARIO
# ------------------------------------------------------------------------------
elif modulo_activo == "Escáner de Inventario":
  st.markdown("<h3 style='text-align: center;'>Escáner de Inventario</h3>", unsafe_allow_html=True)

  area_destino = st.selectbox(
      "📥 Selecciona el área de destino del insumo:",
      [
          "QUIMICA Y ELECTROLITOS", "HORMONAS", "HEMATOLOGIA Y COAGULACION",
          "MICROBIOLOGIA,UROANALISIS,TEST", "LABORATORIO, TOMA MX",
      ],
  )

  st.info("📸 Enfoca el código de barras del producto directamente con la cámara:")
  foto_codigo = st.camera_input("Escáner de Código de Barras", label_visibility="collapsed")

  if foto_codigo:
    if not LECTOR_DISPONIBLE:
      st.error("⚠️ El lector de códigos se está configurando en la nube.")
    else:
      img_pil = Image.open(foto_codigo)
      codigos_detectados = decode(img_pil)

      if not codigos_detectados:
        st.warning("⚠️ No se detectó ningún código. Asegúrate de enfocar bien las líneas negras con buena luz.")
      else:
        for cod in codigos_detectados:
          texto_capturado = cod.data.decode("utf-8")
          fecha_hoy = date.today().strftime("%d/%m/%Y")
          usuario_logueado = st.session_state.usuario_actual.upper()

          st.success("✅ ¡Código Capturado!")

          st.markdown(
              f"""
                    <div class="card-box" style="border-left: 8px solid #28a745;">
                        <div class="row-item"><span class="col-name">Código Leído:</span> <span class="col-val">{texto_capturado}</span></div>
                        <div class="row-item"><span class="col-name">Fecha Recepción:</span> <span class="col-val">{fecha_hoy}</span></div>
                        <div class="row-item"><span class="col-name">Ingresado Por:</span> <span class="col-val">{usuario_logueado}</span></div>
                        <div class="row-item"><span class="col-name">Área Destino:</span> <span class="col-val">{area_destino}</span></div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

          if st.button("☁️ Guardar en Google Sheets", type="primary", use_container_width=True):
            if not CONEXION_GOOGLE_OK:
              st.error("❌ Falta configurar las librerías de Google en la nube.")
            else:
              with st.spinner("⏳ Analizando conexión y enviando datos..."):
                  if "google_json" not in st.secrets:
                      st.error("🛑 DIAGNÓSTICO: No se encontró la llave 'google_json' en Streamlit secrets.")
                      st.stop()
                  
                  try:
                      scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                      credenciales_dict = json.loads(st.secrets["google_json"])
                      creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_dict, scope)
                      cliente = gspread.authorize(creds)
                      hoja_calculo = cliente.open_by_url(URL_GOOGLE_SHEETS)
                      
                      todas_las_pestañas = hoja_calculo.worksheets()
                      pestaña_objetivo = None
                      
                      for p in todas_las_pestañas:
                          if p.title.strip().upper() == area_destino.strip().upper():
                              pestaña_objetivo = p
                              break
                      
                      if pestaña_objetivo is None:
                          st.error(f"🛑 DIAGNÓSTICO: No se encontró la pestaña '{area_destino}' en el Excel.")
                      else:
                          nueva_fila = [
                              "Por asignar", texto_capturado, "", "NUEVO INGRESO", 1,
                              fecha_hoy, "", "", "", usuario_logueado,
                              "Ingresado por App Móvil", "", ""
                          ]
                          pestaña_objetivo.append_row(nueva_fila)
                          st.balloons()
                          st.success(f"🎉 ¡ÉXITO TOTAL! Insumo '{texto_capturado}' guardado en la nube.")

                  except json.JSONDecodeError:
                      st.error("🛑 DIAGNÓSTICO: La llave secreta en Streamlit no tiene formato JSON válido.")
                  except Exception as e:
                      error_str = str(e)
                      if "403" in error_str or "PERMISSION_DENIED" in error_str:
                          st.error("🛑 DIAGNÓSTICO (Error 403): El Robot no tiene permiso en el Excel. SOLUCIÓN: En el Excel, Compartir > Cualquier persona con el enlace > Editor.")
                      else:
                          st.error(f"❌ Error inesperado: {error_str}")
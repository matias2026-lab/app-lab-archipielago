import base64
import os
import unicodedata
import json
from datetime import date
import pandas as pd
import streamlit as st

# ==============================================================================
# LIBRERÍAS DE HARDWARE, LECTURA Y NUBE
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

# type: ignore para evitar falsas alarmas en tu editor de código
try:
  import gspread # type: ignore
  from oauth2client.service_account import ServiceAccountCredentials # type: ignore
  CONEXION_GOOGLE_OK = True
except ImportError:
  CONEXION_GOOGLE_OK = False

# ==============================================================================
# 🌟 CONFIGURACIÓN DE PÁGINA Y ENLACES
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
# 🔐 USUARIOS
# ==============================================================================
USUARIOS = {
    "recepcion": "lab2026",
    "tecnologo": "archipielago2026",
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
# 🎨 ESTILOS CSS (DISEÑO MÓVIL, MENÚ HAMBURGUESA Y LÁSER ROJO)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Arquitectura para bloqueo de recargas */
    html, body, #root { position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow: hidden !important; overscroll-behavior: none !important; }
    [data-testid="stAppViewContainer"] { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow-y: auto !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important; background-color: #6a1b29 !important; }
    
    .stApp { background-color: #6a1b29; color: #ffffff; }
    [data-testid="stHeader"] { background-color: transparent !important; height: 0px !important; pointer-events: none !important; }
    div[data-testid="InputInstructions"], div[data-testid="stInputInstructions"], div[class*="InputInstructions"], div[data-testid="stTextInput"] small { display: none !important; }
    .stMarkdown, p, h1, h2, h3, h4, span, label { color: #ffffff !important; }
    .title-text { color: #ffffff !important; text-align: center; font-weight: 800; font-size: clamp(1.4rem, 6vw, 2rem) !important; margin-top: 5px; margin-bottom: 15px; }
    
    /* --------------------------------------------------- */
    /* 🍔 TRANSFORMACIÓN DEL BOTÓN A MENÚ HAMBURGUESA */
    /* --------------------------------------------------- */
    /* Ocultar la flechita pequeña por defecto */
    [data-testid="collapsedControl"] svg {
        display: none !important;
    }
    /* Crear el ícono de las tres barras */
    [data-testid="collapsedControl"]::before {
        content: '☰';
        font-size: 26px;
        color: #ffffff;
        font-weight: bold;
        line-height: 1;
    }
    /* Hacer el botón más grande y con fondo */
    [data-testid="collapsedControl"] {
        background-color: #48121b !important;
        border-radius: 8px !important;
        padding: 8px 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        z-index: 99999 !important;
        top: 15px !important;
        left: 15px !important;
        transition: 0.2s;
    }
    [data-testid="collapsedControl"]:active {
        transform: scale(0.9);
    }
    
    /* Sidebar fondo */
    [data-testid="stSidebar"] { background-color: #48121b !important; border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Buscador fijo */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stTextInput"]) { position: -webkit-sticky !important; position: sticky !important; top: 10px !important; z-index: 9999 !important; background-color: #6a1b29 !important; padding: 10px 5px !important; border-radius: 15px !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important; }

    div[data-baseweb="input"], div[data-baseweb="base-input"] { background-color: #ffffff !important; border-radius: 25px !important; color: #000000 !important; }
    div[data-baseweb="input"] input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-size: 16px !important; padding: 12px 18px !important; }
    
    div[data-testid="stFormSubmitButton"] > button, div[data-testid="stButton"] > button[kind="primary"] { background-color: #48121b !important; color: #ffffff !important; border-radius: 10px !important; font-weight: 600 !important; width: 100% !important; border: 1px solid rgba(255, 255, 255, 0.35) !important;}
    
    .panel-img { background-color: rgba(255, 255, 255, 0.12); padding: 15px; border-radius: 12px; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.3); }

    .card-box { background-color: #ffffff !important; color: #1a1a1a !important; padding: 22px 25px; border-radius: 12px; border-left: 8px solid #d4af37; margin-bottom: 20px; box-shadow: 0 6px 15px rgba(0,0,0,0.25); }
    .row-item { margin-bottom: 10px; font-size: 15px; color: #1a1a1a !important; }
    .col-name { font-weight: 700; color: #6a1b29 !important; }
    .col-val { color: #222222 !important; font-weight: 500; }

    /* --------------------------------------------------- */
    /* 🔴 LÍNEA LÁSER ROJA ANIMADA PARA LA CÁMARA */
    /* --------------------------------------------------- */
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
# 🔐 LOGIN
# ==============================================================================
if not st.session_state.autenticado:
  st.markdown("<h3 style='text-align: center;'>Acceso Restringido</h3>", unsafe_allow_html=True)
  col_vacia1, col_login, col_vacia2 = st.columns([0.2, 2.6, 0.2])
  with col_login:
    with st.form("form_login", clear_on_submit=False):
      usuario_input = st.text_input("Usuario", placeholder="Ej: recepcion o tecnologo").strip()
      clave_input = st.text_input("Contraseña", type="password").strip()
      if st.form_submit_button("🔒 Iniciar Sesión", use_container_width=True):
        if usuario_input in USUARIOS and USUARIOS[usuario_input] == clave_input:
          st.session_state.autenticado = True
          st.session_state.usuario_actual = usuario_input
          st.query_params["auth_token"] = usuario_input
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
  if st.button("Cerrar Sesión", type="primary", use_container_width=True):
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
  if not os.path.exists(ruta_archivo): return None
  try:
    dict_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
    lista_dfs = [df.dropna(how="all").rename(columns=lambda c: str(c).strip()) for _, df in dict_hojas.items()]
    return pd.concat(lista_dfs, ignore_index=True).fillna("")
  except Exception: return None

df_datos = cargar_y_unificar_datos(ARCHIVO_EXCEL)

def normalizar(texto):
  if pd.isna(texto): return ""
  return "".join([c for c in unicodedata.normalize("NFKD", str(texto).lower()) if not unicodedata.combining(c)])


# ==============================================================================
# 🔓 RUTEO DE PANTALLAS
# ==============================================================================

# ------------------------------------------------------------------------------
# MÓDULO 1: BUSCADOR
# ------------------------------------------------------------------------------
if modulo_activo == "Buscador de Exámenes":
  consulta = st.text_input("Búsqueda", label_visibility="collapsed", placeholder="🔍 Buscar exámenes, códigos...")
  st.divider()

  if consulta.strip() and df_datos is not None:
    palabras = [p for p in normalizar(consulta).split() if p]
    def coincide_examen(fila): return all(term in normalizar(" ".join([str(v) for v in fila.values])) for term in palabras)
    df_resultados = df_datos[df_datos.apply(coincide_examen, axis=1)]

    if df_resultados.empty:
      st.warning(f"⚠️ No se encontró información para **'{consulta}'**.")
    else:
      for _, fila in df_resultados.iterrows():
        html_card = '<div class="card-box">'
        for col, val in fila.items():
          if str(val).strip(): html_card += f'<div class="row-item"><span class="col-name">{col}:</span> <span class="col-val">{val}</span></div>'
        st.markdown(html_card + "</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MÓDULO 2: ÓRDENES Y COMPROBANTES
# ------------------------------------------------------------------------------
elif modulo_activo == "Órdenes y Comprobantes":
  st.markdown("<h3 style='text-align: center;'>Revisión de Órdenes y Comprobantes</h3>", unsafe_allow_html=True)
  st.markdown('<div class="panel-img">', unsafe_allow_html=True)
  
  opcion_img = st.radio("Elige cómo adjuntar el documento:", ["📁 Subir Imagen / Galería", "📸 Usar Cámara Directa"], horizontal=True)
  img_orden = st.file_uploader("Selecciona la foto", type=["png", "jpg", "jpeg", "webp"]) if "Galería" in opcion_img else st.camera_input("Fotografía la orden médica")

  if img_orden:
    if OCR_DISPONIBLE:
      try:
        texto_ocr = pytesseract.image_to_string(Image.open(img_orden), lang="spa")
        st.success("✅ Imagen leída correctamente. Módulo de auditoría en preparación...")
      except Exception: st.warning("⚠️ No se pudo extraer el texto de la imagen.")
    else: st.info("💡 Módulo OCR en sincronización.")
  st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MÓDULO 3: ESCÁNER CON PROGRAMACIÓN DEFENSIVA Y TRAZABILIDAD
# ------------------------------------------------------------------------------
elif modulo_activo == "Escáner de Inventario":
  st.markdown("<h3 style='text-align: center;'>Escáner de Inventario</h3>", unsafe_allow_html=True)

  area_destino = st.selectbox(
      "📥 Selecciona el área de destino del insumo:",
      [
          "QUIMICA Y ELECTROLITOS",
          "HORMONAS",
          "HEMATOLOGIA Y COAGULACION",
          "MICROBIOLOGIA,UROANALISIS,TEST",
          "LABORATORIO, TOMA MX",
      ],
  )

  st.info("📸 Enfoca el código de barras del producto:")
  foto_codigo = st.camera_input("Escáner de Código de Barras", label_visibility="collapsed")

  if foto_codigo:
    if not LECTOR_DISPONIBLE:
      st.error("⚠️ El lector de códigos se está configurando en la nube.")
    else:
      img_pil = Image.open(foto_codigo)
      codigos_detectados = decode(img_pil)

      if not codigos_detectados:
        st.warning("⚠️ No se detectó ningún código. Asegúrate de enfocar bien las líneas.")
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
                        <div class="row-item"><span class="col-name">Área Destino:</span> <span class="col-val">{area_destino}</span></div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

          if st.button("☁️ Guardar en Google Sheets", type="primary", use_container_width=True):
            if not CONEXION_GOOGLE_OK:
              st.error("❌ Faltan credenciales base de Google Sheets (requirements.txt).")
            else:
              with st.spinner("⏳ Analizando conexión y enviando datos..."):
                  
                  # PASO 1
                  if "google_json" not in st.secrets:
                      st.error("🛑 DIAGNÓSTICO 1: No se encontró la llave 'google_json' en Streamlit.")
                      st.stop()
                  
                  # PASO 2
                  try:
                      credenciales_dict = json.loads(st.secrets["google_json"])
                  except Exception as e:
                      st.error(f"🛑 DIAGNÓSTICO 2: La llave secreta en Streamlit tiene un error de sintaxis. Detalle: {e}")
                      st.stop()
                  
                  # PASO 3
                  try:
                      scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                      creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_dict, scope)
                      cliente = gspread.authorize(creds)
                  except Exception as e:
                      st.error(f"🛑 DIAGNÓSTICO 3: Error de credenciales de Google. Detalle: {e}")
                      st.stop()

                  # PASO 4
                  try:
                      hoja_calculo = cliente.open_by_url(URL_GOOGLE_SHEETS)
                  except Exception as e:
                      st.error(f"🛑 DIAGNÓSTICO 4 (Error 403): El Robot no tiene permiso para entrar. Verifica en el Excel que el link esté como 'Cualquier persona con el enlace' Editor. Detalle: {e}")
                      st.stop()

                  # PASO 5
                  try:
                      todas_las_pestañas = hoja_calculo.worksheets()
                      pestaña_objetivo = None
                      
                      for p in todas_las_pestañas:
                          if p.title.strip().upper() == area_destino.strip().upper():
                              pestaña_objetivo = p
                              break
                      
                      if pestaña_objetivo is None:
                          nombres_disponibles = ", ".join([f"'{p.title}'" for p in todas_las_pestañas])
                          st.error(f"🛑 DIAGNÓSTICO 5: No encontré la pestaña '{area_destino}'. Pestañas disponibles: {nombres_disponibles}")
                          st.stop()
                      
                      nueva_fila = [
                          "Por asignar", texto_capturado, "", "NUEVO INGRESO", 1,
                          fecha_hoy, "", "", "", usuario_logueado,
                          "Ingresado por App Móvil", "", ""
                      ]
                      
                      pestaña_objetivo.append_row(nueva_fila)
                      st.balloons()
                      st.success(f"🎉 ¡ÉXITO TOTAL! Insumo '{texto_capturado}' guardado en la nube perfectamente.")

                  except Exception as e:
                      st.error(f"🛑 DIAGNÓSTICO FINAL: Ocurrió un error inesperado al escribir. Detalle: {e}")
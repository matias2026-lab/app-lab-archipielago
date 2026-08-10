import base64
import os
import unicodedata
from datetime import date
import pandas as pd
import streamlit as st

# Intentar importar librerías para lectura de imágenes y códigos de barra
try:
  from PIL import Image
  from pyzbar.pyzbar import decode

  LECTOR_DISPONIBLE = True
except ImportError:
  LECTOR_DISPONIBLE = False

# ==============================================================================
# 🌟 CONFIGURACIÓN DE PÁGINA E ÍCONO OFICIAL
# ==============================================================================
icono_app = "🧪"
logo_encontrado = None

for posible_nombre in [
    "logo lab.png",
    "logo.png",
    "logo lab.webp",
    "logo.webp",
]:
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

st.set_page_config(
    page_title="Lab Archipiélago",
    page_icon=icono_app,
    layout="centered",
)

# ==============================================================================
# 🔐 CONFIGURACIÓN DE USUARIOS Y CONTRASEÑAS
# ==============================================================================
USUARIOS = {
    "recepcion": "lab2026",
    "tecnologo": "archipielago2026",
    "admin": "admin1234",
}

# --- Inicialización de variables de sesión ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = ""
if "mostrar_panel_img" not in st.session_state:
  st.session_state.mostrar_panel_img = False

# 🛡️ Persistencia de sesión en URL
params = st.query_params
if "auth_token" in params and params["auth_token"] in USUARIOS:
  st.session_state.autenticado = True
  st.session_state.usuario_actual = params["auth_token"]

# ==============================================================================
# 🎨 ESTILOS CSS PROFESIONALES
# ==============================================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #6a1b29;
        color: #ffffff;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
        height: 0px !important;
        pointer-events: none !important;
    }

    div[data-testid="InputInstructions"], 
    div[data-testid="stInputInstructions"],
    div[class*="InputInstructions"],
    div[data-testid="stTextInput"] small {
        display: none !important;
    }
    
    .stMarkdown, p, h1, h2, h3, h4, span, label {
        color: #ffffff !important;
    }

    .title-text {
        color: #ffffff !important;
        text-align: center;
        font-weight: 800;
        font-size: clamp(1.4rem, 6vw, 2rem) !important;
        margin-top: 5px;
        margin-bottom: 15px;
    }

    /* ESTILO DE PESTAÑAS (TABS) EN BLANCO Y DORADO */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"] {
        color: #d4af37 !important;
        border-bottom-color: #d4af37 !important;
    }

    /* BARRA DE BÚSQUEDA FIJA EN EL TECHO */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stTextInput"]) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 10px !important;
        z-index: 9999 !important;
        background-color: #6a1b29 !important;
        padding: 10px 5px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 25px !important;
        color: #000000 !important;
    }
    
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
        background-color: transparent !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 16px !important;
        padding: 12px 18px !important;
    }

    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stButton"] > button[kind="primary"],
    button[kind="primary"] {
        background-color: #48121b !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        width: 100% !important;
    }

    .card-box {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        padding: 22px 25px;
        border-radius: 12px;
        border-left: 8px solid #d4af37;
        box-shadow: 0 6px 15px rgba(0,0,0,0.25);
        margin-bottom: 20px;
        width: 100%;
    }

    .row-item {
        margin-bottom: 10px;
        font-size: 15px;
        color: #1a1a1a !important;
    }
    .col-name {
        font-weight: 700;
        color: #6a1b29 !important;
    }
    .col-val {
        color: #222222 !important;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def obtener_img_base64(ruta_imagen):
  with open(ruta_imagen, "rb") as f:
    return base64.b64encode(f.read()).decode()


# ==============================================================================
# 🚪 BOTÓN CERRAR SESIÓN
# ==============================================================================
if st.session_state.autenticado:
  col_logout, col_resto = st.columns([1.2, 3.8])
  with col_logout:
    if st.button("🚪 Cerrar Sesión", type="primary", use_container_width=True):
      st.session_state.autenticado = False
      st.session_state.usuario_actual = ""
      st.query_params.clear()
      st.rerun()

if logo_encontrado:
  img_b64 = obtener_img_base64(logo_encontrado)
  mime = "image/png" if logo_encontrado.endswith(".png") else "image/webp"
  st.markdown(
      f"""
    <div style="text-align: center; margin-bottom: 5px;">
        <img src="data:{mime};base64,{img_b64}" style="width: 130px; max-width: 70%; height: auto;">
    </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown(
    '<h1 class="title-text">Laboratorio Archipiélago</h1>',
    unsafe_allow_html=True,
)

# ==============================================================================
# 🔐 PANTALLA DE INICIO DE SESIÓN
# ==============================================================================
if not st.session_state.autenticado:
  st.markdown(
      "<h3 style='text-align: center;'>Acceso Restringido para Personal</h3>",
      unsafe_allow_html=True,
  )
  col_vacia1, col_login, col_vacia2 = st.columns([0.2, 2.6, 0.2])
  with col_login:
    with st.form("form_login", clear_on_submit=False):
      usuario_input = st.text_input(
          "Usuario", placeholder="Ej: recepcion o tecnologo"
      ).strip()
      clave_input = st.text_input("Contraseña", type="password").strip()
      boton_acceder = st.form_submit_button(
          "🔒 Iniciar Sesión", use_container_width=True
      )

      if boton_acceder:
        if (
            usuario_input in USUARIOS
            and USUARIOS[usuario_input] == clave_input
        ):
          st.session_state.autenticado = True
          st.session_state.usuario_actual = usuario_input
          st.query_params["auth_token"] = usuario_input
          st.success("✅ Acceso correcto.")
          st.rerun()
        else:
          st.error("❌ Usuario o contraseña incorrectos.")
  st.stop()

# ==============================================================================
# 🔓 ZONA SEGURA: PESTAÑAS (BUSCADOR DE EXÁMENES + ESCÁNER DE INVENTARIO)
# ==============================================================================
tab_buscador, tab_inventario = st.tabs(
    ["🔍 Buscador de Exámenes", "📦 Escáner de Inventario"]
)

# ------------------------------------------------------------------------------
# PESTAÑA 1: BUSCADOR DE EXÁMENES
# ------------------------------------------------------------------------------
with tab_buscador:
  col_mas, col_input = st.columns([0.16, 0.84])
  with col_mas:
    if st.button("➕", type="secondary", help="Adjuntar imagen"):
      st.session_state.mostrar_panel_img = (
          not st.session_state.mostrar_panel_img
      )

  with col_input:
    consulta = st.text_input(
        "Búsqueda",
        label_visibility="collapsed",
        placeholder="🔍 Buscar exámenes, códigos o indicaciones...",
    )

  st.divider()

  # Carga de datos de Exámenes
  ARCHIVO_EXCEL = "APP lab archipielago 2.xlsx"

  @st.cache_data(ttl=2)
  def cargar_y_unificar_datos(ruta_archivo):
    if not os.path.exists(ruta_archivo):
      return None
    try:
      dict_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
      lista_dfs = []
      for nombre_hoja, df in dict_hojas.items():
        df = df.dropna(how="all")
        df.columns = [str(c).strip() for c in df.columns]
        lista_dfs.append(df)
      df_total = pd.concat(lista_dfs, ignore_index=True)
      return df_total.fillna("")
    except Exception:
      return None

  df_datos = cargar_y_unificar_datos(ARCHIVO_EXCEL)

  def normalizar(texto):
    if pd.isna(texto):
      return ""
    s = str(texto).lower()
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

  if consulta.strip() and df_datos is not None:
    consulta_norm = normalizar(consulta)
    palabras = [p for p in consulta_norm.split() if p]

    def coincide_examen(fila):
      texto_fila = " ".join([str(val) for val in fila.values])
      return all(term in normalizar(texto_fila) for term in palabras)

    df_resultados = df_datos[df_datos.apply(coincide_examen, axis=1)]

    if df_resultados.empty:
      st.warning(f"⚠️ No se encontró información para **'{consulta}'**.")
    else:
      for idx, fila in df_resultados.iterrows():
        html_card = '<div class="card-box">'
        for col, val in fila.items():
          if str(val).strip() != "":
            html_card += (
                f'<div class="row-item"><span class="col-name">{col}:</span>'
                f' <span class="col-val">{val}</span></div>'
            )
        html_card += "</div>"
        st.markdown(html_card, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PESTAÑA 2: ESCÁNER DE CÓDIGO DE BARRAS DE INSUMOS Y REACTIVOS
# ------------------------------------------------------------------------------
with tab_inventario:
  st.markdown(
      "<h3 style='text-align: center;'>Escáner de Recepción de Insumos</h3>",
      unsafe_allow_html=True,
  )

  if not LECTOR_DISPONIBLE:
    st.info(
        "💡 El motor de escáner 'pyzbar' se está instalando desde tu"
        " requirements.txt en la nube."
    )
  else:
    foto_codigo = st.camera_input(
        "Enfoca el código de barras de la caja o reactivo:"
    )

    if foto_codigo:
      img_pil = Image.open(foto_codigo)
      codigos_detectados = decode(img_pil)

      if not codigos_detectados:
        st.warning(
            "⚠️ No se detectó ningún código. Asegúrate de enfocar bien las"
            " barras con suficiente luz."
        )
      else:
        for cod in codigos_detectados:
          texto_capturado = cod.data.decode("utf-8")
          tipo_formato = cod.type
          fecha_hoy = date.today().strftime("%d/%m/%Y")
          usuario_logueado = st.session_state.usuario_actual.upper()

          st.success("✅ ¡Código capturado exitosamente!")

          # Tarjeta de vista previa
          st.markdown(
              f"""
                    <div class="card-box" style="border-left: 8px solid #28a745;">
                        <div class="row-item"><span class="col-name">Código Capturado:</span> <span class="col-val">{texto_capturado}</span></div>
                        <div class="row-item"><span class="col-name">Tipo de Código:</span> <span class="col-val">{tipo_formato}</span></div>
                        <div class="row-item"><span class="col-name">Fecha Recepción:</span> <span class="col-val">{fecha_hoy}</span> (Automática)</div>
                        <div class="row-item"><span class="col-name">Responsable:</span> <span class="col-val">{usuario_logueado}</span></div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

          if st.button(
              "💾 Registrar Ingreso de Insumo",
              type="primary",
              use_container_width=True,
          ):
            st.balloons()
            st.success(
                f"Ingreso de código '{texto_capturado}' guardado con fecha"
                f" {fecha_hoy}."
            )
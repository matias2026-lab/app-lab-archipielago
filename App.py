import base64
import csv
import json
import os
import time
import unicodedata
import re
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import streamlit as st
from rapidfuzz import fuzz, process
from fpdf import FPDF

# ==============================================================================
# 🌟 CONFIGURACIÓN DE PÁGINA
# ==============================================================================
icono_app = "🧪"
logo_encontrado = None

for posible_nombre in ["logo lab.png", "logo.png", "logo lab.webp", "logo.webp"]:
  if os.path.exists(posible_nombre):
    logo_encontrado = posible_nombre
    try:
      from PIL import Image
      if "Image" in locals():
        icono_app = Image.open(posible_nombre)
    except Exception:
      icono_app = posible_nombre
    break

st.set_page_config(page_title="Lab Archipiélago", page_icon=icono_app, layout="centered")

# ==============================================================================
# 🔐 CONFIGURACIÓN DE USUARIOS
# ==============================================================================
# Las credenciales viven en .streamlit/secrets.toml (NUNCA hardcodeadas aquí).
# En Streamlit Cloud se configuran en el panel de "Secrets" del despliegue.
try:
    USUARIOS = dict(st.secrets["USUARIOS"])
except Exception:
    USUARIOS = None

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = ""

# ==============================================================================
# 📝 REGISTRO DE ACTIVIDAD (AUDITORÍA)
# ==============================================================================
ARCHIVO_LOG = "historial_uso.csv"

def registrar_evento(usuario, tipo_evento, detalle=""):
    """Deja constancia en historial_uso.csv de logins y cotizaciones (trazabilidad)."""
    try:
        es_nuevo = not os.path.exists(ARCHIVO_LOG)
        with open(ARCHIVO_LOG, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if es_nuevo:
                writer.writerow(["timestamp", "usuario", "tipo_evento", "detalle"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), usuario, tipo_evento, detalle])
    except Exception:
        pass

def leer_ultimos_eventos(n=15):
    if not os.path.exists(ARCHIVO_LOG): return []
    try:
        with open(ARCHIVO_LOG, newline="", encoding="utf-8") as f:
            filas = list(csv.reader(f))
        return list(reversed(filas[1:]))[:n]
    except Exception:
        return []

# ==============================================================================
# 📢 AVISO DE TIEMPOS DE RESPUESTA (banner editable por el equipo)
# ==============================================================================
# El tiempo de respuesta real cambia seguido (feriados, próximo envío a Santiago) y
# hoy se avisa por mensajes fijados en WhatsApp, que alguien nuevo o que no vio el chat
# esa mañana se puede perder. Esto lo deja visible arriba en la app para todo el equipo.
ARCHIVO_AVISO = "aviso_tiempo_respuesta.json"

def leer_aviso():
    if not os.path.exists(ARCHIVO_AVISO): return None
    try:
        with open(ARCHIVO_AVISO, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def guardar_aviso(mensaje, usuario):
    try:
        with open(ARCHIVO_AVISO, "w", encoding="utf-8") as f:
            json.dump({"mensaje": mensaje, "usuario": usuario, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")}, f, ensure_ascii=False)
        registrar_evento(usuario, "aviso_actualizado", mensaje)
    except Exception:
        pass

def borrar_aviso(usuario):
    try:
        if os.path.exists(ARCHIVO_AVISO): os.remove(ARCHIVO_AVISO)
        registrar_evento(usuario, "aviso_borrado")
    except Exception:
        pass

# ==============================================================================
# 🎨 ESTILOS (BURDEO + DORADO — versión profesional)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --burdeo: #6a1b29;
        --burdeo-oscuro: #4a1119;
        --burdeo-suave: #7d2436;
        --dorado: #c8a24a;
        --dorado-claro: #e0c887;
        --texto-claro: #f4ece6;
    }

    html, body, #root, .stApp, p, span, div, label, button, input, textarea {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    /* Los íconos (ej. ojo de mostrar/ocultar contraseña) son texto con una tipografía de
    símbolos: si se les fuerza Inter, se ve el nombre del ícono en vez del dibujo. */
    [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded" !important;
    }

    /* Fondo general */
    html, body, #root { position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow: hidden !important; overscroll-behavior: none !important; }
    [data-testid="stAppViewContainer"] {
        position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important;
        overflow-y: auto !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
        background: radial-gradient(120% 100% at 50% 0%, var(--burdeo-suave) 0%, var(--burdeo) 45%, var(--burdeo-oscuro) 100%) !important;
    }
    .stApp { background-color: var(--burdeo); color: var(--texto-claro); }
    .main .block-container { max-width: 760px; padding-top: 1.75rem; padding-bottom: 3rem; }

    /* Ocultar elementos innecesarios */
    footer, #MainMenu, header, .stActionButton, .stDeployButton { display: none !important; visibility: hidden !important; }
    [data-testid="InputInstructions"], [data-testid="stInputInstructions"] { display: none !important; }

    /* Encabezado: logo + título */
    .app-logo { text-align: center; margin: 2px 0 10px; }
    .app-logo img { width: 108px; max-width: 55%; filter: drop-shadow(0 6px 14px rgba(0,0,0,0.35)); }
    .title-text {
        color: #ffffff !important; text-align: center; font-weight: 700 !important;
        font-size: clamp(1.5rem, 5vw, 2.05rem) !important; letter-spacing: 0.2px;
        margin-top: 2px !important; margin-bottom: 2px !important;
    }
    .header-divider { height: 1px; max-width: 260px; margin: 0 auto 26px; background: linear-gradient(90deg, transparent, rgba(200,162,74,0.55), transparent); }

    /* Etiquetas de todos los widgets */
    label p, .stTextInput label p, [data-testid="stWidgetLabel"] p {
        color: rgba(244,236,230,0.8) !important; font-weight: 600 !important; font-size: 13px !important;
        text-transform: uppercase; letter-spacing: 0.6px;
    }

    /* Formulario de Login */
    div[data-testid="stForm"] {
        background-color: rgba(0,0,0,0.16) !important; border: 1px solid rgba(200,162,74,0.35) !important;
        border-radius: 18px !important; padding: 30px 26px !important; box-shadow: 0 14px 32px rgba(0,0,0,0.28);
    }

    /* Botones secundarios (barra superior, sugerencias, "Compartir") — discretos */
    div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"],
    a[data-testid="stBaseLinkButton-secondary"] {
        background-color: rgba(255,255,255,0.04) !important; color: rgba(244,236,230,0.85) !important;
        border: 1px solid rgba(244,236,230,0.28) !important; border-radius: 9px !important;
        font-weight: 600 !important; font-size: 13.5px !important; padding: 9px 14px !important;
        box-shadow: none !important; transition: all 0.15s ease;
    }
    div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"]:hover,
    a[data-testid="stBaseLinkButton-secondary"]:hover {
        border-color: var(--dorado) !important; color: var(--dorado-claro) !important; background-color: rgba(200,162,74,0.10) !important;
    }

    /* Botones primarios (Iniciar Sesión, Descargar PDF) — con jerarquía visual */
    div[data-testid="stButton"] button[data-testid="stBaseButton-primary"],
    div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(180deg, var(--dorado-claro), var(--dorado)) !important; color: #3b2c0c !important;
        border: none !important; border-radius: 10px !important; font-weight: 700 !important; font-size: 15px !important;
        padding: 10px 18px !important; box-shadow: 0 8px 18px rgba(0,0,0,0.28) !important; transition: all 0.15s ease;
    }
    div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover { filter: brightness(1.06); transform: translateY(-1px); }
    div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:active,
    div[data-testid="stFormSubmitButton"] button:active,
    div[data-testid="stDownloadButton"] button:active { transform: translateY(0); filter: brightness(0.95); }

    div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stDownloadButton"] button, a[data-testid="stBaseLinkButton-secondary"] { width: 100% !important; }

    /* 🟡 PESTAÑAS (TABS) */
    [role="tablist"] {
        background-color: transparent !important;
        border-bottom: 1px solid rgba(244,236,230,0.14) !important;
        gap: 30px !important;
    }
    div[data-testid="stTab"] { background-color: transparent !important; border: none !important; padding-bottom: 10px !important; }
    div[data-testid="stTab"] p {
        color: rgba(244,236,230,0.5) !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stTab"][aria-selected="true"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    div[data-testid="stTab"][aria-selected="true"] {
        border-bottom: 2.5px solid var(--dorado) !important;
    }

    /* 🟡 Radio Buttons (Particular, Fonasa) */
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label span,
    div[role="radiogroup"] label div {
        color: rgba(244,236,230,0.92) !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        text-transform: none;
        letter-spacing: normal;
    }

    /* Inputs de texto */
    div[data-testid="stTextInputRootElement"], div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.22) !important;
    }
    div[data-testid="stTextInputRootElement"] input, div[data-baseweb="input"] input, div[data-baseweb="base-input"] input,
    input[type="text"], input[type="password"] {
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        caret-color: var(--burdeo) !important;
        font-size: 15.5px !important;
        padding: 13px 18px !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stTextInputRootElement"]:focus-within, div[data-baseweb="input"]:focus-within, div[data-baseweb="base-input"]:focus-within {
        box-shadow: 0 0 0 3px rgba(200,162,74,0.45), 0 6px 16px rgba(0,0,0,0.22) !important;
    }

    /* Cuadros de texto largos (ej. editor del aviso) - mismo tratamiento que los inputs */
    textarea {
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        caret-color: var(--burdeo) !important;
        background-color: #ffffff !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.22) !important;
    }

    /* Filtro de categoría (multiselect) */
    div[data-baseweb="select"] > div, div[data-testid="stMultiSelect"] [data-baseweb="select"] {
        background-color: #ffffff !important; border-radius: 14px !important; border: none !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.22) !important;
    }
    [data-baseweb="tag"] { background-color: var(--burdeo) !important; border-radius: 6px !important; }
    [data-baseweb="tag"] span, [data-baseweb="tag"] svg { color: #ffffff !important; fill: #ffffff !important; }

    /* Tarjetas de resultados */
    .card-box {
        background-color: #ffffff !important; color: #1a1a1a !important; padding: 22px 26px; border-radius: 14px;
        border-top: 3px solid var(--dorado); margin-bottom: 18px; box-shadow: 0 10px 26px rgba(0,0,0,0.24);
    }
    .row-item { margin-bottom: 9px; font-size: 14.5px; color: #1a1a1a !important; border-radius: 6px; padding: 3px 0; }
    .col-name { font-weight: 600; color: var(--burdeo) !important; }
    .col-val { color: #2a2a2a !important; font-weight: 500; }

    .advertencia-cobro {
        background-color: #fff4e0; color: #7a4a00; border: 1px solid #e8b64a; border-left: 4px solid #d98c00;
        border-radius: 8px; padding: 10px 12px; margin-bottom: 14px; font-size: 13.5px; font-weight: 600; line-height: 1.4;
    }

    .cotizador-box { margin-bottom: 20px; padding-top: 8px; }

    /* Banner de aviso de tiempos de respuesta */
    .aviso-banner {
        background: linear-gradient(180deg, rgba(200,162,74,0.16), rgba(200,162,74,0.08));
        border: 1px solid rgba(200,162,74,0.5); border-radius: 12px; color: #ffffff;
        padding: 12px 16px; margin: 4px 0 20px; font-size: 14px; font-weight: 600; text-align: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.18);
    }

    /* Expanders en la pantalla principal (ej. editor del aviso) - bien visibles */
    [data-testid="stExpander"] {
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(200,162,74,0.45) !important;
        border-radius: 12px !important;
        margin-bottom: 18px !important;
    }
    [data-testid="stExpander"] summary {
        color: #ffffff !important; font-weight: 700 !important; font-size: 14.5px !important;
    }
    [data-testid="stExpander"] summary:hover { color: var(--dorado-claro) !important; }

    /* Menú "☰" (Actualizar datos / Cerrar Sesión) — botón disparador, estilo ícono plano */
    [data-testid="stPopoverButton"] {
        background-color: transparent !important; color: rgba(244,236,230,0.85) !important;
        border: none !important; border-radius: 9px !important;
        font-size: 17px !important; box-shadow: none !important; transition: all 0.15s ease;
    }
    [data-testid="stPopoverButton"]:hover { background-color: rgba(255,255,255,0.06) !important; color: var(--dorado-claro) !important; }
    [data-testid="stPopoverBody"] {
        background-color: var(--burdeo-oscuro) !important;
        border: 1px solid rgba(200,162,74,0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 14px 32px rgba(0,0,0,0.35) !important;
    }
    [data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
    [data-testid="stPopoverBody"] p,
    [data-testid="stPopoverBody"] span,
    [data-testid="stPopoverBody"] label,
    [data-testid="stPopoverBody"] textarea {
        color: rgba(244,236,230,0.95) !important;
    }
    [data-testid="stPopoverBody"] hr {
        border-color: rgba(244,236,230,0.14) !important;
        margin: 4px 0 !important;
    }
    /* Botones del menú ☰ (Actualizar datos / Cerrar Sesión): estilo de ítem de lista, sin recuadro */
    [data-testid="stPopoverBody"] div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] {
        background-color: transparent !important; border: none !important; text-align: left !important;
        justify-content: flex-start !important; padding: 8px 6px !important; font-weight: 600 !important;
    }
    [data-testid="stPopoverBody"] div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"]:hover {
        background-color: rgba(255,255,255,0.06) !important; color: var(--dorado-claro) !important;
    }
    /* Editor de mensaje (expander) anidado en el menú ☰: sin recuadro propio */
    [data-testid="stPopoverBody"] [data-testid="stExpander"] {
        background-color: transparent !important; border: none !important; margin-bottom: 4px !important;
    }
    [data-testid="stPopoverBody"] [data-testid="stExpander"] summary { padding: 8px 6px !important; }
    /* Excepción: "Borrar aviso" (dentro del editor) conserva look de botón real, no de ítem de menú */
    [data-testid="stPopoverBody"] [data-testid="stExpander"] div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] {
        background-color: rgba(255,255,255,0.04) !important; border: 1px solid rgba(244,236,230,0.28) !important;
        text-align: center !important; justify-content: center !important; padding: 9px 14px !important;
    }
    [data-testid="stPopoverBody"] [data-testid="stExpander"] div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"]:hover {
        border-color: var(--dorado) !important; background-color: rgba(200,162,74,0.10) !important;
    }

    /* Alertas (success / warning / error / info) coherentes con la paleta */
    div[data-testid="stAlert"] { border-radius: 12px !important; border: none !important; box-shadow: 0 6px 16px rgba(0,0,0,0.18); }

    /* Barra lateral */
    section[data-testid="stSidebar"] { background-color: var(--burdeo-oscuro) !important; border-right: 1px solid rgba(200,162,74,0.2); }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {
        color: rgba(244,236,230,0.85) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def obtener_img_base64(ruta_imagen):
  with open(ruta_imagen, "rb") as f:
    return base64.b64encode(f.read()).decode()

# ----------------- BARRA SUPERIOR -----------------
if st.session_state.autenticado:
    col_menu, col_espacio = st.columns([0.15, 0.85])
    with col_menu:
        with st.popover("☰", use_container_width=True, help="Más opciones"):
            if st.button("Actualizar datos", use_container_width=True, help="Vuelve a leer el Excel desde disco (usar si se editaron precios o exámenes)."):
                st.cache_data.clear()
                st.success("Datos actualizados.")
                st.rerun()

            with st.expander("Editor de mensaje"):
                aviso_actual_menu = leer_aviso()
                nuevo_aviso = st.text_area(
                    "Mensaje visible para todo el equipo",
                    value=aviso_actual_menu.get("mensaje", "") if aviso_actual_menu else "",
                    placeholder="Ej: Tiempo extendido para Hormonas y Coagulación hasta el martes 7 de julio.",
                    key="input_aviso",
                    label_visibility="collapsed",
                )
                col_guardar_aviso, col_borrar_aviso = st.columns(2)
                with col_guardar_aviso:
                    if st.button("Guardar aviso", use_container_width=True, type="primary", key="btn_guardar_aviso"):
                        if nuevo_aviso.strip():
                            guardar_aviso(nuevo_aviso.strip(), st.session_state.usuario_actual)
                            st.rerun()
                        else:
                            st.warning("Escribe un mensaje antes de guardar.")
                with col_borrar_aviso:
                    if st.button("Borrar aviso", use_container_width=True, key="btn_borrar_aviso"):
                        borrar_aviso(st.session_state.usuario_actual)
                        st.rerun()
                if aviso_actual_menu:
                    st.caption(f"Actualizado por {aviso_actual_menu.get('usuario','?')} · {aviso_actual_menu.get('fecha','?')}")

            st.markdown("---")
            if st.button("Cerrar Sesión", use_container_width=True):
                st.session_state.autenticado = False
                st.session_state.usuario_actual = ""
                st.rerun()

if logo_encontrado:
  img_b64 = obtener_img_base64(logo_encontrado)
  mime = "image/png" if logo_encontrado.endswith(".png") else "image/webp"
  st.markdown(f'<div class="app-logo"><img src="data:{mime};base64,{img_b64}"></div>', unsafe_allow_html=True)

st.markdown('<h1 class="title-text">Laboratorio Archipiélago</h1>', unsafe_allow_html=True)
st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)

# ==============================================================================
# 🔐 PANTALLA DE INICIO DE SESIÓN
# ==============================================================================
if not st.session_state.autenticado:
  if USUARIOS is None:
    st.error(
        "⚠️ No hay usuarios configurados. Crea el archivo `.streamlit/secrets.toml` "
        "con una sección `[USUARIOS]` (o configúralo en Streamlit Cloud → Settings → Secrets)."
    )
    st.stop()

  col_vacia1, col_login, col_vacia2 = st.columns([0.05, 2.9, 0.05])
  with col_login:
    with st.form("form_login", clear_on_submit=False):
      usuario_input = st.text_input("Usuario", placeholder="").strip()
      clave_input = st.text_input("Contraseña", type="password").strip()
      if st.form_submit_button("Iniciar Sesión", use_container_width=True, type="primary"):
        if usuario_input in USUARIOS and USUARIOS[usuario_input] == clave_input:
          st.session_state.autenticado = True
          st.session_state.usuario_actual = usuario_input
          registrar_evento(usuario_input, "login")
          st.rerun()
        else:
          st.error("Credenciales incorrectas.")
  st.stop()

def normalizar(texto):
  if pd.isna(texto): return ""
  return "".join([c for c in unicodedata.normalize("NFKD", str(texto).lower()) if not unicodedata.combining(c)])

def es_columna_precio_fonasa(col_name):
    c = normalizar(str(col_name))
    return "copago fonasa 2026" in c or ("copago" in c and "fonasa" in c and "2026" in c)
def es_columna_precio_particular(col_name):
    c = normalizar(str(col_name))
    return "valor particular 2026" in c or ("valor" in c and "particular" in c and "2026" in c)
def es_col_precio(c):
    cn = normalizar(str(c))
    return es_columna_precio_fonasa(c) or es_columna_precio_particular(c) or "valor" in cn or "precio" in cn or "arancel" in cn
def es_col_tiempo(c): return "tiempo" in normalizar(str(c)) or "respuesta" in normalizar(str(c)) or "dias" in normalizar(str(c))
def es_col_contenedor(c): return "contenedor" in normalizar(str(c)) or "transporte" in normalizar(str(c)) or "tubo" in normalizar(str(c))
def es_col_muestra(c): return "tipo" in normalizar(str(c)) or "muestra" in normalizar(str(c))
def es_col_incluye(c): return "incluye" in normalizar(str(c))
def es_col_codigo(c): return "codigo" in normalizar(str(c)) or "bklab" in normalizar(str(c)) or "proactive" in normalizar(str(c))
def es_col_nombre(c):
    cn = normalizar(str(c)).strip()
    return "archipielago" in cn or "nombre" in cn or "prestacion" in cn or "examen" in cn or "unnamed" in cn or "descripcion" in cn
def es_col_categoria(c):
    cn = normalizar(str(c)).strip()
    return cn == "seccion" or "seccion" in cn or cn == "categoria" or "categoria" in cn
def es_col_advertencia_cobro(c):
    cn = normalizar(str(c))
    return "nota" in cn and "cobro" in cn

# Columnas auxiliares que la app agrega internamente y que nunca deben mostrarse
# ni tratarse como datos reales del examen.
COLUMNAS_INTERNAS = ("__hoja_origen__", "__puntaje__", "__categoria__", "__nombre_examen__", "__texto_busqueda__")

def obtener_mejor_col_nombre(f_dict):
    posibles = [c for c in f_dict.keys() if es_col_nombre(c) and c not in COLUMNAS_INTERNAS and str(f_dict[c]).strip() != "" and "sinonimo" not in normalizar(str(c))]
    for c in posibles:
        if "archipielago" in normalizar(str(c)): return c, True
    for c in posibles:
        if "nombre" in normalizar(str(c)) or "prestacion" in normalizar(str(c)): return c, True
    if posibles: return posibles[0], True

    for c in f_dict.keys():
        if c not in COLUMNAS_INTERNAS and str(f_dict[c]).strip() != "": return c, False
    return None, False

def _construir_alias_barnafi_prestaciones(dict_limpio, conectores):
    """Empareja cada examen de 'Examenes barnafi (BK)' con su fila equivalente en
    'prestaciones', incluso cuando el nombre no es idéntico (ej. 'Zinc en suero o
    plasma' vs 'ZINC EN PLASMA'). Primero por nombre exacto (una vez normalizado);
    lo que quede, por similitud de palabras -pero solo si hay un candidato claramente
    mejor que el resto, para no arriesgar una fusión incorrecta entre dos exámenes
    distintos con nombres parecidos (ej. 'Factor V' vs 'Factor V Leiden')."""
    df_prest = next((df for n, df in dict_limpio.items() if "prestac" in normalizar(n)), None)
    df_barn = next((df for n, df in dict_limpio.items() if "barnafi" in normalizar(n) or "bklab" in normalizar(n)), None)
    if df_prest is None or df_barn is None:
        return {}, {}

    def clave(nombre):
        n = normalizar(str(nombre)).strip()
        n = re.sub(r'[^\w\s]', ' ', n)
        return " ".join(p for p in n.split() if p and p not in conectores)

    claves_prest = set()
    for _, fila in df_prest.iterrows():
        fd = fila.to_dict()
        col_n, _ = obtener_mejor_col_nombre(fd)
        if col_n:
            c = clave(fd[col_n])
            if c: claves_prest.add(c)

    barnafi_filas = []
    for _, fila in df_barn.iterrows():
        fd = fila.to_dict()
        col_n, _ = obtener_mejor_col_nombre(fd)
        if col_n:
            c = clave(fd[col_n])
            if c: barnafi_filas.append((c, fd))

    restantes = set(claves_prest)
    alias_barnafi_a_prest = {}
    barnafi_por_clave_prest = {}
    pendientes = []
    for c, fd in barnafi_filas:
        if c in restantes:
            alias_barnafi_a_prest[c] = c
            barnafi_por_clave_prest[c] = fd
            restantes.discard(c)
        else:
            pendientes.append((c, fd))

    # Respaldo por similitud: solo si hay un único candidato claramente mejor que el
    # resto (subconjunto de palabras + comparten la primera palabra, que normalmente
    # es el nombre del analito -evita coincidir con filas basura del Excel como
    # "EN ORINA AISLADA" que no traen el nombre del examen-).
    for c, fd in pendientes:
        palabras_b = set(c.split())
        primera = c.split()[0] if c else None
        if not primera: continue
        mejor, mejor_score, segundo_score = None, 0.0, 0.0
        for cp in restantes:
            palabras_p = set(cp.split())
            if primera not in palabras_p: continue
            if not (palabras_b.issubset(palabras_p) or palabras_p.issubset(palabras_b)): continue
            inter = len(palabras_b & palabras_p); union = len(palabras_b | palabras_p)
            score = inter / union if union else 0
            if score > mejor_score:
                segundo_score = mejor_score
                mejor_score = score
                mejor = cp
            elif score > segundo_score:
                segundo_score = score
        if mejor and mejor_score >= 0.55 and (mejor_score - segundo_score) >= 0.15:
            alias_barnafi_a_prest[c] = mejor
            barnafi_por_clave_prest[mejor] = fd
            restantes.discard(mejor)

    return alias_barnafi_a_prest, barnafi_por_clave_prest

# ==============================================================================
# 📂 CARGA DE DATOS MULTI-HOJA Y DICCIONARIO
# ==============================================================================
ARCHIVO_EXCEL = "APP lab archipielago 2.xlsx"

def _config_google_sheets():
    """Lee [GOOGLE_SHEETS] de secrets.toml. Si no está configurado, la app sigue
    funcionando con el Excel local (modo por defecto)."""
    try:
        cfg = st.secrets["GOOGLE_SHEETS"]
        sheet_id = str(cfg["sheet_id"]).strip()
        gids = {str(k): str(v) for k, v in dict(cfg["gids"]).items()}
        if sheet_id and gids:
            return sheet_id, gids
    except Exception:
        pass
    return None, None

GOOGLE_SHEET_ID, GOOGLE_SHEET_GIDS = _config_google_sheets()
USA_GOOGLE_SHEETS = GOOGLE_SHEET_ID is not None

def _leer_hojas_desde_google_sheets(sheet_id, gids):
    """Cada pestaña de Google Sheets se lee como CSV público (requiere que la hoja
    esté compartida como 'Cualquier usuario con el enlace: Lector')."""
    dict_hojas = {}
    for nombre_hoja, gid in gids.items():
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        if df.shape[1] <= 1 and str(df.columns[0]).lstrip().startswith("<"):
            # La hoja devolvió HTML (login de Google) en vez de CSV: no está compartida.
            raise RuntimeError(f"La hoja '{nombre_hoja}' no es accesible públicamente. Revisa el permiso para compartir en Google Sheets.")
        dict_hojas[nombre_hoja] = df
    return dict_hojas

if USA_GOOGLE_SHEETS:
    # Sin un archivo local no hay "fecha de modificación" que vigilar, así que la
    # clave de caché cambia sola cada 90s (más el botón manual "Actualizar datos"
    # que siempre fuerza una relectura inmediata).
    _version_datos = ("gsheets", int(time.time() // 90))
else:
    _version_datos = ("local", os.path.getmtime(ARCHIVO_EXCEL) if os.path.exists(ARCHIVO_EXCEL) else 0)

@st.cache_data
def cargar_hojas_y_diccionario(_version):
    try:
        if USA_GOOGLE_SHEETS:
            dict_hojas = _leer_hojas_desde_google_sheets(GOOGLE_SHEET_ID, GOOGLE_SHEET_GIDS)
        else:
            if not os.path.exists(ARCHIVO_EXCEL): return None, None, None, None
            dict_hojas = pd.read_excel(ARCHIVO_EXCEL, sheet_name=None)

        diccionario = {
            "sin_preparacion": [],
            "conectores": []
        }

        clave_dicc = next((k for k in dict_hojas.keys() if "diccionario" in normalizar(k)), None)
        if clave_dicc is not None:
            df_dicc = dict_hojas[clave_dicc]
            for col in df_dicc.columns:
                cn = normalizar(str(col))
                valores = [normalizar(str(v)).strip() for v in df_dicc[col].dropna() if str(v).strip() != ""]
                if "preparacion" in cn: diccionario["sin_preparacion"] = valores
                elif "conector" in cn or "ignorar" in cn: diccionario["conectores"] = valores
            del dict_hojas[clave_dicc]

        if not diccionario["sin_preparacion"]:
            diccionario["sin_preparacion"] = ["tp", "tt", "ttpa", "ttpk", "pcr", "gen", "mutacion", "fr", "factor reumatoide", "grupo sanguineo", "coombs", "subunidad beta", "test rapido", "biologia molecular", "hemograma", "coagulacion", "fibrinogeno", "creatinina"]
        if not diccionario["conectores"]:
            diccionario["conectores"] = ["de", "la", "el", "los", "las", "en", "con", "para", "y", "o"]

        dict_limpio = {}
        for nombre_hoja, df in dict_hojas.items():
            df_clean = df.dropna(how="all").rename(columns=lambda c: str(c).strip()).fillna("")
            df_clean['__hoja_origen__'] = nombre_hoja.strip()
            dict_limpio[nombre_hoja.strip()] = df_clean

        df_todas = pd.concat(list(dict_limpio.values()), ignore_index=True).fillna("")

        def pre_calcular_texto(fila):
            elementos = []
            tiene_plata = False
            tiene_codigo = False
            nombre_oculto = ""
            for c, v in fila.items():
                if str(v).strip() != "" and c != "__hoja_origen__":
                    cn = normalizar(str(c))
                    vn = normalizar(str(v))
                    elementos.extend([cn, vn])
                    if es_col_precio(c): tiene_plata = True
                    if es_col_codigo(c): tiene_codigo = True
                    if es_col_nombre(c): nombre_oculto += " " + str(v)

            texto = " ".join(elementos)
            if tiene_plata: texto += " precio precios valor valores arancel copago fonasa particular"
            if tiene_codigo: texto += " codigo codigos"

            for term in diccionario["sin_preparacion"]:
                norm = normalizar(nombre_oculto)
                if (len(term) <= 4 and re.search(rf'\b{term}\b', norm)) or (len(term) > 4 and term in norm):
                    texto += " examen examenes sin preparacion no requiere preparacion indicaciones"
                    break

            return texto

        df_todas['__texto_busqueda__'] = df_todas.apply(pre_calcular_texto, axis=1)

        def obtener_categoria_fila(fila):
            for c, v in fila.items():
                if c in COLUMNAS_INTERNAS: continue
                if es_col_categoria(c) and str(v).strip() != "":
                    return str(v).strip().title()
            return str(fila.get("__hoja_origen__", "")).strip() or "Otros"

        def obtener_nombre_examen_fila(fila):
            for c, v in fila.items():
                if c in COLUMNAS_INTERNAS: continue
                cn = normalizar(str(c))
                if es_col_nombre(c) and "sinonimo" not in cn and str(v).strip() != "":
                    return str(v).strip()
            return ""

        df_todas['__categoria__'] = df_todas.apply(obtener_categoria_fila, axis=1)
        df_todas['__nombre_examen__'] = df_todas.apply(obtener_nombre_examen_fila, axis=1)

        lista_autocomplete = sorted({n for n in df_todas['__nombre_examen__'] if n and len(n) > 2})

        alias_barnafi_a_prest, barnafi_por_clave_prest = _construir_alias_barnafi_prestaciones(dict_limpio, diccionario["conectores"])

        return dict_limpio, diccionario, df_todas, lista_autocomplete, alias_barnafi_a_prest, barnafi_por_clave_prest
    except Exception as e:
        st.session_state["_error_carga_datos"] = str(e)
        return None, None, None, None, {}, {}

dict_hojas_excel, diccionario_virtual, df_todas_las_hojas_cache, lista_autocomplete, alias_barnafi_a_prest, barnafi_por_clave_prest = cargar_hojas_y_diccionario(_version_datos)

# ==============================================================================
# 🛠️ FUNCIONES DE CÁLCULO Y AGRUPACIÓN
# ==============================================================================
def extraer_monto_limpio(val):
    if pd.isna(val) or str(val).strip() == "": return 0
    if isinstance(val, (int, float)): return int(val)
    s_val = str(val).replace('$', '').replace(' ', '').strip()
    if s_val.endswith('.0'): s_val = s_val[:-2]
    if s_val.endswith('.00'): s_val = s_val[:-3]
    s_val = s_val.replace('.', '').replace(',', '')
    numeros = re.findall(r'\d+', s_val)
    if numeros: return int(numeros[0])
    return 0

def formatear_pesos(monto): return f"${int(monto):,}".replace(",", ".")

def obtener_precio(fila, tipo_pago):
    fila_dict = fila.to_dict()
    if tipo_pago == "Particular":
        for col, val in fila_dict.items():
            if es_columna_precio_particular(col): return extraer_monto_limpio(val)
    else:
        for col, val in fila_dict.items():
            if es_columna_precio_fonasa(col): return extraer_monto_limpio(val)
    return 0

def _texto_latin1_seguro(texto):
    return str(texto).encode("latin-1", "replace").decode("latin-1")

def generar_pdf_cotizacion(items, total, tipo_pago, usuario):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 10, _texto_latin1_seguro("Laboratorio Archipiélago - Cotización"), align="C")

    pdf.set_font("Helvetica", "", 10)
    encabezado = f"Previsión: {tipo_pago}    Usuario: {usuario}    Fecha: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 8, _texto_latin1_seguro(encabezado), align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    for nombre_real, precio, es_aproximado in items:
        prefijo = "(aprox.) " if es_aproximado else "- "
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 7, _texto_latin1_seguro(f"{prefijo}{nombre_real}: {formatear_pesos(precio)}"))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 10, _texto_latin1_seguro(f"TOTAL {tipo_pago.upper()}: {formatear_pesos(total)}"))
    return bytes(pdf.output())

def normalizar_nombre_agrupacion(nombre):
    n = normalizar(str(nombre)).strip()
    n = re.sub(r'[^\w\s]', '', n)
    conectores = diccionario_virtual["conectores"] if diccionario_virtual else ["de", "la", "el", "los", "las", "en", "con", "para", "y", "o"]
    palabras = [p for p in n.split() if p not in conectores]
    return " ".join(palabras)

def verificar_es_sin_prep(nombre_test):
    if not diccionario_virtual: return False
    norm = normalizar(nombre_test)
    for term in diccionario_virtual["sin_preparacion"]:
        if len(term) <= 4:
            if re.search(rf'\b{term}\b', norm): return True
        else:
            if term in norm: return True
    return False

def acortar_nombre_examen(nombre):
    """Muchos nombres de examen traen una descripción larga entre paréntesis
    (ej. 'PERFIL HEPATICO (INCLUYE: BILIRRUBINA...)'). Para el fuzzy matching hay que
    comparar solo contra el título corto, si no el ratio de similitud queda dominado
    por la descripción y puede preferir una coincidencia parcial incorrecta."""
    return re.split(r'[(,]', str(nombre))[0].strip()

def busqueda_fuzzy(df, consulta, min_score=70, top_n=40):
    """Respaldo para errores de tipeo: se usa solo cuando la búsqueda exacta no encuentra nada."""
    if df.empty or '__nombre_examen__' not in df.columns: return df.iloc[0:0]
    q = normalizar(consulta)
    nombres = [normalizar(acortar_nombre_examen(n)) for n in df['__nombre_examen__'].tolist()]
    coincidencias = process.extract(q, nombres, scorer=fuzz.WRatio, limit=top_n, score_cutoff=min_score)
    if not coincidencias: return df.iloc[0:0]
    posiciones = [idx for _, _score, idx in coincidencias]
    return df.iloc[posiciones]

def _campo_nombre_fusion(c):
    cn = normalizar(str(c))
    return "archipielago" in cn or "descripcion" in cn or "prestacion" in cn or cn.strip() == "nombre" or "examen" in cn
def _campo_fonasa_fusion(c):
    cn = normalizar(str(c))
    return "codigo" in cn and "fonasa" in cn
def _campo_tiempo_resp_fusion(c):
    cn = normalizar(str(c))
    return "tiempo" in cn and "respuesta" in cn
def _campo_dia_proceso_fusion(c):
    cn = normalizar(str(c))
    return "dia" in cn and "proceso" in cn
def _campo_precio_fusion(c):
    return es_col_precio(c) and not _campo_nombre_fusion(c)
def _es_campo_compartido_fusion(c):
    return _campo_nombre_fusion(c) or _campo_fonasa_fusion(c) or _campo_tiempo_resp_fusion(c) or _campo_dia_proceso_fusion(c) or _campo_precio_fusion(c)

def fusionar_prestacion_y_barnafi(fila_prest, fila_barnafi):
    """Cuando un examen aparece en 'prestaciones' Y en 'Examenes barnafi (BK)' (es decir,
    se deriva al laboratorio BK), ambas filas describen la MISMA prestación y no deben
    mostrarse como dos tarjetas separadas.

    Regla: en los campos que existen en ambas hojas (nombre, código FONASA, tiempo de
    respuesta, día de proceso) se usa el valor de Barnafi -EXCEPTO el precio, que siempre
    se toma de 'prestaciones'-. Los campos exclusivos de 'prestaciones' (ayuno, contenedor,
    tipo de muestra, sección, etc.) y los exclusivos de Barnafi (código BK, horas de
    proceso) se agregan tal cual, formando una sola tarjeta completa."""
    fp = fila_prest.to_dict() if hasattr(fila_prest, "to_dict") else dict(fila_prest)
    fb = fila_barnafi.to_dict() if hasattr(fila_barnafi, "to_dict") else dict(fila_barnafi)

    consolidada = {}

    # 1. Campos exclusivos de 'prestaciones' (no se solapan con Barnafi ni son precio).
    for c, v in fp.items():
        if c in COLUMNAS_INTERNAS or str(v).strip() == "": continue
        if _es_campo_compartido_fusion(c): continue
        consolidada[c] = v

    # 2. Precio: siempre desde 'prestaciones'.
    for c, v in fp.items():
        if c in COLUMNAS_INTERNAS or str(v).strip() == "": continue
        if _campo_precio_fusion(c):
            consolidada[c] = v

    # 3. Campos compartidos (nombre, código FONASA, tiempo de respuesta, día de proceso):
    #    preferir Barnafi; si Barnafi no trae el dato, usar el de 'prestaciones'.
    for check in (_campo_nombre_fusion, _campo_fonasa_fusion, _campo_tiempo_resp_fusion, _campo_dia_proceso_fusion):
        col_b = next((c for c, v in fb.items() if c not in COLUMNAS_INTERNAS and check(c) and not _campo_precio_fusion(c) and str(v).strip() != ""), None)
        if col_b:
            consolidada[col_b] = fb[col_b]
        else:
            col_p = next((c for c, v in fp.items() if c not in COLUMNAS_INTERNAS and check(c) and not _campo_precio_fusion(c) and str(v).strip() != ""), None)
            if col_p and col_p not in consolidada:
                consolidada[col_p] = fp[col_p]

    # 4. Campos exclusivos de Barnafi (código BK, horas de proceso, etc.).
    for c, v in fb.items():
        if c in COLUMNAS_INTERNAS or str(v).strip() == "": continue
        if _es_campo_compartido_fusion(c): continue
        if c not in consolidada:
            consolidada[c] = v

    return consolidada

# ==============================================================================
# 🎨 RENDERIZADOR GRÁFICO DE TARJETAS
# ==============================================================================
def renderizar_tarjeta(fila_dict, palabras, palabras_filtro):
    fila_dict = {k: v for k, v in fila_dict.items() if k not in COLUMNAS_INTERNAS}

    # La advertencia de cobro (ej. "ya incluye GGT, no cobrar aparte") es información de
    # seguridad: se muestra siempre, sin importar qué columnas filtró la búsqueda, y se
    # saca de fila_dict para que no aparezca ademas como una fila normal más abajo.
    col_advertencia = next((c for c in fila_dict.keys() if es_col_advertencia_cobro(c)), None)
    texto_advertencia = str(fila_dict.pop(col_advertencia, "")).strip() if col_advertencia else ""

    palabras_f = palabras_filtro.copy()
    if "horario" in palabras_f or "horarios" in palabras_f:
        palabras_f.extend(["horario", "horarios", "condicion", "condiciones", "lunes", "sabado", "viernes"])

    col_nombre_final, es_nombre_oficial = obtener_mejor_col_nombre(fila_dict)
    cols_esenciales = [col_nombre_final] if col_nombre_final else []

    has_fonasa = "fonasa" in palabras
    has_particular = "particular" in palabras
    has_precio = any(w in palabras for w in ["precio", "precios", "valor", "valores", "arancel", "copago"])

    cols_especificas = []
    if has_fonasa and not has_particular:
        for c in fila_dict.keys():
            if es_columna_precio_fonasa(c) or "valor" in normalizar(str(c)) or "precio" in normalizar(str(c)): cols_especificas.append(c)
            elif any(p in normalizar(str(c)) for p in palabras_f if p not in ["fonasa", "copago", "2026"]): cols_especificas.append(c)
    elif has_particular and not has_fonasa:
        for c in fila_dict.keys():
            if es_columna_precio_particular(c) or "valor" in normalizar(str(c)) or "precio" in normalizar(str(c)): cols_especificas.append(c)
            elif any(p in normalizar(str(c)) for p in palabras_f if p not in ["particular", "valor", "2026"]): cols_especificas.append(c)
    elif has_precio:
        for c in fila_dict.keys():
            if es_col_precio(c): cols_especificas.append(c)
            elif any(p in normalizar(str(c)) for p in palabras_f if p not in ["fonasa", "particular", "precio", "valor", "arancel", "copago"]): cols_especificas.append(c)
    else:
        for c in fila_dict.keys():
            if any(term in normalizar(str(c)) for term in palabras_f):
                cols_especificas.append(c)

    if cols_especificas or has_fonasa or has_particular or has_precio:
        cols_a_mostrar = list(dict.fromkeys(([col_nombre_final] if col_nombre_final else []) + cols_especificas))
    else:
        cols_a_mostrar = [c for c in fila_dict.keys() if c not in COLUMNAS_INTERNAS]

    cols_filtradas = []
    for c in cols_a_mostrar:
        if c in COLUMNAS_INTERNAS: continue
        cn = normalizar(str(c))
        val_norm = normalizar(str(fila_dict[c]))

        if any(b in cn for b in ["sinonimo", "sinónimo", "palabra", "item", "tema/examen", "tema / examen"]): continue
        if es_col_nombre(c) and col_nombre_final and c != col_nombre_final: continue

        if cn == "categoria" or cn == "tema":
            if not any(p in val_norm for p in palabras): continue

        cols_filtradas.append(c)

    cols_a_mostrar = cols_filtradas

    contenido_tarjeta = ""
    es_sin_prep_test = False

    # 1. Título Principal
    if col_nombre_final:
        val_str_nombre = str(fila_dict.get(col_nombre_final, "")).strip()

        es_sin_prep_test = verificar_es_sin_prep(val_str_nombre)

        if val_str_nombre != "":
            cn_final = normalizar(str(col_nombre_final)).strip()
            es_titulo_limpio = (not es_nombre_oficial or cn_final == "" or "unnamed" in cn_final or "tema" in cn_final or "examen" == cn_final)

            if es_titulo_limpio:
                contenido_tarjeta += f'<div class="row-item" style="margin-bottom: 12px; border-bottom: 2px solid #d4af37; padding-bottom: 8px;"><span class="col-val" style="font-size: 1.15em; font-weight: 800; color: #1a1a1a; text-transform: uppercase;">{val_str_nombre}</span></div>'
            else:
                contenido_tarjeta += f'<div class="row-item" style="margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;"><span class="col-name" style="font-size: 1.05em; color: #6a1b29;">{col_nombre_final}:</span> <span class="col-val" style="font-size: 1.05em; font-weight: 800; color: #1a1a1a;">{val_str_nombre}</span></div>'

        if col_nombre_final in cols_a_mostrar: cols_a_mostrar.remove(col_nombre_final)

    if texto_advertencia:
        contenido_tarjeta += f'<div class="advertencia-cobro">⚠️ {texto_advertencia}</div>'

    mensaje_prep_impreso = False

    # 2. Columnas
    for col in cols_a_mostrar:
        val = fila_dict[col]
        if str(val).strip() != "":
            if es_col_precio(col) and extraer_monto_limpio(val) > 0:
                val_str = formatear_pesos(extraer_monto_limpio(val))
            else:
                val_str = str(val)

            contenido_tarjeta += f'<div class="row-item"><span class="col-name">{col}:</span> <span class="col-val">{val_str}</span></div>'

            if es_sin_prep_test and "ayuno" in normalizar(str(col)) and not mensaje_prep_impreso:
                contenido_tarjeta += f'<div class="row-item"><span class="col-name">Indicaciones Extras:</span> <span class="col-val">Examen sin preparación</span></div>'
                mensaje_prep_impreso = True

    if es_sin_prep_test and not mensaje_prep_impreso:
        has_explicit_prep = any("preparac" in normalizar(str(c)) or "indicac" in normalizar(str(c)) for c in cols_a_mostrar)
        if not has_explicit_prep:
            contenido_tarjeta += f'<div class="row-item"><span class="col-name">Indicaciones Extras:</span> <span class="col-val">Examen sin preparación</span></div>'

    if contenido_tarjeta.strip() != "":
        st.markdown(f'<div class="card-box">{contenido_tarjeta}</div>', unsafe_allow_html=True)


# ==============================================================================
# 🗂️ SISTEMA DE PESTAÑAS (TABS)
# ==============================================================================
if dict_hojas_excel is not None:

    with st.sidebar:
        st.markdown(f"**Usuario:** {st.session_state.usuario_actual}")
        with st.expander("🕒 Historial reciente"):
            eventos = leer_ultimos_eventos(15)
            if not eventos:
                st.caption("Sin actividad registrada todavía.")
            else:
                for ts, usuario, tipo, detalle in eventos:
                    etiqueta = "🔑 Login" if tipo == "login" else "🧮 Cotización"
                    st.caption(f"{ts} · {usuario} · {etiqueta}")
                    if detalle: st.caption(f"　{detalle}")

    # El aviso ahora se edita desde el menú "☰" de arriba; acá solo se muestra
    # el mensaje vigente, en el mismo lugar de siempre.
    aviso_actual = leer_aviso()
    if aviso_actual and aviso_actual.get("mensaje", "").strip():
        st.markdown(f'<div class="aviso-banner">{aviso_actual["mensaje"]}</div>', unsafe_allow_html=True)

    tab_buscador, tab_cotizador = st.tabs(["Buscador de Exámenes", "Cotizador Múltiple"])

    # ---------------------------------------------------------
    # 🌟 PESTAÑA 1: BUSCADOR GENERAL
    # ---------------------------------------------------------
    with tab_buscador:
        categorias_disponibles = sorted({str(c) for c in df_todas_las_hojas_cache['__categoria__'].unique() if str(c).strip()})
        with st.expander("Filtrar por categoría/sección (opcional)"):
            categorias_sel = st.multiselect("Categorías", categorias_disponibles, key="filtro_categorias", label_visibility="collapsed")

        # Streamlit no permite escribir en st.session_state["input_busqueda"] una vez que
        # ese widget ya fue instanciado en este mismo ciclo. Por eso las sugerencias usan
        # una clave de "espera" que se aplica ANTES de crear el text_input.
        if "_pendiente_busqueda" in st.session_state:
            st.session_state["input_busqueda"] = st.session_state.pop("_pendiente_busqueda")

        consulta_b = st.text_input("Búsqueda", key="input_busqueda", placeholder="", label_visibility="collapsed")

        if consulta_b.strip() and len(consulta_b.strip()) >= 2:
            q_norm_auto = normalizar(consulta_b)
            sugerencias = [n for n in lista_autocomplete if q_norm_auto in normalizar(n) and normalizar(n) != q_norm_auto][:8]
            if sugerencias:
                st.caption("¿Buscabas alguno de estos?")
                cols_sug = st.columns(4)
                for i, s in enumerate(sugerencias):
                    if cols_sug[i % 4].button(s, key=f"sug_{i}_{s}", use_container_width=True):
                        st.session_state["_pendiente_busqueda"] = s
                        st.rerun()

        if consulta_b.strip() or categorias_sel:
            if consulta_b.strip():
                palabras = [p for p in normalizar(consulta_b).split() if p]
                palabras = ["horario" if p == "horarios" else p for p in palabras]
                palabras_filtro = [p for p in palabras if p not in ["perfil", "hemograma", "examen", "prueba", "test", "de", "la", "el", "los", "las"]]

                def coincide_examen_general(fila):
                    hoja_origen = normalizar(str(fila.get("__hoja_origen__", "")))

                    q_norm = normalizar(consulta_b).strip()
                    if q_norm in ["horario", "horarios", "flujos", "horarios y flujos"]:
                        if "horario" in hoja_origen or "flujo" in hoja_origen:
                            nombre_examen_oculto = ""
                            col_n_local, _ = obtener_mejor_col_nombre(fila.to_dict())
                            if col_n_local: nombre_examen_oculto = str(fila.get(col_n_local, "")).lower()
                            if "cortisol" in nombre_examen_oculto: return False
                            return True
                        return False

                    texto_total = fila.get('__texto_busqueda__', "")

                    if not all(term in texto_total for term in palabras):
                        return False

                    return True

                df_resultados = df_todas_las_hojas_cache[df_todas_las_hojas_cache.apply(coincide_examen_general, axis=1)].copy()

                if df_resultados.empty:
                    df_fuzzy = busqueda_fuzzy(df_todas_las_hojas_cache, consulta_b)
                    if not df_fuzzy.empty:
                        st.info("No hubo coincidencias exactas. Mostrando resultados aproximados (revisa que el término esté bien escrito):")
                        df_resultados = df_fuzzy.copy()
            else:
                palabras, palabras_filtro = [], []
                df_resultados = df_todas_las_hojas_cache.copy()

            if categorias_sel:
                df_resultados = df_resultados[df_resultados['__categoria__'].isin(categorias_sel)]

            if '__texto_busqueda__' in df_resultados.columns:
                df_resultados = df_resultados.drop(columns=['__texto_busqueda__'])

            if df_resultados.empty:
                if consulta_b.strip():
                    st.warning(f"No se encontró información para '{consulta_b}'.")
                else:
                    st.warning("No hay exámenes en la categoría seleccionada.")
            else:
                def calcular_puntaje_general(fila):
                    puntaje = 10000
                    valores_validos = [normalizar(str(v)).strip() for c, v in fila.items() if c not in COLUMNAS_INTERNAS and str(v).strip() != ""]
                    for p in palabras:
                        if any(p == v for v in valores_validos): puntaje -= 5000
                        else: puntaje -= 500
                    return puntaje + len(" ".join(valores_validos))

                df_resultados['__puntaje__'] = df_resultados.apply(calcular_puntaje_general, axis=1)
                df_resultados = df_resultados.sort_values('__puntaje__')

                if len(df_resultados) > 150:
                    st.info(f"Se encontraron {len(df_resultados)} resultados; mostrando los 150 más relevantes. Refina tu búsqueda o usa el filtro de categoría para acotar.")
                resultados_mostrar = df_resultados.head(150)

                examenes_agrupados = {}
                for _, fila in resultados_mostrar.iterrows():
                    f_dict = fila.to_dict()
                    col_n, _ = obtener_mejor_col_nombre(f_dict)

                    n_val = str(f_dict[col_n]).strip() if col_n else ""
                    n_norm = normalizar_nombre_agrupacion(n_val)
                    hoja_origen_fila = normalizar(str(f_dict.get("__hoja_origen__", "")))
                    if "barnafi" in hoja_origen_fila or "bklab" in hoja_origen_fila:
                        # Agrupa usando el nombre de 'prestaciones' equivalente (si existe),
                        # aunque el nombre en Barnafi esté redactado distinto (ver
                        # _construir_alias_barnafi_prestaciones) -así se fusionan en una
                        # sola tarjeta en vez de mostrarse por separado.
                        n_norm = alias_barnafi_a_prest.get(n_norm, n_norm)
                    if n_norm not in examenes_agrupados: examenes_agrupados[n_norm] = {'filas': [], 'puntaje': f_dict['__puntaje__']}
                    examenes_agrupados[n_norm]['filas'].append(f_dict)

                grupos_ordenados = sorted(examenes_agrupados.values(), key=lambda x: x['puntaje'])

                for grupo in grupos_ordenados:
                    lista_filas = grupo['filas']
                    tiene_gine = any("ginecologico" in normalizar(str(f.get("__hoja_origen__", ""))) for f in lista_filas)
                    tiene_prest = any("prestac" in normalizar(str(f.get("__hoja_origen__", ""))) for f in lista_filas)
                    tiene_barnafi_bk = any("barnafi" in normalizar(str(f.get("__hoja_origen__", ""))) or "bklab" in normalizar(str(f.get("__hoja_origen__", ""))) for f in lista_filas)

                    if tiene_prest and tiene_barnafi_bk and not tiene_gine:
                        # Examen derivado al laboratorio BK: aparece en 'prestaciones' y en
                        # 'Examenes barnafi (BK)'. Se fusionan en una sola tarjeta (ver
                        # fusionar_prestacion_y_barnafi) en vez de mostrar dos duplicadas.
                        fila_prest = next((f for f in lista_filas if "prestac" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                        fila_barnafi = next((f for f in lista_filas if "barnafi" in normalizar(str(f.get("__hoja_origen__", ""))) or "bklab" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                        filas_otras = [f for f in lista_filas if f != fila_prest and f != fila_barnafi]

                        fila_consolidada = fusionar_prestacion_y_barnafi(fila_prest, fila_barnafi)

                        for f in filas_otras:
                            for c, v in f.items():
                                if c in COLUMNAS_INTERNAS or str(v).strip() == "" or es_col_nombre(c): continue
                                fila_consolidada[c] = v

                        renderizar_tarjeta(fila_consolidada, palabras, palabras_filtro)

                    elif tiene_gine and tiene_prest:
                        fila_gine = next((f for f in lista_filas if "ginecologico" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                        fila_prest = next((f for f in lista_filas if "prestac" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                        fila_barnafi = next((f for f in lista_filas if "barnafi" in normalizar(str(f.get("__hoja_origen__", ""))) or "bklab" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                        filas_otras = [f for f in lista_filas if f != fila_gine and f != fila_prest and f != fila_barnafi]

                        fila_consolidada = {}

                        for c, v in fila_prest.items():
                            if c == "__hoja_origen__" or c == "__puntaje__" or str(v).strip() == "": continue
                            if es_col_nombre(c) or es_col_precio(c) or es_col_tiempo(c) or es_col_contenedor(c) or es_col_muestra(c) or es_col_incluye(c): continue
                            fila_consolidada[c] = v

                        col_n_gine, _ = obtener_mejor_col_nombre(fila_gine)
                        if col_n_gine:
                            nombres_viejos = [c for c in fila_consolidada.keys() if es_col_nombre(c)]
                            for nv in nombres_viejos: del fila_consolidada[nv]
                            fila_consolidada[col_n_gine] = fila_gine[col_n_gine]

                        for c, v in fila_gine.items():
                            if c == "__hoja_origen__" or c == "__puntaje__" or str(v).strip() == "": continue
                            if es_col_precio(c) or es_col_tiempo(c) or es_col_contenedor(c) or es_col_muestra(c) or es_col_incluye(c):
                                fila_consolidada[c] = v

                        if fila_barnafi:
                            for c, v in fila_barnafi.items():
                                if str(v).strip() != "" and es_col_codigo(c) and c != "__hoja_origen__" and c != "__puntaje__":
                                    fila_consolidada[c] = v

                        for f in filas_otras:
                            for c, v in f.items():
                                if c == "__hoja_origen__" or c == "__puntaje__" or str(v).strip() == "" or es_col_nombre(c): continue
                                fila_consolidada[c] = v

                        renderizar_tarjeta(fila_consolidada, palabras, palabras_filtro)

                    else:
                        for f in lista_filas:
                            renderizar_tarjeta(f, palabras, palabras_filtro)

    # ---------------------------------------------------------
    # 🧮 PESTAÑA 2: COTIZADOR MÚLTIPLE
    # ---------------------------------------------------------
    with tab_cotizador:
        st.write("")
        tipo_pago = st.radio("Selecciona la Previsión:", ["Particular", "Fonasa"], horizontal=True)
        consulta_c = st.text_input("Cotizador", key="input_cotizador", placeholder="", label_visibility="collapsed")

        if consulta_c.strip():
            df_prestaciones = None
            for nombre, df in dict_hojas_excel.items():
                if "prestac" in normalizar(nombre): df_prestaciones = df; break
            if df_prestaciones is None: df_prestaciones = list(dict_hojas_excel.values())[0]

            def texto_completo_fila(fila):
                return normalizar(" ".join(
                    [str(c) for c in fila.index if c not in COLUMNAS_INTERNAS] +
                    [str(v) for c, v in fila.items() if c not in COLUMNAS_INTERNAS]
                ))

            # Nombre corto por fila, solo para el respaldo fuzzy: comparar una consulta
            # corta contra el nombre del examen (no contra la fila completa concatenada,
            # que arruina el ratio de similitud por diferencia de longitud).
            nombres_cortos_prestaciones = []
            for _, fila in df_prestaciones.iterrows():
                col_n, _ = obtener_mejor_col_nombre(fila.to_dict())
                nombre_completo = str(fila[col_n]) if col_n else ""
                nombres_cortos_prestaciones.append(normalizar(acortar_nombre_examen(nombre_completo)))

            # barnafi_por_clave_prest ya viene precalculado desde cargar_hojas_y_diccionario
            # (ver _construir_alias_barnafi_prestaciones): mapea el nombre normalizado de
            # 'prestaciones' a su fila equivalente en Barnafi, misma lógica que usa el
            # Buscador para fusionar tarjetas sin duplicar.

            st.markdown('<div class="cotizador-box">', unsafe_allow_html=True)

            nombres_examenes = [x.strip() for x in re.split(r',|\by\b', consulta_c) if x.strip()]
            total = 0
            items_cotizacion = []  # (nombre_real, precio, es_aproximado)

            for nombre in nombres_examenes:
                palabras = [p for p in normalizar(nombre).split() if p]
                palabras = ["horario" if p == "horarios" else p for p in palabras]

                def coincide_examen_suma(fila):
                    return all(term in texto_completo_fila(fila) for term in palabras)

                df_resultados = df_prestaciones[df_prestaciones.apply(coincide_examen_suma, axis=1)]
                es_aproximado = False

                if df_resultados.empty:
                    # Sin coincidencia exacta (posible error de tipeo): intenta con fuzzy matching
                    # contra el nombre corto de cada examen.
                    match = process.extractOne(normalizar(nombre), nombres_cortos_prestaciones, scorer=fuzz.WRatio, score_cutoff=70)
                    if match is not None:
                        _texto, _score, idx_pos = match
                        df_resultados = df_prestaciones.iloc[[idx_pos]]
                        es_aproximado = True

                if not df_resultados.empty:
                    mejor_fila = None
                    mejor_puntaje = 999999

                    for _, fila in df_resultados.iterrows():
                        puntaje = 10000
                        for p in palabras:
                            if any(p == normalizar(str(v)).strip() for c, v in fila.items() if c not in COLUMNAS_INTERNAS): puntaje -= 5000
                            else: puntaje -= 500

                        val0 = normalizar(str(fila.values[0]))
                        val1 = normalizar(str(fila.values[1])) if len(fila.values) > 1 else ""
                        puntaje += len(val0 + " " + val1)

                        if puntaje < mejor_puntaje:
                            mejor_puntaje = puntaje
                            mejor_fila = fila

                    precio = obtener_precio(mejor_fila, tipo_pago)
                    total += precio

                    # Si esta prestación también existe en Barnafi (mismo nombre normalizado),
                    # el nombre se toma fusionado (Barnafi manda en el nombre, el precio
                    # sigue viniendo de 'prestaciones' vía obtener_precio de arriba).
                    fila_para_nombre = mejor_fila.to_dict()
                    col_n_prest, _ = obtener_mejor_col_nombre(fila_para_nombre)
                    if col_n_prest:
                        clave_prest = normalizar_nombre_agrupacion(str(fila_para_nombre[col_n_prest]))
                        if clave_prest in barnafi_por_clave_prest:
                            fila_para_nombre = fusionar_prestacion_y_barnafi(mejor_fila, barnafi_por_clave_prest[clave_prest])

                    col_nombre_real, _ = obtener_mejor_col_nombre(fila_para_nombre)
                    nombre_real = str(fila_para_nombre.get(col_nombre_real, "")).strip() if col_nombre_real else ""

                    items_cotizacion.append((nombre_real or nombre.upper(), precio, es_aproximado))

                    if es_aproximado:
                        st.warning(f"**{nombre.upper()}** ➔ no hubo match exacto, se usó el más parecido: **{nombre_real}** ➔ **{formatear_pesos(precio)}**")
                    else:
                        st.success(f"**{nombre.upper()}** ({nombre_real}) ➔ **{formatear_pesos(precio)}**")

                    col_advertencia_cotiz = next((c for c, v in mejor_fila.items() if c not in COLUMNAS_INTERNAS and es_col_advertencia_cobro(c) and str(v).strip() != ""), None)
                    if col_advertencia_cotiz:
                        st.markdown(f'<div class="advertencia-cobro">⚠️ {mejor_fila[col_advertencia_cotiz]}</div>', unsafe_allow_html=True)
                else:
                    st.error(f"**{nombre.upper()}** ➔ No encontrado.")

            st.divider()
            st.markdown(f"<h2 style='text-align: center; color: #ffffff;'>TOTAL {tipo_pago.upper()}: {formatear_pesos(total)}</h2>", unsafe_allow_html=True)

            if items_cotizacion:
                # Streamlit re-ejecuta todo el script en cada interacción (incluso en otra
                # pestaña), así que sin esta guarda se reescribiría el mismo evento en el
                # historial en cada rerun. Solo registra cuando la cotización cambia de verdad.
                firma_cotizacion = f"{tipo_pago}|{consulta_c.strip().lower()}|{total}"
                if st.session_state.get("_ultima_cotizacion_registrada") != firma_cotizacion:
                    registrar_evento(
                        st.session_state.usuario_actual, "cotizacion",
                        f"{tipo_pago} | {len(items_cotizacion)} examen(es) | total {formatear_pesos(total)}"
                    )
                    st.session_state["_ultima_cotizacion_registrada"] = firma_cotizacion

                texto_wsp = f"Cotización Laboratorio Archipiélago ({tipo_pago}):\n" + \
                    "\n".join(f"- {n}: {formatear_pesos(p)}" for n, p, _a in items_cotizacion) + \
                    f"\n\nTOTAL {tipo_pago.upper()}: {formatear_pesos(total)}"
                url_wsp = "https://wa.me/?text=" + quote(texto_wsp)

                pdf_bytes = generar_pdf_cotizacion(items_cotizacion, total, tipo_pago, st.session_state.usuario_actual)

                col_pdf, col_wsp = st.columns(2)
                with col_pdf:
                    st.download_button(
                        "📄 Descargar PDF", data=pdf_bytes,
                        file_name=f"cotizacion_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf", use_container_width=True, type="primary",
                    )
                with col_wsp:
                    st.link_button("📲 Compartir por WhatsApp", url_wsp, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

else:
    detalle_error = st.session_state.get("_error_carga_datos")
    if USA_GOOGLE_SHEETS:
        st.error(
            "⚠️ No se pudo leer la planilla desde Google Sheets. Verifica que esté compartida "
            "como 'Cualquier usuario con el enlace: Lector' y que el `sheet_id` y los `gids` "
            "en Secrets sean correctos." + (f"\n\nDetalle: {detalle_error}" if detalle_error else "")
        )
    else:
        st.error(f"⚠️ Error Crítico: No se encontró el archivo base de datos ({ARCHIVO_EXCEL}). Asegúrate de que el archivo se encuentre en la misma carpeta." + (f"\n\nDetalle: {detalle_error}" if detalle_error else ""))

import base64
import os
import unicodedata
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Intentar importar librerías para lectura de imágenes (OCR)
try:
  from PIL import Image
  import pytesseract

  OCR_DISPONIBLE = True
except ImportError:
  OCR_DISPONIBLE = False

# ==============================================================================
# 🌟 CONFIGURACIÓN DE PÁGINA E ÍCONO OFICIAL ("logo lab.png" prioritario)
# ==============================================================================
icono_app = "🧪"
logo_encontrado = None

# Priorizar versión PNG para máxima compatibilidad con Android PWA / APK
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
    layout="centered",  # Interfaz limpia y centrada
)

# ==============================================================================
# 🛡️ ESTRATEGIA DE EXPERTO 1 & 2: INYECCIÓN JS EN EL DOM PADRE PARA BLOQUEAR RECARGA
# ==============================================================================
components.html(
    """
    <script>
    try {
        const win = window.parent;
        const doc = win.document;
        
        // 1. Bloquear comportamiento de rebote en el documento principal del teléfono
        doc.documentElement.style.overscrollBehavior = 'none';
        doc.body.style.overscrollBehavior = 'none';
        
        // 2. Aplicar touch-action al contenedor principal de Streamlit
        const container = doc.querySelector('[data-testid="stAppViewContainer"]');
        if (container) {
            container.style.overscrollBehavior = 'none';
            container.style.touchAction = 'pan-x pan-y';
        }
        
        // 3. Interceptar arrastre superior en el tope para evitar que Android recargue la app
        let touchStartY = 0;
        doc.addEventListener('touchstart', function(e) {
            touchStartY = e.touches[0].clientY;
        }, { passive: false });
        
        doc.addEventListener('touchmove', function(e) {
            const moveY = e.touches[0].clientY;
            const scrollTop = container ? container.scrollTop : doc.documentElement.scrollTop;
            // Si está arriba del todo y el usuario arrastra hacia abajo, cancelar el evento de recarga
            if (scrollTop <= 2 && moveY > touchStartY && (moveY - touchStartY) > 10) {
                e.preventDefault();
            }
        }, { passive: false });
    } catch(e) {
        console.log("Error configurando overscroll:", e);
    }
    </script>
    """,
    height=0,
    width=0,
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

# ==============================================================================
# 🛡️ ESTRATEGIA DE EXPERTO 3: PERSISTENCIA DE SESIÓN VÍA PARÁMETROS DE URL
# ==============================================================================
params = st.query_params
if "auth_token" in params and params["auth_token"] in USUARIOS:
  st.session_state.autenticado = True
  st.session_state.usuario_actual = params["auth_token"]

# --- Estilos CSS Minimalistas, Texto Responsivo para Móvil y Contraste ---
st.markdown(
    """
    <style>
    /* Fondo burdeo corporativo */
    .stApp {
        background-color: #6a1b29;
        color: #ffffff;
    }

    /* BLOQUEO TOTAL DE PULL-TO-REFRESH Y GESTOS DE REBOTE EN MÓVIL */
    html, body, .stApp, [data-testid="stAppViewContainer"], section.main {
        overscroll-behavior-y: none !important;
        overscroll-behavior: none !important;
        touch-action: pan-x pan-y !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* NEUTRALIZAR LA BARRA SUPERIOR BLANCA DE STREAMLIT PARA QUE NO ATRAPE EL TOQUE */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        height: 0px !important;
        min-height: 0px !important;
        pointer-events: none !important;
        z-index: 0 !important;
    }

    /* Ocultar mensaje por defecto "Press Enter to apply / submit form" */
    div[data-testid="InputInstructions"], 
    div[data-testid="stInputInstructions"],
    div[class*="InputInstructions"],
    div[data-testid="stTextInput"] small {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Textos generales en blanco */
    .stMarkdown, p, h1, h2, h3, h4, span, label {
        color: #ffffff !important;
    }

    /* TÍTULO PRINCIPAL ADAPTADO A PANTALLAS DE CELULAR */
    .title-text {
        color: #ffffff !important;
        text-align: center;
        font-weight: 800;
        font-size: clamp(1.6rem, 6.5vw, 2.2rem) !important;
        white-space: normal !important;
        line-height: 1.25 !important;
        margin-top: 5px;
        margin-bottom: 25px;
        width: 100%;
        padding: 0 10px;
    }

    /* CONTENEDOR BLANCO UNIFICADO PARA USUARIO, CONTRASEÑA Y BÚSQUEDA */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 25px !important;
        color: #000000 !important;
    }
    
    /* TEXTO INTERNO EN NEGRO ABSOLUTO */
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
        background-color: transparent !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        font-size: 16px !important;
        padding: 12px 18px !important;
    }
    
    div[data-baseweb="input"] input::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
    }

    /* PROTEGER EL BOTÓN DEL OJITO EN LA CONTRASEÑA */
    div[data-baseweb="input"] button, div[data-testid="stTextInput"] button {
        background-color: transparent !important;
        color: #333333 !important;
        border: none !important;
        width: auto !important;
        height: auto !important;
        box-shadow: none !important;
        padding: 0 12px !important;
        margin: 0 !important;
    }

    /* BOTONES DE ACCIÓN ("Cerrar Sesión", "Iniciar Sesión") */
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stButton"] > button[kind="primary"],
    button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background-color: #48121b !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        width: 100% !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
        margin-top: 5px !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stButton"] > button[kind="primary"]:hover,
    button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background-color: #6a1b29 !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* BOTÓN "+" ESTILO GEMINI */
    div[data-testid="stButton"] > button[kind="secondary"],
    button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        margin-top: 2px !important;
        padding: 0 !important;
    }
    
    div[data-testid="stButton"] > button[kind="secondary"]:hover,
    button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        transform: scale(1.05);
    }

    /* CARGADOR DE ARCHIVOS */
    [data-testid="stFileUploader"] section {
        background-color: #f8f9fa !important;
        border: 2px dashed #6a1b29 !important;
    }
    [data-testid="stFileUploader"] * {
        color: #1a1a1a !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #e9ecef !important;
        color: #000000 !important;
        border: 1px solid #ced4da !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #dee2e6 !important;
    }
    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span {
        color: #333333 !important;
    }

    /* RECUADRO BLANCO DE RESULTADOS */
    .card-box {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        padding: 22px 25px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        border-left: 8px solid #d4af37;
        box-shadow: 0 6px 15px rgba(0,0,0,0.25);
        margin-bottom: 20px;
        width: 100%;
    }

    .row-item {
        margin-bottom: 10px;
        font-size: 15px;
        line-height: 1.5;
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

    /* PANEL DEL BOTÓN "+" */
    .panel-img {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* ALERTAS */
    .stAlert {
        border-radius: 10px !important;
    }
    .stAlert p, .stAlert div {
        color: #1a1a1a !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Función para convertir imagen local en Base64 ---
def obtener_img_base64(ruta_imagen):
  with open(ruta_imagen, "rb") as f:
    return base64.b64encode(f.read()).decode()


# ==============================================================================
# 🚪 BOTÓN CERRAR SESIÓN EN LA ESQUINA SUPERIOR IZQUIERDA
# ==============================================================================
if st.session_state.autenticado:
  col_logout, col_resto = st.columns([1.2, 3.8])
  with col_logout:
    if st.button(
        "🚪 Cerrar Sesión",
        type="primary",
        use_container_width=True,
        help="Cerrar sesión y salir del sistema",
    ):
      st.session_state.autenticado = False
      st.session_state.usuario_actual = ""
      st.query_params.clear()  # Borra el token persistente de la URL
      st.rerun()

# --- Logo Clickeable e inyección de íconos PWA ---
if logo_encontrado:
  img_b64 = obtener_img_base64(logo_encontrado)
  mime = "image/png" if logo_encontrado.endswith(".png") else "image/webp"

  meta_iconos_html = f"""
    <head>
        <link rel="shortcut icon" href="data:{mime};base64,{img_b64}">
        <link rel="apple-touch-icon" href="data:{mime};base64,{img_b64}">
        <link rel="icon" type="{mime}" sizes="192x192" href="data:{mime};base64,{img_b64}">
        <link rel="icon" type="{mime}" sizes="512x512" href="data:{mime};base64,{img_b64}">
    </head>
    <div style="text-align: center; margin-bottom: 5px;">
        <a href="." target="_self" title="Haz clic en el logo para volver a empezar">
            <img src="data:{mime};base64,{img_b64}" style="width: 140px; max-width: 80%; height: auto; cursor: pointer; border: none;">
        </a>
    </div>
    """
  st.markdown(meta_iconos_html, unsafe_allow_html=True)
else:
  st.warning(
      "⚠️ Recuerda guardar tu archivo como **logo lab.png** en la carpeta del"
      " proyecto."
  )

# Título Limpio y Adaptable
st.markdown(
    '<h1 class="title-text">Laboratorio Archipiélago</h1>',
    unsafe_allow_html=True,
)

# ==============================================================================
# 🔐 PANTALLA DE INICIO DE SESIÓN (BLOQUEO DE SEGURIDAD)
# ==============================================================================
if not st.session_state.autenticado:
  st.markdown(
      "<h3 style='text-align: center; font-size: 1.3rem; margin-bottom:"
      " 20px;'>Acceso Restringido para Personal</h3>",
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
          # 🛡️ Guardar token seguro en URL para persistir ante recargas
          st.query_params["auth_token"] = usuario_input
          st.success("✅ Acceso correcto.")
          st.rerun()
        else:
          st.error("❌ Usuario o contraseña incorrectos.")

  # Detener completamente el código aquí si no han iniciado sesión
  st.stop()

# ==============================================================================
# 🔓 ZONA SEGURA: A PARTIR DE AQUÍ SOLO ACCEDE PERSONAL AUTORIZADO
# ==============================================================================

# --- Barra de búsqueda + Botón Símbolo "Más" (Estilo Gemini) ---
col_mas, col_input = st.columns([0.16, 0.84])

with col_mas:
  if st.button(
      "➕",
      type="secondary",
      help="Adjuntar imagen de orden o cámara",
  ):
    st.session_state.mostrar_panel_img = not st.session_state.mostrar_panel_img

with col_input:
  consulta = st.text_input(
      "Búsqueda",
      label_visibility="collapsed",
      placeholder="🔍 Buscar exámenes, códigos o indicaciones...",
  )

# --- Opciones desplegables de Imagen cuando se presiona "+" ---
texto_ocr = ""
if st.session_state.mostrar_panel_img:
  st.markdown('<div class="panel-img">', unsafe_allow_html=True)
  opcion_img = st.radio(
      "Selecciona origen de la imagen:",
      ["📁 Subir desde Galería", "📸 Acceder a cámara"],
      horizontal=True,
  )

  img_seleccionada = None
  if "Galería" in opcion_img:
    img_seleccionada = st.file_uploader(
        "Sube una foto u orden médica",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
    )
  else:
    img_seleccionada = st.camera_input("Enfoca la orden médica o pantalla")

  if img_seleccionada:
    if OCR_DISPONIBLE:
      try:
        img_pil = Image.open(img_seleccionada)
        texto_ocr = pytesseract.image_to_string(img_pil, lang="spa")
        st.success("✅ Imagen analizada. Buscando coincidencias...")
      except Exception:
        st.warning(
            "⚠️ No se pudo leer el texto de la imagen automáticamente. Revisa"
            " la configuración de OCR."
        )
    else:
      st.info(
          "💡 Para lectura automática de fotos instala Tesseract OCR en tu"
          " computador."
      )
  st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- Carga Automática e Infalible del Excel ---
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

if df_datos is None:
  st.error(
      f"❌ No se pudo cargar el archivo '{ARCHIVO_EXCEL}' en la carpeta del"
      " proyecto."
  )
  st.stop()


# --- Funciones de Normalización y Formateo ---
def normalizar(texto):
  if pd.isna(texto):
    return ""
  s = str(texto).lower()
  nfkd = unicodedata.normalize("NFKD", s)
  return "".join([c for c in nfkd if not unicodedata.combining(c)])


def formatear_valor(col, val):
  if pd.isna(val):
    return ""
  val_str = str(val).strip()
  if not val_str:
    return ""

  col_norm = normalizar(col)
  if any(
      palabra in col_norm
      for palabra in ["codigo", "cod", "id", "rut", "bklab", "item"]
  ):
    return val_str

  val_limpio = val_str[:-2] if val_str.endswith(".0") else val_str
  if val_limpio.startswith("0") and len(val_limpio) > 1:
    return val_str

  es_moneda = False
  val_test = val_limpio
  if val_test.startswith("$"):
    es_moneda = True
    val_test = val_test.replace("$", "").strip()

  if val_test.isdigit():
    num = int(val_test)
    if num >= 1000:
      num_fmt = f"{num:,}".replace(",", ".")
      return f"$ {num_fmt}" if es_moneda else num_fmt
    return f"$ {val_test}" if es_moneda else val_limpio

  return val_str


MODIFICADORES_CAMPOS = {
    "fonasa",
    "particular",
    "privado",
    "isapre",
    "isapres",
    "arancel",
    "aranceles",
    "precio",
    "precios",
    "valor",
    "valores",
    "copago",
    "copagos",
    "total",
    "bono",
    "costo",
    "costos",
    "pago",
    "pagos",
    "descuento",
    "horario",
    "horarios",
    "hora",
    "horas",
    "dia",
    "dias",
    "plazo",
    "plazos",
    "demora",
    "entrega",
    "proceso",
    "tiempo",
    "toma",
    "recepcion",
    "tubo",
    "tubos",
    "contenedor",
    "frasco",
    "muestra",
    "muestras",
    "volumen",
    "cantidad",
    "estabilidad",
    "ayuno",
    "preparacion",
    "indicacion",
    "indicaciones",
    "protocolo",
    "preanalitica",
    "requisito",
    "requisitos",
    "parametro",
    "parametros",
    "analito",
    "analitos",
    "incluye",
    "componentes",
    "codigo",
    "codigos",
    "cod",
    "bklab",
    "proactive",
    "sinonimo",
    "sinonimos",
    "comprobacion",
    "utilidad",
    "metodo",
    "tecnica",
}


def es_modificador_de_campo(palabra):
  if palabra in MODIFICADORES_CAMPOS:
    return True
  for col in df_datos.columns:
    col_norm = normalizar(col)
    if (
        palabra in col_norm
        and palabra not in ["examen", "prestacion", "nombre", "item"]
        and len(palabra) > 3
    ):
      return True
  return False


def mostrar_recuadro_blanco(columnas_a_mostrar):
  html_card = '<div class="card-box">'
  for col, val in columnas_a_mostrar:
    html_card += (
        f'<div class="row-item"><span class="col-name">{col}:</span> <span'
        f' class="col-val">{formatear_valor(col, val)}</span></div>'
    )
  html_card += "</div>"
  st.markdown(html_card, unsafe_allow_html=True)


# --- Lógica de Búsqueda (Texto o Texto leído de Imagen OCR) ---
texto_a_buscar = (
    consulta.strip() if consulta.strip() else texto_ocr.strip()
)

if texto_a_buscar:
  consulta_norm = normalizar(texto_a_buscar)
  palabras = [p for p in consulta_norm.split() if p]

  terminos_examen = [p for p in palabras if not es_modificador_de_campo(p)]
  filtros_especificos = [p for p in palabras if es_modificador_de_campo(p)]

  if not terminos_examen:
    terminos_examen = palabras
    filtros_especificos = []

  def coincide_examen(fila):
    texto_fila = " ".join([str(val) for val in fila.values])
    texto_fila_norm = normalizar(texto_fila)
    if len(terminos_examen) > 3:
      return any(
          term in texto_fila_norm for term in terminos_examen if len(term) > 3
      )
    return all(term in texto_fila_norm for term in terminos_examen)

  df_resultados = df_datos[df_datos.apply(coincide_examen, axis=1)]

  if df_resultados.empty:
    st.warning(
        f"⚠️ No se encontró información para **'{texto_a_buscar}'** en la"
        " base de datos."
    )
  else:
    tarjetas_mostradas = 0

    for idx, fila in df_resultados.iterrows():
      if filtros_especificos:
        columnas_a_mostrar = []
        encontro_filtro_real = False

        for col_idx, (col, val) in enumerate(fila.items()):
          val_str = str(val).strip()
          if not val_str:
            continue

          col_norm = normalizar(col)
          val_norm = normalizar(val_str)

          es_identificador = (
              col_idx in [0, 1]
              or "nombre" in col_norm
              or "examen" in col_norm
              or "prestacion" in col_norm
          )
          coincide_filtro = any(
              f in col_norm or f in val_norm for f in filtros_especificos
          )

          if coincide_filtro:
            encontro_filtro_real = True
            columnas_a_mostrar.append((col, val))
          elif es_identificador:
            columnas_a_mostrar.append((col, val))

        if encontro_filtro_real:
          mostrar_recuadro_blanco(columnas_a_mostrar)
          tarjetas_mostradas += 1

      else:
        columnas_a_mostrar = [
            (col, val)
            for col, val in fila.items()
            if str(val).strip() != ""
        ]
        mostrar_recuadro_blanco(columnas_a_mostrar)
        tarjetas_mostradas += 1

    if tarjetas_mostradas == 0 and filtros_especificos:
      st.info(
          f"No se encontraron datos de **'{' '.join(filtros_especificos)}'**"
          " para esta prestación. Mostrando toda la información disponible:"
      )
      for idx, fila in df_resultados.iterrows():
        columnas_a_mostrar = [
            (col, val)
            for col, val in fila.items()
            if str(val).strip() != ""
        ]
        mostrar_recuadro_blanco(columnas_a_mostrar)
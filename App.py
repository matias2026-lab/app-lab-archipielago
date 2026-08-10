import base64
import os
import unicodedata
import re
import pandas as pd
import streamlit as st

# ==============================================================================
# 🌟 CONFIGURACIÓN DE PÁGINA E ÍCONO OFICIAL
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
# 🎨 ESTILOS CSS PROFESIONALES (RECUADRO ÚNICO & ALTO CONTRASTE)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Bloqueo PWA Nativo */
    html, body, #root { position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow: hidden !important; overscroll-behavior: none !important; }
    [data-testid="stAppViewContainer"] { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow-y: auto !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important; background-color: #6a1b29 !important; }
    .stApp { background-color: #6a1b29; color: #ffffff; }
    
    /* 🚫 ELIMINAR BRANDING STREAMLIT Y "PRESS ENTER TO APPLY" 🚫 */
    footer, #MainMenu, header, .stActionButton, .stDeployButton { display: none !important; visibility: hidden !important; }
    [data-testid="InputInstructions"], [data-testid="stInputInstructions"], div[class*="InputInstructions"], .stTextInput small, .st-emotion-cache-1c7y2kd { display: none !important; opacity: 0 !important; visibility: hidden !important; }
    
    /* 🌟 RECUADRO ÚNICO PARA EL LOGIN (SIN CAPAS SOBREPUESTAS) */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border: 1.5px solid rgba(212, 175, 55, 0.5) !important;
        border-radius: 16px !important;
        padding: 25px 20px !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* FIX CONTRASTE TEXTOS LOGIN */
    .stTextInput label p, .stTextInput label, label { 
        color: #ffffff !important; 
        font-weight: 700 !important; 
        font-size: 16px !important; 
    }
    
    /* FIX BOTÓN CERRAR SESIÓN (ALTO CONTRASTE) */
    div[data-testid="stButton"] > button {
        background-color: #48121b !important;
        color: #ffffff !important;
        border: 1.5px solid #d4af37 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 8px 16px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: 0.2s;
    }
    div[data-testid="stButton"] > button:active, div[data-testid="stButton"] > button:hover {
        background-color: #6a1b29 !important;
        color: #d4af37 !important;
        border-color: #ffffff !important;
    }

    /* BARRA SUPERIOR */
    [data-testid="stHeader"] { background-color: transparent !important; visibility: visible !important; height: 50px !important; }
    
    /* BUSCADOR FIJO EN TECHO */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stTextInput"]) { position: -webkit-sticky !important; position: sticky !important; top: 10px !important; z-index: 9999 !important; background-color: #6a1b29 !important; padding: 10px 5px !important; border-radius: 15px !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important; }
    div[data-baseweb="input"], div[data-baseweb="base-input"] { background-color: #ffffff !important; border-radius: 25px !important; color: #000000 !important; border: none !important; }
    div[data-baseweb="input"] input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-size: 16px !important; padding: 12px 18px !important; }
    
    /* BOTÓN FORMULARIO LOGIN */
    div[data-testid="stFormSubmitButton"] > button { 
        background-color: #48121b !important; 
        color: #ffffff !important; 
        border-radius: 10px !important; 
        font-weight: 700 !important; 
        width: 100% !important; 
        border: 1.5px solid #d4af37 !important;
        margin-top: 10px !important;
    }
    
    /* TARJETAS DE RESULTADOS */
    .card-box { background-color: #ffffff !important; color: #1a1a1a !important; padding: 22px 25px; border-radius: 12px; border-left: 8px solid #d4af37; margin-bottom: 20px; box-shadow: 0 6px 15px rgba(0,0,0,0.25); }
    .row-item { margin-bottom: 10px; font-size: 15px; color: #1a1a1a !important; border-radius: 6px; padding: 4px 6px;}
    .col-name { font-weight: 700; color: #6a1b29 !important; }
    .col-val { color: #222222 !important; font-weight: 500; }
    .title-text { color: #ffffff !important; text-align: center; font-weight: 800; font-size: clamp(1.4rem, 6vw, 2rem) !important; margin-top: 5px; margin-bottom: 15px; }
    .cotizador-box { background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 2px solid #d4af37; }
    </style>
    """,
    unsafe_allow_html=True,
)

def obtener_img_base64(ruta_imagen):
  with open(ruta_imagen, "rb") as f:
    return base64.b64encode(f.read()).decode()

# ----------------- BARRA SUPERIOR (BOTÓN CERRAR SESIÓN) -----------------
if st.session_state.autenticado:
    col_espacio, col_salir = st.columns([0.6, 0.4])
    with col_salir:
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario_actual = ""
            st.query_params.clear()
            st.rerun()

if logo_encontrado:
  img_b64 = obtener_img_base64(logo_encontrado)
  mime = "image/png" if logo_encontrado.endswith(".png") else "image/webp"
  st.markdown(
      f'<div style="text-align: center; margin-bottom: 5px; margin-top: 5px;"><img src="data:{mime};base64,{img_b64}" style="width: 130px; max-width: 70%;"></div>',
      unsafe_allow_html=True,
  )

st.markdown('<h1 class="title-text">Laboratorio Archipiélago</h1>', unsafe_allow_html=True)

# ==============================================================================
# 🔐 PANTALLA DE INICIO DE SESIÓN (RECUADRO ÚNICO LIMPIO)
# ==============================================================================
if not st.session_state.autenticado:
  st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>Acceso Restringido</h3>", unsafe_allow_html=True)
  col_vacia1, col_login, col_vacia2 = st.columns([0.05, 2.9, 0.05])
  with col_login:
    with st.form("form_login", clear_on_submit=False):
      usuario_input = st.text_input("Usuario", placeholder="Ej: recepcion o tecnologo").strip()
      clave_input = st.text_input("Contraseña", type="password").strip()
      if st.form_submit_button("Iniciar Sesión", use_container_width=True):
        if usuario_input in USUARIOS and USUARIOS[usuario_input] == clave_input:
          st.session_state.autenticado = True
          st.session_state.usuario_actual = usuario_input
          st.rerun()
        else:
          st.error("❌ Credenciales incorrectas.")
  st.stop()

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
# 🛠️ FUNCIONES DE CLASIFICACIÓN DE COLUMNAS (CÓDIGOS VS PRECIOS)
# ==============================================================================
def es_columna_codigo(col_name):
    """Identifica columnas de códigos (Fonasa, Proactive) para mantenerlas intactas."""
    c = normalizar(str(col_name))
    return "codigo" in c or "proactive" in c

def es_columna_precio_fonasa(col_name):
    """Identifica la columna exacta del valor Copago Fonasa 2026."""
    c = normalizar(str(col_name))
    return ("copago" in c or "fonasa" in c) and ("2026" in c or "valor" in c or "precio" in c or "copago" in c) and not es_columna_codigo(col_name)

def es_columna_precio_particular(col_name):
    """Identifica la columna exacta del Valor Particular 2026."""
    c = normalizar(str(col_name))
    return ("particular" in c or "part" in c) and not es_columna_codigo(col_name)

def extraer_monto_limpio(val):
    """Extrae el número entero exacto ignorando letras, puntos o signos."""
    if pd.isna(val) or val == "": return 0
    s_clean = str(val).split('.')[0]
    nums = re.findall(r'\d+', s_clean)
    if nums:
        return int("".join(nums))
    return 0

def formatear_pesos(monto):
    """Aplica formato de dinero oficial chileno con punto de miles (Ej: $10.000)."""
    return f"${int(monto):,}".replace(",", ".")

def obtener_precio(fila, tipo_pago):
    """Saca el precio exclusivo de la columna correspondiente para la suma."""
    fila_dict = fila.to_dict()
    
    if tipo_pago == "Particular":
        for col, val in fila_dict.items():
            if es_columna_precio_particular(col):
                v = extraer_monto_limpio(val)
                if v > 0: return v
    else: # Fonasa
        for col, val in fila_dict.items():
            if es_columna_precio_fonasa(col):
                v = extraer_monto_limpio(val)
                if v > 0: return v
    return 0


# ==============================================================================
# 🔍 INTERFAZ PRINCIPAL: BUSCADOR Y COTIZADOR
# ==============================================================================

consulta = st.text_input("Búsqueda", label_visibility="collapsed", placeholder="Ej: Perfil hepático fonasa | O: suma venosa y TSH")
st.divider()

if consulta.strip() and df_datos is not None:
    
    # ---------------------------------------------------------
    # MODO 1: COTIZADOR AUTOMÁTICO (Escribiendo "suma ")
    # ---------------------------------------------------------
    if consulta.lower().startswith("suma "):
        st.markdown('<div class="cotizador-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>🛒 Cotizador de Exámenes</h3>", unsafe_allow_html=True)
        
        tipo_pago = st.radio("Selecciona la Previsión:", ["Particular", "Fonasa"], horizontal=True)
        
        # Limpieza de nombres de exámenes pedidos
        texto_examenes = consulta[5:] 
        nombres_examenes = [x.strip() for x in re.split(r',|\by\b', texto_examenes) if x.strip()]
        
        total = 0
        st.markdown("#### 📋 Detalle de Valores:")
        
        for nombre in nombres_examenes:
            palabras = [p for p in normalizar(nombre).split() if p]
            def coincide_examen(fila):
                texto_fila = normalizar(" ".join([str(c) for c in fila.index] + [str(v) for v in fila.values]))
                return all(term in texto_fila for term in palabras)
            
            df_resultados = df_datos[df_datos.apply(coincide_examen, axis=1)]
            
            if not df_resultados.empty:
                mejor_fila = df_resultados.iloc[0]
                precio = obtener_precio(mejor_fila, tipo_pago)
                total += precio
                
                # Nombre del examen rescatado
                nombre_real = str(mejor_fila.values[0]) if len(str(mejor_fila.values[0])) > 3 else str(mejor_fila.values[1])
                st.success(f"✅ **{nombre.title()}** ({nombre_real}) ➔ **{formatear_pesos(precio)}**")
            else:
                st.error(f"❌ **{nombre.title()}** ➔ No encontrado.")
                
        st.divider()
        st.markdown(f"<h2 style='text-align: center; color: #d4af37;'>TOTAL {tipo_pago.upper()}: {formatear_pesos(total)}</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # ---------------------------------------------------------
    # MODO 2: BÚSQUEDA NORMAL / "MODO LÁSER" POR ESPECIFICACIÓN
    # ---------------------------------------------------------
    else:
        palabras = [p for p in normalizar(consulta).split() if p]

        def coincide_examen(fila):
            texto_fila = normalizar(" ".join([str(c) for c in fila.index] + [str(v) for v in fila.values]))
            return all(term in texto_fila for term in palabras)

        df_resultados = df_datos[df_datos.apply(coincide_examen, axis=1)]

        if df_resultados.empty:
            st.warning(f"⚠️ No se encontró información para **'{consulta}'**.")
        else:
            resultados_mostrar = df_resultados.head(50)

            for _, fila in resultados_mostrar.iterrows():
                
                # 🎯 LÓGICA DE FILTRADO LÁSER DE COLUMNAS
                # Columnas esenciales que siempre van: Nombre del Examen + Códigos
                cols_esenciales = []
                for c in fila.index:
                    cn = normalizar(str(c))
                    if any(k in cn for k in ["prestac", "examen", "nombre", "codigo", "proactive", "descripcion"]):
                        cols_esenciales.append(c)

                # Verificar si el usuario escribió especificaciones en su búsqueda
                has_fonasa = "fonasa" in palabras
                has_particular = "particular" in palabras
                
                cols_especificas = []
                if has_fonasa and not has_particular:
                    for c in fila.index:
                        if es_columna_precio_fonasa(c): cols_especificas.append(c)
                elif has_particular and not has_fonasa:
                    for c in fila.index:
                        if es_columna_precio_particular(c): cols_especificas.append(c)
                else:
                    # Búsqueda general por palabra clave en título de columna
                    for c in fila.index:
                        cn = normalizar(str(c))
                        if any(term in cn for term in palabras if term not in ["perfil", "hemograma", "examen"]):
                            cols_especificas.append(c)

                # Definir columnas finales a mostrar en la tarjeta
                if cols_especificas:
                    cols_a_mostrar = list(dict.fromkeys(cols_esenciales + cols_especificas))
                else:
                    cols_a_mostrar = list(fila.index)

                # 💳 RENDERIZADO DE LA TARJETA
                html_card = '<div class="card-box">'
                for col in cols_a_mostrar:
                    val = fila[col]
                    
                    if str(val).strip():
                        # Si es columna de precio, formateamos con punto de miles ($10.000)
                        if (es_columna_precio_fonasa(col) or es_columna_precio_particular(col)) and extraer_monto_limpio(val) > 0:
                            val_str = formatear_pesos(extraer_monto_limpio(val))
                        else:
                            # Si es un CÓDIGO FONASA o PROACTIVE, se muestra tal cual (sin puntos ni $)
                            val_str = str(val)
                            
                        # Resaltador Visual Dorado para coincidencia
                        col_norm = normalizar(str(col))
                        val_norm = normalizar(str(val))
                        es_buscado = any(term in col_norm or term in val_norm for term in palabras)
                        estilo = "background-color: rgba(212, 175, 55, 0.15); border-left: 4px solid #d4af37;" if es_buscado else ""
                        
                        html_card += f'<div class="row-item" style="{estilo}"><span class="col-name">{col}:</span> <span class="col-val">{val_str}</span></div>'
                
                st.markdown(html_card + "</div>", unsafe_allow_html=True)
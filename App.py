import base64
import os
import unicodedata
import re
import pandas as pd
import streamlit as st

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
# 🎨 ESTILOS CSS PURIFICADOS (Login Limpio y Alto Contraste)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Bloqueo PWA Nativo */
    html, body, #root { position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow: hidden !important; overscroll-behavior: none !important; }
    [data-testid="stAppViewContainer"] { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow-y: auto !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important; background-color: #6a1b29 !important; }
    .stApp { background-color: #6a1b29; color: #ffffff; }
    
    /* 🚫 ELIMINAR BRANDING STREAMLIT 🚫 */
    footer, #MainMenu, header, .stActionButton, .stDeployButton { display: none !important; visibility: hidden !important; }
    [data-testid="InputInstructions"], [data-testid="stInputInstructions"], div[class*="InputInstructions"], .stTextInput small, .st-emotion-cache-1c7y2kd { display: none !important; opacity: 0 !important; visibility: hidden !important; }
    
    /* 🌟 RECUADRO ÚNICO PARA EL LOGIN (FONDO TRANSPARENTE) */
    div[data-testid="stForm"] {
        background-color: transparent !important;
        border: 2px solid #d4af37 !important;
        border-radius: 16px !important;
        padding: 25px 20px !important;
    }
    
    /* FIX CONTRASTE TEXTOS LOGIN */
    .stTextInput label p, .stTextInput label, label { 
        color: #ffffff !important; 
        font-weight: 700 !important; 
        font-size: 16px !important; 
    }
    
    /* FIX BOTÓN CERRAR SESIÓN Y LOGIN (ALTO CONTRASTE) */
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #48121b !important;
        color: #ffffff !important;
        border: 1.5px solid #d4af37 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 8px 16px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: 0.2s;
        width: 100% !important;
        margin-top: 10px !important;
    }
    div[data-testid="stButton"] > button:active, div[data-testid="stFormSubmitButton"] > button:active {
        background-color: #6a1b29 !important;
        color: #d4af37 !important;
        border-color: #ffffff !important;
    }

    /* BARRA SUPERIOR */
    [data-testid="stHeader"] { background-color: transparent !important; visibility: visible !important; height: 50px !important; }
    
    /* BUSCADOR PRINCIPAL */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stTextInput"]) { position: -webkit-sticky !important; position: sticky !important; top: 10px !important; z-index: 9999 !important; background-color: #6a1b29 !important; padding: 10px 5px !important; border-radius: 15px !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important; }
    div[data-baseweb="input"], div[data-baseweb="base-input"] { background-color: #ffffff !important; border-radius: 25px !important; color: #000000 !important; border: none !important; }
    div[data-baseweb="input"] input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-size: 16px !important; padding: 12px 18px !important; }
    
    /* TARJETAS DE RESULTADOS */
    .card-box { background-color: #ffffff !important; color: #1a1a1a !important; padding: 22px 25px; border-radius: 12px; border-left: 8px solid #d4af37; margin-bottom: 20px; box-shadow: 0 6px 15px rgba(0,0,0,0.25); }
    .row-item { margin-bottom: 10px; font-size: 15px; color: #1a1a1a !important; border-radius: 6px; padding: 4px 6px;}
    .col-name { font-weight: 700; color: #6a1b29 !important; }
    .col-val { color: #222222 !important; font-weight: 500; }
    .title-text { color: #ffffff !important; text-align: center; font-weight: 800; font-size: clamp(1.4rem, 6vw, 2rem) !important; margin-top: 5px; margin-bottom: 15px; }
    
    /* COTIZADOR INVISIBLE */
    .cotizador-box { margin-bottom: 20px; padding-top: 10px; }
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
# 🔐 PANTALLA DE INICIO DE SESIÓN
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
# 📂 CARGA DE DATOS SEPARADA POR HOJAS
# ==============================================================================
ARCHIVO_EXCEL = "APP lab archipielago 2.xlsx"

@st.cache_data(ttl=2)
def cargar_hojas_excel(ruta_archivo):
  if not os.path.exists(ruta_archivo): return None
  try:
    dict_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
    dict_limpio = {}
    for nombre_hoja, df in dict_hojas.items():
        df_clean = df.dropna(how="all").rename(columns=lambda c: str(c).strip()).fillna("")
        dict_limpio[nombre_hoja.strip()] = df_clean
    return dict_limpio
  except Exception: return None

dict_hojas_excel = cargar_hojas_excel(ARCHIVO_EXCEL)

def normalizar(texto):
  if pd.isna(texto): return ""
  return "".join([c for c in unicodedata.normalize("NFKD", str(texto).lower()) if not unicodedata.combining(c)])

def obtener_df_segun_modo(dict_hojas, es_modo_bk=False):
    if not dict_hojas: return None
    hoja_prestaciones = None
    hoja_bk = None
    
    for nombre, df in dict_hojas.items():
        n_norm = normalizar(nombre)
        if "barnafi" in n_norm or "bk" in n_norm:
            hoja_bk = df
        elif "prestac" in n_norm:
            hoja_prestaciones = df
            
    if es_modo_bk:
        if hoja_bk is not None: return hoja_bk
        return list(dict_hojas.values())[-1] 
    else:
        if hoja_prestaciones is not None: return hoja_prestaciones
        return list(dict_hojas.values())[0] 

# ==============================================================================
# 🛠️ MATEMÁTICA Y EXTRACCIÓN DE DINERO (¡CORREGIDO PARA CHILE!)
# ==============================================================================
def es_columna_precio_fonasa(col_name):
    """Busca estrictamente la columna 'COPAGO FONASA 2026'."""
    c = normalizar(str(col_name))
    return "copago" in c and "fonasa" in c

def es_columna_precio_particular(col_name):
    """Busca estrictamente la columna 'VALOR PARTICULAR 2026'."""
    c = normalizar(str(col_name))
    return "particular" in c

def extraer_monto_limpio(val):
    """
    CORRECCIÓN CRÍTICA: Convierte correctamente el formato "5.420" a 5420.
    Evita que Python lo lea como decimal (5.42 -> 5 pesos).
    """
    if pd.isna(val) or str(val).strip() == "": return 0
    
    # Si ya es un número nativo en Python (int o float sin formato de texto)
    if isinstance(val, (int, float)):
        return int(val)
        
    # Si viene como texto (ej. "5.420" o "$ 5.420")
    s_val = str(val).replace('$', '').replace(' ', '').strip()
    
    # Quitamos posibles decimales nulos que deja pandas al leer (ej: "15000.0")
    if s_val.endswith('.0'): s_val = s_val[:-2]
    if s_val.endswith('.00'): s_val = s_val[:-3]
    
    # ¡AQUÍ ESTABA EL TRUCO! Quitamos los puntos de miles (chilenos)
    s_val = s_val.replace('.', '')
    
    # Si hubiera una coma de centavos reales (ej: 15000,50), cortamos en la coma
    if ',' in s_val:
        s_val = s_val.split(',')[0]
        
    try:
        return int(s_val)
    except ValueError:
        return 0

def formatear_pesos(monto):
    return f"${int(monto):,}".replace(",", ".")

def obtener_precio(fila, tipo_pago):
    """Busca y extrae el precio de la columna EXACTA solicitada."""
    fila_dict = fila.to_dict()
    if tipo_pago == "Particular":
        for col, val in fila_dict.items():
            if es_columna_precio_particular(col):
                return extraer_monto_limpio(val)
    else: # Fonasa
        for col, val in fila_dict.items():
            if es_columna_precio_fonasa(col):
                return extraer_monto_limpio(val)
    return 0

# ==============================================================================
# 🔍 INTERFAZ PRINCIPAL: BUSCADOR Y COTIZADOR
# ==============================================================================

consulta = st.text_input("Búsqueda", label_visibility="collapsed", placeholder="Ej: TSH | TSH BK | O: suma venosa y TSH")
st.divider()

if consulta.strip() and dict_hojas_excel is not None:
    
    query_clean = consulta.strip()
    
    # Detección del comando "BK" al final
    es_modo_bk = bool(re.search(r'(?i)\s+bk$', query_clean) or query_clean.lower() == "bk")
    
    if es_modo_bk:
        query_busqueda = re.sub(r'(?i)\s+bk$', '', query_clean).strip()
    else:
        query_busqueda = query_clean
        
    df_actual = obtener_df_segun_modo(dict_hojas_excel, es_modo_bk=es_modo_bk)

    # ---------------------------------------------------------
    # MODO 1: COTIZADOR AUTOMÁTICO ("suma ...") 
    # ---------------------------------------------------------
    if query_busqueda.lower().startswith("suma "):
        df_prestaciones = obtener_df_segun_modo(dict_hojas_excel, es_modo_bk=False)
        
        st.markdown('<div class="cotizador-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0; color:#d4af37;'>Cotizador de Exámenes</h3>", unsafe_allow_html=True)
        
        tipo_pago = st.radio("Selecciona la Previsión:", ["Particular", "Fonasa"], horizontal=True)
        
        texto_examenes = query_busqueda[5:] 
        nombres_examenes = [x.strip() for x in re.split(r',|\by\b', texto_examenes) if x.strip()]
        
        total = 0
        
        for nombre in nombres_examenes:
            palabras = [p for p in normalizar(nombre).split() if p]
            def coincide_examen(fila):
                texto_fila = normalizar(" ".join([str(c) for c in fila.index] + [str(v) for v in fila.values]))
                return all(term in texto_fila for term in palabras)
            
            df_resultados = df_prestaciones[df_prestaciones.apply(coincide_examen, axis=1)]
            
            if not df_resultados.empty:
                # Algoritmo de relevancia
                mejor_fila = None
                mejor_puntaje = 999999
                
                for _, fila in df_resultados.iterrows():
                    val0 = normalizar(str(fila.values[0]))
                    val1 = normalizar(str(fila.values[1])) if len(fila.values) > 1 else ""
                    val_texto = val0 + " " + val1
                    
                    puntaje = len(val_texto)
                    for p in palabras:
                        if p == val0 or p == val1: puntaje -= 1000
                        elif f" {p} " in f" {val_texto} ": puntaje -= 500
                        
                    if puntaje < mejor_puntaje:
                        mejor_puntaje = puntaje
                        mejor_fila = fila

                precio = obtener_precio(mejor_fila, tipo_pago)
                total += precio
                
                nombre_real = str(mejor_fila.values[0]) if len(str(mejor_fila.values[0])) > 5 else str(mejor_fila.values[1])
                st.success(f"✅ **{nombre.upper()}** ({nombre_real}) ➔ **{formatear_pesos(precio)}**")
            else:
                st.error(f"❌ **{nombre.upper()}** ➔ No encontrado.")
                
        st.divider()
        st.markdown(f"<h2 style='text-align: center; color: #ffffff;'>TOTAL {tipo_pago.upper()}: {formatear_pesos(total)}</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # ---------------------------------------------------------
    # MODO 2: BÚSQUEDA NORMAL O MODO BK
    # ---------------------------------------------------------
    else:
        palabras = [p for p in normalizar(query_busqueda).split() if p]

        def coincide_examen(fila):
            texto_fila = normalizar(" ".join([str(c) for c in fila.index] + [str(v) for v in fila.values]))
            return all(term in texto_fila for term in palabras)

        if df_actual is not None:
            df_resultados = df_actual[df_actual.apply(coincide_examen, axis=1)]
        else:
            df_resultados = pd.DataFrame()

        if df_resultados.empty:
            origen_str = "en Exámenes BKLAB" if es_modo_bk else "en Prestaciones"
            st.warning(f"⚠️ No se encontró información para **'{query_busqueda}'** {origen_str}.")
        else:
            def calcular_puntaje(fila):
                val0 = normalizar(str(fila.values[0]))
                val1 = normalizar(str(fila.values[1])) if len(fila.values) > 1 else ""
                val_texto = val0 + " " + val1
                puntaje = len(val_texto)
                for p in palabras:
                    if p == val0 or p == val1: puntaje -= 1000
                    elif f" {p} " in f" {val_texto} ": puntaje -= 500
                return puntaje

            df_resultados['__puntaje__'] = df_resultados.apply(calcular_puntaje, axis=1)
            df_resultados = df_resultados.sort_values('__puntaje__').drop(columns=['__puntaje__'])
            
            resultados_mostrar = df_resultados.head(50)

            if es_modo_bk:
                st.info("🧪 **Mostrando información de Ficha Técnica BKLAB / Barnafi**")

            for _, fila in resultados_mostrar.iterrows():
                
                cols_esenciales = []
                for c in fila.index:
                    cn = normalizar(str(c))
                    if any(k in cn for k in ["prestac", "examen", "nombre", "codigo", "proactive", "bklab", "descripcion"]):
                        cols_esenciales.append(c)

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
                    for c in fila.index:
                        cn = normalizar(str(c))
                        if any(term in cn for term in palabras if term not in ["perfil", "hemograma", "examen"]):
                            cols_especificas.append(c)

                if cols_especificas:
                    cols_a_mostrar = list(dict.fromkeys(cols_esenciales + cols_especificas))
                else:
                    cols_a_mostrar = list(fila.index)

                # Ocultar columna de sinónimos de la visualización
                cols_a_mostrar = [c for c in cols_a_mostrar if "sinonimo" not in normalizar(str(c)) and "sinónimo" not in normalizar(str(c))]

                html_card = '<div class="card-box">'
                for col in cols_a_mostrar:
                    val = fila[col]
                    
                    if str(val).strip():
                        # Si es columna de plata, le aplicamos el formato
                        if (es_columna_precio_fonasa(col) or es_columna_precio_particular(col)) and extraer_monto_limpio(val) > 0:
                            val_str = formatear_pesos(extraer_monto_limpio(val))
                        else:
                            val_str = str(val)
                            
                        col_norm = normalizar(str(col))
                        val_norm = normalizar(str(val))
                        es_buscado = any(term in col_norm or term in val_norm for term in palabras)
                        estilo = "background-color: rgba(212, 175, 55, 0.15); border-left: 4px solid #d4af37;" if es_buscado else ""
                        
                        html_card += f'<div class="row-item" style="{estilo}"><span class="col-name">{col}:</span> <span class="col-val">{val_str}</span></div>'
                
                st.markdown(html_card + "</div>", unsafe_allow_html=True)
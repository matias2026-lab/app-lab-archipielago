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
# ----- MEJORA APLICADA: Uso de st.secrets con respaldo local -----
try:
    USUARIOS = st.secrets["USUARIOS"]
except Exception:
    USUARIOS = {
      "659": "12345",
    }
# -----------------------------------------------------------------

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = ""

params = st.query_params
if "auth_token" in params and params["auth_token"] in USUARIOS:
  st.session_state.autenticado = True
  st.session_state.usuario_actual = params["auth_token"]

# ==============================================================================
# 🎨 ESTILOS CSS PURIFICADOS (PESTAÑAS SIEMPRE AMARILLAS)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Fondo general */
    html, body, #root { position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow: hidden !important; overscroll-behavior: none !important; }
    [data-testid="stAppViewContainer"] { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow-y: auto !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important; background-color: #6a1b29 !important; }
    .stApp { background-color: #6a1b29; color: #ffffff; }
    
    /* Ocultar elementos innecesarios */
    footer, #MainMenu, header, .stActionButton, .stDeployButton { display: none !important; visibility: hidden !important; }
    [data-testid="InputInstructions"], [data-testid="stInputInstructions"] { display: none !important; }
    
    /* Formulario de Login */
    div[data-testid="stForm"] { background-color: transparent !important; border: 2px solid #d4af37 !important; border-radius: 16px !important; padding: 25px 20px !important; }
    .stTextInput label p, .stTextInput label, label { color: #ffffff !important; font-weight: 700 !important; font-size: 16px !important; }
    
    /* Botones */
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #48121b !important; color: #ffffff !important; border: 1.5px solid #d4af37 !important; border-radius: 10px !important;
        font-weight: 700 !important; font-size: 15px !important; padding: 8px 16px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: 0.2s; width: 100% !important; margin-top: 10px !important;
    }
    div[data-testid="stButton"] > button:active, div[data-testid="stFormSubmitButton"] > button:active { background-color: #6a1b29 !important; color: #d4af37 !important; border-color: #ffffff !important; }

    /* 🟡 PESTAÑAS (TABS) - AMARILLO/DORADO PERMANENTE, INCLUSO INACTIVAS */
    div[data-testid="stTabs"] button,
    div[data-testid="stTabs"] button p, 
    div[data-testid="stTabs"] button span {
        color: #d4af37 !important;
        font-size: 1.15em !important;
        font-weight: 800 !important;
    }
    /* Estilo de la pestaña seleccionada */
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 3px solid #d4af37 !important;
    }
    
    /* 🟡 Radio Buttons (Particular, Fonasa) - AMARILLO/DORADO */
    div[role="radiogroup"] label p, 
    div[role="radiogroup"] label span,
    div[role="radiogroup"] label div {
        color: #d4af37 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    div[data-testid="stRadio"] > label p,
    div[data-testid="stRadio"] > label {
        color: #ffffff !important;
    }
    
    /* Inputs de texto */
    div[data-baseweb="input"], div[data-baseweb="base-input"] { 
        background-color: #ffffff !important; 
        border-radius: 25px !important; 
        border: none !important; 
    }
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input, input[type="text"], input[type="password"] { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        caret-color: #000000 !important; 
        font-size: 16px !important; 
        padding: 12px 18px !important; 
        background-color: #ffffff !important;
    }
    
    /* Tarjetas de resultados */
    .card-box { background-color: #ffffff !important; color: #1a1a1a !important; padding: 22px 25px; border-radius: 12px; border-left: 8px solid #d4af37; margin-bottom: 20px; box-shadow: 0 6px 15px rgba(0,0,0,0.25); }
    .row-item { margin-bottom: 10px; font-size: 15px; color: #1a1a1a !important; border-radius: 6px; padding: 4px 6px;}
    .col-name { font-weight: 700; color: #6a1b29 !important; }
    .col-val { color: #222222 !important; font-weight: 500; }
    .title-text { color: #ffffff !important; text-align: center; font-weight: 800; font-size: clamp(1.4rem, 6vw, 2rem) !important; margin-top: 5px; margin-bottom: 15px; }
    
    .cotizador-box { margin-bottom: 20px; padding-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

def obtener_img_base64(ruta_imagen):
  with open(ruta_imagen, "rb") as f:
    return base64.b64encode(f.read()).decode()

# ----------------- BARRA SUPERIOR -----------------
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
  st.markdown(f'<div style="text-align: center; margin-bottom: 5px; margin-top: 5px;"><img src="data:{mime};base64,{img_b64}" style="width: 130px; max-width: 70%;"></div>', unsafe_allow_html=True)

st.markdown('<h1 class="title-text">Laboratorio Archipiélago</h1>', unsafe_allow_html=True)

# ==============================================================================
# 🔐 PANTALLA DE INICIO DE SESIÓN
# ==============================================================================
if not st.session_state.autenticado:
  col_vacia1, col_login, col_vacia2 = st.columns([0.05, 2.9, 0.05])
  with col_login:
    with st.form("form_login", clear_on_submit=False):
      usuario_input = st.text_input("Usuario", placeholder="").strip()
      clave_input = st.text_input("Contraseña", type="password").strip()
      if st.form_submit_button("Iniciar Sesión", use_container_width=True):
        if usuario_input in USUARIOS and USUARIOS[usuario_input] == clave_input:
          st.session_state.autenticado = True
          st.session_state.usuario_actual = usuario_input
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
    return "archipielago" in cn or "nombre" in cn or "prestacion" in cn or "examen" in cn or "unnamed" in cn

# ==============================================================================
# 📂 CARGA DE DATOS MULTI-HOJA Y DICCIONARIO
# ==============================================================================
ARCHIVO_EXCEL = "APP lab archipielago 2.xlsx"

@st.cache_data(ttl=2)
def cargar_hojas_y_diccionario(ruta_archivo):
    # ----- MEJORA APLICADA: Validar retorno de 3 elementos -----
    if not os.path.exists(ruta_archivo): return None, None, None
    try:
        dict_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
        
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
            
        # ----- MEJORA APLICADA: Pre-concatenación y Pre-normalización para búsquedas súper rápidas -----
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
            
            # Verificamos manualmente con diccionario local
            for term in diccionario["sin_preparacion"]:
                norm = normalizar(nombre_oculto)
                if (len(term) <= 4 and re.search(rf'\b{term}\b', norm)) or (len(term) > 4 and term in norm):
                    texto += " examen examenes sin preparacion no requiere preparacion indicaciones"
                    break

            return texto

        df_todas['__texto_busqueda__'] = df_todas.apply(pre_calcular_texto, axis=1)
        # -----------------------------------------------------------------------------------------------
            
        return dict_limpio, diccionario, df_todas
    except Exception: return None, None, None

# Recibimos el tercer dataframe cacheado
dict_hojas_excel, diccionario_virtual, df_todas_las_hojas_cache = cargar_hojas_y_diccionario(ARCHIVO_EXCEL)

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

def obtener_mejor_col_nombre(f_dict):
    posibles = [c for c in f_dict.keys() if es_col_nombre(c) and c != "__hoja_origen__" and str(f_dict[c]).strip() != "" and "sinonimo" not in normalizar(str(c))]
    for c in posibles:
        if "archipielago" in normalizar(str(c)): return c, True
    for c in posibles:
        if "nombre" in normalizar(str(c)) or "prestacion" in normalizar(str(c)): return c, True
    if posibles: return posibles[0], True
    
    for c in f_dict.keys():
        if c != "__hoja_origen__" and str(f_dict[c]).strip() != "": return c, False
    return None, False

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

# ==============================================================================
# 🎨 RENDERIZADOR GRÁFICO DE TARJETAS
# ==============================================================================
def renderizar_tarjeta(fila_dict, palabras, palabras_filtro):
    
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
        cols_a_mostrar = [c for c in fila_dict.keys() if c != "__hoja_origen__" and c != "__puntaje__"]

    cols_filtradas = []
    for c in cols_a_mostrar:
        if c == "__hoja_origen__" or c == "__puntaje__": continue
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
    
    tab_buscador, tab_cotizador = st.tabs(["Buscador de Exámenes", "Cotizador Múltiple"])

    # ---------------------------------------------------------
    # 🌟 PESTAÑA 1: BUSCADOR GENERAL
    # ---------------------------------------------------------
    with tab_buscador:
        consulta_b = st.text_input("Búsqueda", key="input_busqueda", placeholder="", label_visibility="collapsed")
        
        if consulta_b.strip():
            palabras = [p for p in normalizar(consulta_b).split() if p]
            # ----- MEJORA APLICADA: Unificar 'horarios' para resolver el bug visual -----
            palabras = ["horario" if p == "horarios" else p for p in palabras]
            # --------------------------------------------------------------------------
            palabras_filtro = [p for p in palabras if p not in ["perfil", "hemograma", "examen", "prueba", "test", "de", "la", "el", "los", "las"]]
            
            # Usamos la data ya procesada desde el caché
            def coincide_examen_general(fila):
                hoja_origen = normalizar(str(fila.get("__hoja_origen__", "")))

                # ----- MEJORA APLICADA: Añadir .strip() para evitar fallos si el usuario da un espacio extra -----
                q_norm = normalizar(consulta_b).strip()
                if q_norm in ["horario", "horarios", "flujos", "horarios y flujos"]:
                    if "horario" in hoja_origen or "flujo" in hoja_origen:
                        nombre_examen_oculto = ""
                        col_n_local, _ = obtener_mejor_col_nombre(fila.to_dict())
                        if col_n_local: nombre_examen_oculto = str(fila.get(col_n_local, "")).lower()
                        if "cortisol" in nombre_examen_oculto: return False
                        return True
                    return False

                # ----- MEJORA APLICADA: Búsqueda súper rápida usando texto pre-calculado -----
                texto_total = fila.get('__texto_busqueda__', "")
                
                if not all(term in texto_total for term in palabras):
                    return False
                    
                return True

            df_resultados = df_todas_las_hojas_cache[df_todas_las_hojas_cache.apply(coincide_examen_general, axis=1)].copy()
            
            # ----- MEJORA APLICADA: Ocultamos rastro del caché para no desarmar los renderizados de tu código original -----
            if '__texto_busqueda__' in df_resultados.columns:
                df_resultados = df_resultados.drop(columns=['__texto_busqueda__'])

            if df_resultados.empty:
                st.warning(f"No se encontró información para '{consulta_b}'.")
            else:
                def calcular_puntaje_general(fila):
                    puntaje = 10000
                    valores_validos = [normalizar(str(v)).strip() for c, v in fila.items() if c != "__hoja_origen__" and str(v).strip() != ""]
                    for p in palabras:
                        if any(p == v for v in valores_validos): puntaje -= 5000
                        else: puntaje -= 500
                    return puntaje + len(" ".join(valores_validos))

                df_resultados['__puntaje__'] = df_resultados.apply(calcular_puntaje_general, axis=1)
                df_resultados = df_resultados.sort_values('__puntaje__')
                resultados_mostrar = df_resultados.head(150)

                examenes_agrupados = {}
                for _, fila in resultados_mostrar.iterrows():
                    f_dict = fila.to_dict()
                    col_n, _ = obtener_mejor_col_nombre(f_dict)
                    
                    n_val = str(f_dict[col_n]).strip() if col_n else ""
                    n_norm = normalizar_nombre_agrupacion(n_val)
                    if n_norm not in examenes_agrupados: examenes_agrupados[n_norm] = {'filas': [], 'puntaje': f_dict['__puntaje__']}
                    examenes_agrupados[n_norm]['filas'].append(f_dict)
                
                grupos_ordenados = sorted(examenes_agrupados.values(), key=lambda x: x['puntaje'])
                
                for grupo in grupos_ordenados:
                    lista_filas = grupo['filas']
                    tiene_gine = any("ginecologico" in normalizar(str(f.get("__hoja_origen__", ""))) for f in lista_filas)
                    tiene_prest = any("prestac" in normalizar(str(f.get("__hoja_origen__", ""))) for f in lista_filas)

                    if tiene_gine and tiene_prest:
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

            st.markdown('<div class="cotizador-box">', unsafe_allow_html=True)
            
            nombres_examenes = [x.strip() for x in re.split(r',|\by\b', consulta_c) if x.strip()]
            total = 0
            
            for nombre in nombres_examenes:
                palabras = [p for p in normalizar(nombre).split() if p]
                # ----- MEJORA APLICADA: Unificar 'horarios' para resolver el bug visual también en cotizador -----
                palabras = ["horario" if p == "horarios" else p for p in palabras]
                # -------------------------------------------------------------------------------------------------

                def coincide_examen_suma(fila):
                    texto_fila = normalizar(" ".join([str(c) for c in fila.index if c != "__hoja_origen__" and c != "__puntaje__"] + [str(v) for c, v in fila.items() if c != "__hoja_origen__" and c != "__puntaje__"]))
                    return all(term in texto_fila for term in palabras)
                
                df_resultados = df_prestaciones[df_prestaciones.apply(coincide_examen_suma, axis=1)]
                
                if not df_resultados.empty:
                    mejor_fila = None
                    mejor_puntaje = 999999
                    
                    for _, fila in df_resultados.iterrows():
                        puntaje = 10000
                        for p in palabras:
                            if any(p == normalizar(str(v)).strip() for c, v in fila.items() if c != "__hoja_origen__" and c != "__puntaje__"): puntaje -= 5000
                            else: puntaje -= 500
                                
                        val0 = normalizar(str(fila.values[0]))
                        val1 = normalizar(str(fila.values[1])) if len(fila.values) > 1 else ""
                        puntaje += len(val0 + " " + val1)
                            
                        if puntaje < mejor_puntaje:
                            mejor_puntaje = puntaje
                            mejor_fila = fila

                    precio = obtener_precio(mejor_fila, tipo_pago)
                    total += precio
                    
                    nombre_real = ""
                    for c in mejor_fila.index:
                        if c != "__hoja_origen__" and c != "__puntaje__" and "archipielago" in normalizar(str(c)): nombre_real = str(mejor_fila[c]); break
                    if not nombre_real:
                        for c in mejor_fila.index:
                            if c != "__hoja_origen__" and c != "__puntaje__" and str(mejor_fila[c]).strip() != "":
                                nombre_real = str(mejor_fila[c])
                                if len(nombre_real) > 5: break

                    st.success(f"**{nombre.upper()}** ({nombre_real}) ➔ **{formatear_pesos(precio)}**")
                else:
                    st.error(f"**{nombre.upper()}** ➔ No encontrado.")
                    
            st.divider()
            st.markdown(f"<h2 style='text-align: center; color: #ffffff;'>TOTAL {tipo_pago.upper()}: {formatear_pesos(total)}</h2>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ----- MEJORA APLICADA: Manejo visual en caso de que falte el Excel en lugar de quedar en blanco -----
else:
    st.error("⚠️ Error Crítico: No se encontró el archivo base de datos (APP lab archipielago 2.xlsx). Asegúrate de que el archivo se encuentre en la misma carpeta.")
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
    "659": "12345",
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
# 🎨 ESTILOS CSS PURIFICADOS
# ==============================================================================
st.markdown(
    """
    <style>
    /* Bloqueo PWA Nativo */
    html, body, #root { position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow: hidden !important; overscroll-behavior: none !important; }
    [data-testid="stAppViewContainer"] { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; overflow-y: auto !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important; background-color: #6a1b29 !important; }
    .stApp { background-color: #6a1b29; color: #ffffff; }
    
    footer, #MainMenu, header, .stActionButton, .stDeployButton { display: none !important; visibility: hidden !important; }
    [data-testid="InputInstructions"], [data-testid="stInputInstructions"], div[class*="InputInstructions"], .stTextInput small, .st-emotion-cache-1c7y2kd { display: none !important; opacity: 0 !important; visibility: hidden !important; }
    
    div[data-testid="stForm"] { background-color: transparent !important; border: 2px solid #d4af37 !important; border-radius: 16px !important; padding: 25px 20px !important; }
    .stTextInput label p, .stTextInput label, label { color: #ffffff !important; font-weight: 700 !important; font-size: 16px !important; }
    
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #48121b !important; color: #ffffff !important; border: 1.5px solid #d4af37 !important; border-radius: 10px !important;
        font-weight: 700 !important; font-size: 15px !important; padding: 8px 16px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: 0.2s; width: 100% !important; margin-top: 10px !important;
    }
    div[data-testid="stButton"] > button:active, div[data-testid="stFormSubmitButton"] > button:active { background-color: #6a1b29 !important; color: #d4af37 !important; border-color: #ffffff !important; }

    [data-testid="stHeader"] { background-color: transparent !important; visibility: visible !important; height: 50px !important; }
    
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stTextInput"]) { position: -webkit-sticky !important; position: sticky !important; top: 10px !important; z-index: 9999 !important; background-color: #6a1b29 !important; padding: 10px 5px !important; border-radius: 15px !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important; margin-bottom: 20px !important;}
    div[data-baseweb="input"], div[data-baseweb="base-input"] { background-color: #ffffff !important; border-radius: 25px !important; color: #000000 !important; border: none !important; }
    div[data-baseweb="input"] input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-size: 16px !important; padding: 12px 18px !important; }
    
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
  st.markdown(
      f'<div style="text-align: center; margin-bottom: 5px; margin-top: 5px;"><img src="data:{mime};base64,{img_b64}" style="width: 130px; max-width: 70%;"></div>',
      unsafe_allow_html=True,
  )

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
          st.error("❌ Credenciales incorrectas.")
  st.stop()

# ==============================================================================
# 📂 CARGA DE DATOS MULTI-HOJA
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
        df_clean['__hoja_origen__'] = nombre_hoja.strip() 
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
    for nombre, df in dict_hojas.items():
        if "prestac" in normalizar(nombre):
            hoja_prestaciones = df
    return hoja_prestaciones if hoja_prestaciones is not None else list(dict_hojas.values())[0]

# ==============================================================================
# 🛠️ MATEMÁTICA Y EXTRACCIÓN DE DINERO (INTACTO Y BLINDADO 🔒)
# ==============================================================================
def es_columna_precio_fonasa(col_name):
    c = normalizar(str(col_name))
    return "copago fonasa 2026" in c or ("copago" in c and "fonasa" in c and "2026" in c)

def es_columna_precio_particular(col_name):
    c = normalizar(str(col_name))
    return "valor particular 2026" in c or ("valor" in c and "particular" in c and "2026" in c)

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

def formatear_pesos(monto):
    return f"${int(monto):,}".replace(",", ".")

def obtener_precio(fila, tipo_pago):
    fila_dict = fila.to_dict()
    if tipo_pago == "Particular":
        for col, val in fila_dict.items():
            if es_columna_precio_particular(col): return extraer_monto_limpio(val)
    else: 
        for col, val in fila_dict.items():
            if es_columna_precio_fonasa(col): return extraer_monto_limpio(val)
    return 0

# FUNCIONES CLASIFICADORAS GLOBALES
def es_col_precio(c):
    cn = normalizar(str(c))
    return es_columna_precio_fonasa(c) or es_columna_precio_particular(c) or "valor" in cn or "precio" in cn or "arancel" in cn

def es_col_tiempo(c): return "tiempo" in normalizar(str(c)) or "respuesta" in normalizar(str(c))
def es_col_contenedor(c): return "contenedor" in normalizar(str(c)) or "transporte" in normalizar(str(c)) or "tubo" in normalizar(str(c))
def es_col_muestra(c): return "tipo" in normalizar(str(c)) or "muestra" in normalizar(str(c))
def es_col_incluye(c): return "incluye" in normalizar(str(c))
def es_col_codigo(c): return "codigo" in normalizar(str(c)) or "bklab" in normalizar(str(c)) or "proactive" in normalizar(str(c))

def es_col_nombre(c):
    cn = normalizar(str(c)).strip()
    return "archipielago" in cn or "nombre" in cn or "prestacion" in cn or "examen" in cn or "unnamed" in cn

# DETECTOR AMPLIADO DE EXÁMENES QUE NO REQUIEREN PREPARACIÓN
def requiere_no_preparacion(nombre_test):
    norm = normalizar(nombre_test)
    palabras_test = set(re.findall(r'\b\w+\b', norm))
    
    # Siglas exactas
    siglas = ["tp", "tt", "ttpa", "ttpk", "pcr", "gen", "fr"]
    if any(s in palabras_test for s in siglas) or "f.r" in norm: return True
            
    # Frases o términos compuestos
    frases = [
        "factor reumatoide", "grupo sanguineo", "grupo y rh", "coombs",
        "subunidad beta", "beta hcg", "test rapido", "biologia molecular",
        "mutacion", "hemograma", "coagulacion", "fibrinogeno", "creatinina"
    ]
    if any(f in norm for f in frases): return True
    return False

# ==============================================================================
# 🎨 FUNCIÓN DE DIBUJO DE TARJETAS (NOMBRES ANCLADOS ARRIBA Y FILTROS)
# ==============================================================================
def renderizar_tarjeta(fila_dict, palabras, palabras_filtro):
    
    # --- PUENTE INTELIGENTE PARA MOSTRAR HORARIOS ---
    # Asegura que al buscar "horarios", la app atrape "Horario Lunes", "Horario Sábado", "Condiciones"
    palabras_f = palabras_filtro.copy()
    if "horario" in palabras_f or "horarios" in palabras_f:
        palabras_f.extend(["horario", "horarios", "condicion", "condiciones", "lunes", "sabado", "viernes"])

    # 1. Identificar Nombre
    # Solo miramos columnas que realmente tengan un valor en esta fila
    posibles_nombres = [c for c in fila_dict.keys() if es_col_nombre(c) and c not in ["__hoja_origen__", "__puntaje__"] and str(fila_dict[c]).strip() != "" and "sinonimo" not in normalizar(str(c))]
    col_nombre_final = None
    
    # Jerarquía: Primero Archipiélago, luego Nombre/Prestación, luego Examen genérico/Unnamed
    for c in posibles_nombres:
        if "archipielago" in normalizar(str(c)): col_nombre_final = c; break
    if not col_nombre_final:
        for c in posibles_nombres:
            if "nombre" in normalizar(str(c)) or "prestacion" in normalizar(str(c)): col_nombre_final = c; break
    if not col_nombre_final and posibles_nombres: 
        col_nombre_final = posibles_nombres[0]

    # 🚀 FALLBACK SUPREMO: Si el usuario dejó la celda del título en blanco en el Excel (Ej: Hoja Horarios)
    # Tomamos obligatoriamente la PRIMERA columna que tenga contenido como título principal
    if not col_nombre_final:
        for c in fila_dict.keys():
            if c not in ["__hoja_origen__", "__puntaje__"] and str(fila_dict[c]).strip() != "":
                col_nombre_final = c
                break

    cols_esenciales = [col_nombre_final] if col_nombre_final else []

    # 2. Lógica Láser (Búsquedas Específicas)
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
        cols_a_mostrar = list(fila_dict.keys())

    # 3. FILTRO BASURA, DUPLICADOS Y CATEGORÍAS
    cols_filtradas = []
    for c in cols_a_mostrar:
        if c in ["__hoja_origen__", "__puntaje__"]: continue
        cn = normalizar(str(c))
        val_norm = normalizar(str(fila_dict[c]))

        # Destruir columnas basura 
        if any(b in cn for b in ["sinonimo", "sinónimo", "palabra", "item", "tema/examen", "tema / examen"]): continue
        
        # Destruir nombres duplicados, conservar solo el oficial (col_nombre_final)
        if es_col_nombre(c) and col_nombre_final and c != col_nombre_final: continue

        # REGLA AZUL: Ocultar Categorías o Temas a menos que la búsqueda coincida con su contenido
        if any(m in cn for m in ["categoria", "tema", "protocolo"]):
            if not any(p in val_norm for p in palabras):
                continue

        cols_filtradas.append(c)

    cols_a_mostrar = cols_filtradas

    # 4. DIBUJAR HTML (REGLA: NOMBRE SIEMPRE EN LA LÍNEA 1 ARRIBA Y DESTACADO)
    contenido_tarjeta = ""
    
    if col_nombre_final:
        val_str_nombre = str(fila_dict.get(col_nombre_final, "")).strip()
        if val_str_nombre != "":
            cn_final = normalizar(str(col_nombre_final)).strip()
            
            # 🚀 MAGIA DEL FALLBACK: Si el nombre de la columna es raro (Unnamed) o un título sin sentido como 'tema'
            # NO escribimos esa etiqueta. Mostramos SU VALOR como el gran título principal de la tarjeta.
            es_titulo_limpio = (cn_final == "" or "unnamed" in cn_final or "tema" in cn_final or "examen" == cn_final or col_nombre_final not in posibles_nombres)
            
            if es_titulo_limpio:
                contenido_tarjeta += f'<div class="row-item" style="margin-bottom: 12px; border-bottom: 2px solid #d4af37; padding-bottom: 8px;"><span class="col-val" style="font-size: 1.15em; font-weight: 800; color: #1a1a1a; text-transform: uppercase;">{val_str_nombre}</span></div>'
            else:
                # Comportamiento normal (Ej: PRESTACIONES ARCHIPIELAGO: Nombre del examen)
                contenido_tarjeta += f'<div class="row-item" style="margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;"><span class="col-name" style="font-size: 1.05em; color: #6a1b29;">{col_nombre_final}:</span> <span class="col-val" style="font-size: 1.05em; font-weight: 800; color: #1a1a1a;">{val_str_nombre}</span></div>'
            
        if col_nombre_final in cols_a_mostrar:
            cols_a_mostrar.remove(col_nombre_final)

    # 💉 INYECTAR AUTOMÁTICAMENTE "NO REQUIERE PREPARACIÓN" SI CORRESPONDE
    if col_nombre_final:
        val_nombre = str(fila_dict.get(col_nombre_final, ""))
        if requiere_no_preparacion(val_nombre):
            has_explicit_prep = any("preparac" in normalizar(str(c)) or "indicac" in normalizar(str(c)) for c in cols_a_mostrar)
            if not has_explicit_prep:
                contenido_tarjeta += '<div class="row-item"><span class="col-name">Indicaciones:</span> <span class="col-val" style="color: #2e7d32; font-weight: 700;">No requiere preparación</span></div>'

    # Renderizar el resto de columnas (ej. Horarios y Condiciones)
    for col in cols_a_mostrar:
        val = fila_dict[col]
        if str(val).strip() != "":
            if es_col_precio(col) and extraer_monto_limpio(val) > 0:
                val_str = formatear_pesos(extraer_monto_limpio(val))
            else:
                val_str = str(val)
            contenido_tarjeta += f'<div class="row-item"><span class="col-name">{col}:</span> <span class="col-val">{val_str}</span></div>'

    if contenido_tarjeta.strip() != "":
        st.markdown(f'<div class="card-box">{contenido_tarjeta}</div>', unsafe_allow_html=True)


# ==============================================================================
# 🔍 INTERFAZ PRINCIPAL: BUSCADOR Y COTIZADOR
# ==============================================================================

consulta = st.text_input("Búsqueda", label_visibility="collapsed", placeholder="")

if consulta.strip() and dict_hojas_excel is not None:
    
    query_clean = consulta.strip()

    # ---------------------------------------------------------
    # 🔒 MODO 1: COTIZADOR AUTOMÁTICO (SUMA INTACTA 100%)
    # ---------------------------------------------------------
    if query_clean.lower().startswith("suma "):
        df_prestaciones = obtener_df_segun_modo(dict_hojas_excel, es_modo_bk=False)
        
        st.markdown('<div class="cotizador-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0; color:#d4af37;'>Cotizador de Exámenes</h3>", unsafe_allow_html=True)
        
        tipo_pago = st.radio("Selecciona la Previsión:", ["Particular", "Fonasa"], horizontal=True)
        
        texto_examenes = query_clean[5:] 
        nombres_examenes = [x.strip() for x in re.split(r',|\by\b', texto_examenes) if x.strip()]
        
        total = 0
        
        for nombre in nombres_examenes:
            palabras = [p for p in normalizar(nombre).split() if p]
            def coincide_examen_suma(fila):
                texto_fila = normalizar(" ".join([str(c) for c in fila.index] + [str(v) for v in fila.values]))
                return all(term in texto_fila for term in palabras)
            
            df_resultados = df_prestaciones[df_prestaciones.apply(coincide_examen_suma, axis=1)]
            
            if not df_resultados.empty:
                mejor_fila = None
                mejor_puntaje = 999999
                
                for _, fila in df_resultados.iterrows():
                    puntaje = 10000
                    for p in palabras:
                        if any(p == normalizar(str(v)).strip() for v in fila.values): puntaje -= 5000
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
                    if "archipielago" in normalizar(str(c)):
                        nombre_real = str(mejor_fila[c])
                        break
                if not nombre_real:
                    nombre_real = str(mejor_fila.values[0]) if len(str(mejor_fila.values[0])) > 5 else str(mejor_fila.values[1])

                st.success(f"✅ **{nombre.upper()}** ({nombre_real}) ➔ **{formatear_pesos(precio)}**")
            else:
                st.error(f"❌ **{nombre.upper()}** ➔ No encontrado.")
                
        st.divider()
        st.markdown(f"<h2 style='text-align: center; color: #ffffff;'>TOTAL {tipo_pago.upper()}: {formatear_pesos(total)}</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # ---------------------------------------------------------
    # 🌟 MODO 2: BÚSQUEDA GENERAL ORQUESTADA (CON INYECTOR)
    # ---------------------------------------------------------
    else:
        palabras = [p for p in normalizar(query_clean).split() if p]
        palabras_filtro = [p for p in palabras if p not in ["perfil", "hemograma", "examen", "prueba", "test", "de", "la", "el", "los", "las"]]
        
        df_todas_las_hojas = pd.concat(list(dict_hojas_excel.values()), ignore_index=True).fillna("")

        def coincide_examen_general(fila):
            hoja_origen = normalizar(str(fila.get("__hoja_origen__", "")))

            # ⏰ 1. AISLAMIENTO ESTRICTO DE HORARIOS (Filtra a Cortisol si no lo pides)
            if query_clean.lower() in ["horario", "horarios", "flujos", "horarios y flujos"]:
                if "horario" in hoja_origen or "flujo" in hoja_origen:
                    nombre_examen_oculto = ""
                    
                    # Usar el Fallback también aquí para poder identificar el nombre (Ej: Cortisol)
                    col_n_local = None
                    for c in fila.keys():
                        if es_col_nombre(c) and c not in ["__hoja_origen__", "__puntaje__"] and str(fila[c]).strip() != "": col_n_local = c; break
                    if not col_n_local:
                        for c in fila.keys():
                            if c not in ["__hoja_origen__", "__puntaje__"] and str(fila[c]).strip() != "": col_n_local = c; break
                            
                    if col_n_local: nombre_examen_oculto = str(fila[col_n_local]).lower()
                        
                    if "cortisol" in nombre_examen_oculto:
                        return False
                    return True
                return False

            # 2. BÚSQUEDA NORMAL
            elementos_validos = []
            tiene_plata = False
            tiene_codigo = False
            nombre_examen_oculto = ""
            
            for c, v in fila.items():
                if str(v).strip() != "" and c != "__hoja_origen__":
                    elementos_validos.append(str(c))
                    elementos_validos.append(str(v))
                    if es_col_precio(c): tiene_plata = True
                    if es_col_codigo(c): tiene_codigo = True
                    if es_col_nombre(c): nombre_examen_oculto += " " + str(v)
            
            valores_str = " ".join([normalizar(str(v)) for c, v in fila.items() if str(v).strip() != "" and c != "__hoja_origen__"])
            columnas_str = " ".join([normalizar(str(c)) for c, v in fila.items() if str(v).strip() != "" and c != "__hoja_origen__"])
            
            if tiene_plata: columnas_str += " precio precios valor valores arancel copago fonasa particular"
            if tiene_codigo: columnas_str += " codigo codigos"
                
            # 💉 INYECTOR DE BÚSQUEDA PARA "SIN PREPARACIÓN"
            valores_para_filtro = valores_str
            if requiere_no_preparacion(nombre_examen_oculto):
                inyeccion = " examen examenes sin preparacion no requiere preparacion indicaciones horario horarios"
                valores_str += inyeccion
                columnas_str += inyeccion
                valores_para_filtro += inyeccion

            texto_total = valores_str + " " + columnas_str
            
            # REGLA A: Todo lo que escribas debe existir en la fila
            if not all(term in texto_total for term in palabras):
                return False
                
            # REGLA B (ESCUDO ANTI-RUIDO): Al menos una palabra buscada debe coincidir con el VALOR real
            if not any(term in valores_para_filtro for term in palabras):
                return False
                
            return True

        df_resultados = df_todas_las_hojas[df_todas_las_hojas.apply(coincide_examen_general, axis=1)]

        if df_resultados.empty:
            st.warning(f"⚠️ No se encontró información para **'{query_clean}'**.")
        else:
            def calcular_puntaje_general(fila):
                puntaje = 10000
                valores_validos = [normalizar(str(v)).strip() for c, v in fila.items() if str(v).strip() != "" and c != "__hoja_origen__"]
                for p in palabras:
                    if any(p == v for v in valores_validos): puntaje -= 5000
                    else: puntaje -= 500
                return puntaje + len(" ".join(valores_validos))

            df_resultados['__puntaje__'] = df_resultados.apply(calcular_puntaje_general, axis=1)
            df_resultados = df_resultados.sort_values('__puntaje__')
            
            # Se aumentó a 150 para que, al buscar "horarios", despliegue la lista completa
            resultados_mostrar = df_resultados.head(150)

            # --- AGRUPAR EXÁMENES POR NOMBRE PARA DETECTAR COLISIONES ---
            examenes_agrupados = {}
            for _, fila in resultados_mostrar.iterrows():
                f_dict = fila.to_dict()
                
                col_n = None
                for c in f_dict.keys():
                    if es_col_nombre(c) and c not in ["__hoja_origen__", "__puntaje__"] and str(f_dict[c]).strip() != "": col_n = c; break
                
                # Identificación por Fallback para agrupar
                if not col_n:
                    for c in f_dict.keys():
                        if c not in ["__hoja_origen__", "__puntaje__"] and str(f_dict[c]).strip() != "": col_n = c; break
                
                n_val = str(f_dict[col_n]).strip() if col_n else str(list(f_dict.values())[0])
                n_norm = normalizar(n_val)
                
                if n_norm not in examenes_agrupados: 
                    examenes_agrupados[n_norm] = {'filas': [], 'puntaje': f_dict['__puntaje__']}
                examenes_agrupados[n_norm]['filas'].append(f_dict)
            
            grupos_ordenados = sorted(examenes_agrupados.values(), key=lambda x: x['puntaje'])
            
            # --- EVALUAR CADA EXAMEN (¿Se fusiona o se muestra individual?) ---
            for grupo in grupos_ordenados:
                lista_filas = grupo['filas']
                
                tiene_gine = any("ginecologico" in normalizar(str(f.get("__hoja_origen__", ""))) for f in lista_filas)
                tiene_prest = any("prestac" in normalizar(str(f.get("__hoja_origen__", ""))) for f in lista_filas)

                # 🧠 REGLA MAESTRA: SOLO FUSIONAR SI ESTÁ EN GINECOLÓGICO Y EN PRESTACIONES
                if tiene_gine and tiene_prest:
                    fila_gine = next((f for f in lista_filas if "ginecologico" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                    fila_prest = next((f for f in lista_filas if "prestac" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                    fila_barnafi = next((f for f in lista_filas if "barnafi" in normalizar(str(f.get("__hoja_origen__", ""))) or "bklab" in normalizar(str(f.get("__hoja_origen__", "")))), None)
                    filas_otras = [f for f in lista_filas if f != fila_gine and f != fila_prest and f != fila_barnafi]

                    fila_consolidada = {}

                    # 1. Absorber Prestaciones (Omitiendo lo que Gine va a reemplazar)
                    for c, v in fila_prest.items():
                        if c in ["__hoja_origen__", "__puntaje__"] or str(v).strip() == "": continue
                        if es_col_nombre(c) or es_col_precio(c) or es_col_tiempo(c) or es_col_contenedor(c) or es_col_muestra(c) or es_col_incluye(c): continue
                        fila_consolidada[c] = v

                    # 2. Imponer Reglas de Maestro Ginecológico
                    nombres_gine = [c for c in fila_gine.keys() if es_col_nombre(c) and c not in ["__hoja_origen__", "__puntaje__"] and str(fila_gine[c]).strip() != ""]
                    if nombres_gine:
                        nombres_viejos = [c for c in fila_consolidada.keys() if es_col_nombre(c)]
                        for nv in nombres_viejos: del fila_consolidada[nv]
                        fila_consolidada[nombres_gine[0]] = fila_gine[nombres_gine[0]] 
                    
                    for c, v in fila_gine.items():
                        if c in ["__hoja_origen__", "__puntaje__"] or str(v).strip() == "": continue
                        if es_col_precio(c) or es_col_tiempo(c) or es_col_contenedor(c) or es_col_muestra(c) or es_col_incluye(c):
                            fila_consolidada[c] = v
                            
                    # 3. De Barnafi SOLO extraemos el Código
                    if fila_barnafi:
                        for c, v in fila_barnafi.items():
                            if str(v).strip() != "" and es_col_codigo(c) and c not in ["__hoja_origen__", "__puntaje__"]:
                                fila_consolidada[c] = v

                    # 4. WhatsApp y Otras hojas (Evitando duplicar nombres)
                    for f in filas_otras:
                        for c, v in f.items():
                            if c in ["__hoja_origen__", "__puntaje__"] or str(v).strip() == "" or es_col_nombre(c): continue
                            fila_consolidada[c] = v

                    renderizar_tarjeta(fila_consolidada, palabras, palabras_filtro)

                else:
                    # 🧠 COMPORTAMIENTO INDIVIDUAL 
                    for f in lista_filas:
                        renderizar_tarjeta(f, palabras, palabras_filtro)
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
    cn = normalizar(str(c))
    return "archipielago" in cn or "nombre" in cn or "prestacion" in cn or cn == "examen"

# ==============================================================================
# 🔍 INTERFAZ PRINCIPAL: BUSCADOR Y COTIZADOR
# ==============================================================================

consulta = st.text_input("Búsqueda", label_visibility="collapsed", placeholder="")

if consulta.strip() and dict_hojas_excel is not None:
    
    query_clean = consulta.strip()

    # ---------------------------------------------------------
    # 🔒 MODO 1: COTIZADOR AUTOMÁTICO (SUMA INTACTA)
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
                        if any(p == normalizar(str(v)).strip() for v in fila.values):
                            puntaje -= 5000
                        else:
                            puntaje -= 500
                            
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
    # 🌟 MODO 2: BÚSQUEDA GENERAL (FUSIÓN JERÁRQUICA E INTELIGENTE)
    # ---------------------------------------------------------
    else:
        palabras = [p for p in normalizar(query_clean).split() if p]
        df_todas_las_hojas = pd.concat(list(dict_hojas_excel.values()), ignore_index=True).fillna("")

        def coincide_examen_general(fila):
            elementos_validos = []
            tiene_plata = False
            tiene_codigo = False
            
            for c, v in fila.items():
                if str(v).strip() != "" and c != "__hoja_origen__":
                    elementos_validos.append(str(c))
                    elementos_validos.append(str(v))
                    if es_col_precio(c): tiene_plata = True
                    if es_col_codigo(c): tiene_codigo = True
            
            texto_fila = normalizar(" ".join(elementos_validos))
            
            # Traductor interno de conceptos
            if tiene_plata: texto_fila += " precio precios valor valores arancel copago fonasa particular"
            if tiene_codigo: texto_fila += " codigo codigos"
                
            return all(term in texto_fila for term in palabras)

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
            resultados_mostrar = df_resultados.head(50)

            # --- 🚀 FASE 1: AGRUPAR RESULTADOS POR EXAMEN ---
            examenes_agrupados = {}
            for _, fila in resultados_mostrar.iterrows():
                f_dict = fila.to_dict()
                
                col_n = None
                for c in f_dict.keys():
                    if es_col_nombre(c): col_n = c; break
                
                n_val = str(f_dict[col_n]).strip() if col_n else str(list(f_dict.values())[0])
                n_norm = normalizar(n_val)
                
                if n_norm not in examenes_agrupados: 
                    examenes_agrupados[n_norm] = {'filas': [], 'puntaje': f_dict['__puntaje__']}
                examenes_agrupados[n_norm]['filas'].append(f_dict)
            
            # Ordenar los grupos para mostrar el más relevante arriba
            grupos_ordenados = sorted(examenes_agrupados.values(), key=lambda x: x['puntaje'])
            
            # --- 🚀 FASE 2: FUSIÓN DE DATOS Y RENDERIZADO ---
            for grupo in grupos_ordenados:
                lista_filas = grupo['filas']
                
                fila_gine = None
                fila_prest = None
                fila_barnafi = None
                filas_otras = []
                
                for f in lista_filas:
                    hoja = normalizar(str(f.get("__hoja_origen__", "")))
                    if "ginecologico" in hoja: fila_gine = f
                    elif "prestac" in hoja: fila_prest = f
                    elif "barnafi" in hoja or "bklab" in hoja: fila_barnafi = f
                    else: filas_otras.append(f)
                
                fila_consolidada = {}
                
                # --- REGLA ESTRICTA: SI ESTÁ EN GINE Y PRESTACIONES ---
                if fila_gine and fila_prest:
                    # 1. Extraer único nombre del Maestro Ginecológico
                    nombres_gine = [c for c in fila_gine.keys() if es_col_nombre(c) and c != "__hoja_origen__"]
                    if nombres_gine: fila_consolidada[nombres_gine[0]] = fila_gine[nombres_gine[0]]
                    
                    # 2. Extraer resto de información de Prestaciones (Ocultando lo que Gine debe reemplazar)
                    for c, v in fila_prest.items():
                        if c == "__hoja_origen__" or str(v).strip() == "": continue
                        if es_col_nombre(c) or es_col_precio(c) or es_col_tiempo(c) or es_col_contenedor(c) or es_col_muestra(c) or es_col_incluye(c):
                            continue
                        fila_consolidada[c] = v
                        
                    # 3. Extraer la información superior del Maestro Ginecológico
                    for c, v in fila_gine.items():
                        if c == "__hoja_origen__" or str(v).strip() == "": continue
                        if es_col_precio(c) or es_col_tiempo(c) or es_col_contenedor(c) or es_col_muestra(c) or es_col_incluye(c):
                            fila_consolidada[c] = v
                            
                    # 4. De Barnafi SOLO extraemos el Código BKLAB
                    if fila_barnafi:
                        for c, v in fila_barnafi.items():
                            if str(v).strip() != "" and es_col_codigo(c) and c != "__hoja_origen__":
                                fila_consolidada[c] = v
                else:
                    # -- COMPORTAMIENTO NORMAL (Si no hay conflicto Gine vs Prest) --
                    base = fila_prest or fila_gine
                    if base:
                        for c, v in base.items():
                            if c != "__hoja_origen__" and str(v).strip() != "": fila_consolidada[c] = v
                    
                    if fila_barnafi:
                        for c, v in fila_barnafi.items():
                            if c == "__hoja_origen__" or str(v).strip() == "": continue
                            if base: # Si ya hay base, Barnafi da solo código
                                if es_col_codigo(c): fila_consolidada[c] = v
                            else: # Si Barnafi es la única hoja que tiene el examen (Ej. TSH BK)
                                fila_consolidada[c] = v
                                
                # Agregar información de WhatsApp y Horarios
                for f in filas_otras:
                    for c, v in f.items():
                        if c == "__hoja_origen__" or str(v).strip() == "": continue
                        cn = normalizar(str(c))
                        # FILTRO BASURA EXPRESO
                        if any(b in cn for b in ["item", "palabras", "sinonimo"]): continue
                        # PREVENIR DUPLICACIÓN DE NOMBRES DE OTRAS HOJAS
                        if es_col_nombre(c): continue 
                        fila_consolidada[c] = v

                # --- 🚀 FASE 3: APLICAR FILTRO LÁSER DE BÚSQUEDA ---
                col_nombre_final_cons = None
                for c in fila_consolidada.keys():
                    if es_col_nombre(c): col_nombre_final_cons = c; break
                
                cols_esenciales = [col_nombre_final_cons] if col_nombre_final_cons else []

                has_fonasa = "fonasa" in palabras
                has_particular = "particular" in palabras
                has_precio = any(w in palabras for w in ["precio", "precios", "valor", "valores", "arancel", "copago"])
                
                cols_especificas = []
                palabras_filtro = [p for p in palabras if p not in ["perfil", "hemograma", "examen", "prueba", "test", "de", "la", "el", "los", "las"]]
                
                if has_fonasa and not has_particular:
                    for c in fila_consolidada.keys():
                        if es_col_precio(c): cols_especificas.append(c)
                        elif any(p in normalizar(str(c)) for p in palabras_filtro if p not in ["fonasa", "copago", "2026"]): cols_especificas.append(c)
                            
                elif has_particular and not has_fonasa:
                    for c in fila_consolidada.keys():
                        if es_col_precio(c): cols_especificas.append(c)
                        elif any(p in normalizar(str(c)) for p in palabras_filtro if p not in ["particular", "valor", "2026"]): cols_especificas.append(c)
                            
                elif has_precio:
                    for c in fila_consolidada.keys():
                        if es_col_precio(c): cols_especificas.append(c)
                        elif any(p in normalizar(str(c)) for p in palabras_filtro if p not in ["fonasa", "particular", "precio", "valor", "arancel", "copago"]): cols_especificas.append(c)
                else:
                    for c in fila_consolidada.keys():
                        if any(term in normalizar(str(c)) for term in palabras_filtro):
                            cols_especificas.append(c)

                if cols_especificas or has_fonasa or has_particular or has_precio:
                    cols_a_mostrar = list(dict.fromkeys(cols_esenciales + cols_especificas))
                else:
                    cols_a_mostrar = list(fila_consolidada.keys())

                # Eliminar nombres repetidos o columnas ocultas que se hayan filtrado
                columnas_basura = ["sinonimo", "sinónimo", "palabra", "item"]
                cols_filtradas = []
                for c in cols_a_mostrar:
                    cn = normalizar(str(c))
                    if any(b in cn for b in columnas_basura): continue
                    if es_col_nombre(c) and c != col_nombre_final_cons: continue
                    cols_filtradas.append(c)
                
                cols_a_mostrar = cols_filtradas

                # 👑 ANCLAR EL NOMBRE EN EL PUESTO #1
                if col_nombre_final_cons and col_nombre_final_cons in cols_a_mostrar:
                    cols_a_mostrar.remove(col_nombre_final_cons)
                    cols_a_mostrar.insert(0, col_nombre_final_cons)

                # 💳 RENDERIZADO VISUAL
                contenido_tarjeta = ""
                for col in cols_a_mostrar:
                    val = fila_consolidada[col]
                    
                    if str(val).strip() != "" and col != "__puntaje__":
                        # Formatear el dinero con su punto de miles chileno
                        if es_col_precio(col) and extraer_monto_limpio(val) > 0:
                            val_str = formatear_pesos(extraer_monto_limpio(val))
                        else:
                            val_str = str(val)
                            
                        contenido_tarjeta += f'<div class="row-item"><span class="col-name">{col}:</span> <span class="col-val">{val_str}</span></div>'
                
                # SEGURO ANTI-BARRAS VACÍAS
                if contenido_tarjeta.strip() != "":
                    st.markdown(f'<div class="card-box">{contenido_tarjeta}</div>', unsafe_allow_html=True)
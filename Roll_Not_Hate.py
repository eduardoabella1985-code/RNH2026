import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="RNH 2026 - Oficial", layout="centered")

# URL de tu Google Sheet (Asegúrate que sea el link de compartir)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1YJn17Yz1mNit90vmG45mrPgE49E8rKKzSQj8wWx8LuU/edit?usp=sharing"

st.title("🏆 Roll Not Hate 2026")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- PANEL LATERAL ---
st.sidebar.header("CONTROL JUEZ")
juez = st.sidebar.selectbox("Juez", ["Erika", "Xiomara", "George", "Mike"])
pasada = st.sidebar.selectbox("Pasada", [f"Pasada {i+1}" for i in range(6)])

# Cargar lista de inscritos (Hoja 1)
if 'df_full' not in st.session_state:
    try:
        st.session_state.df_full = conn.read(spreadsheet=URL_SHEET, worksheet="Hoja 1")
    except:
        st.sidebar.error("Conectando con la lista...")

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["📝 CALIFICAR", "📊 RANKING"])

with tab1:
    if 'df_full' in st.session_state:
        df = st.session_state.df_full
        cat_sel = st.selectbox("Categoría", df['Categoria'].unique())
        
        patinadores = df[df['Categoria'] == cat_sel]['Nombre'].tolist()
        np.random.seed(42) 
        np.random.shuffle(patinadores)
        
        grupos = [patinadores[i:i + 5] for i in range(0, len(patinadores), 5)]
        num_grupo = st.number_input(f"Grupo (1 de {len(grupos)})", 1, len(grupos))
        grupo_actual = grupos[int(num_grupo)-1]

        st.header(f"Grupo {num_grupo} - {pasada}")

        notas_pasada = {}
        for p in grupo_actual:
            st.subheader(f"👤 {p}")
            # Cajas en blanco para no tener que borrar el 0.0
            n = st.text_input(f"Puntaje {p}", value="", key=f"n_{p}_{juez}_{pasada}_{num_grupo}")
            notas_pasada[p] = n

        if st.button("🚀 ENVIAR NOTAS A LA NUBE"):
            try:
                # Organizamos los datos para la pestaña "Puntaje"
                nuevos_datos = pd.DataFrame([{
                    "Juez": juez, 
                    "Pasada": pasada, 
                    "Grupo": num_grupo,
                    "Categoria": cat_sel, 
                    "Patinador": p, 
                    "Puntaje": float(val.replace(',','.'))
                } for p, val in notas_pasada.items() if val.strip() != ""])
                
                if not nuevos_datos.empty:
                    # Leemos lo que ya hay en 'Puntaje' para no borrarlo
                    df_existente = conn.read(spreadsheet=URL_SHEET, worksheet="Puntaje")
                    df_final = pd.concat([df_existente, nuevos_datos], ignore_index=True)
                    
                    # Guardamos todo de nuevo en la nube
                    conn.update(spreadsheet=URL_SHEET, worksheet="Puntaje", data=df_final)
                    
                    st.balloons()
                    st.success("✅ ¡Estadísticas guardadas con éxito!")
                else:
                    st.warning("⚠️ Escribe al menos un puntaje.")
            except Exception as e:
                st.error("❌ Error: Verifica la conexión o los Secrets.")

with tab2:
    st.header("Ranking Acumulado")
    try:
        res = conn.read(spreadsheet=URL_SHEET, worksheet="Puntaje")
        if not res.empty:
            ranking = res.groupby(["Categoria", "Patinador"])["Puntaje"].sum().reset_index()
            st.table(ranking.sort_values(by="Puntaje", ascending=False))
        else:
            st.info("Aún no hay puntajes registrados.")
    except:
        st.write("Cargando resultados...")

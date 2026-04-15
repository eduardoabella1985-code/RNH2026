import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection

# 1. Configuración
st.set_page_config(page_title="RNH 2026 - Oficial", layout="centered")
URL_SHEET = "https://docs.google.com/spreadsheets/d/1YJn17Yz1mNit90vmG45mrPgE49E8rKKzSQj8wWx8LuU/edit?usp=sharing"

st.title("🏆 Roll Not Hate 2026")

# 2. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Panel Lateral
st.sidebar.header("CONTROL JUEZ")
juez = st.sidebar.selectbox("Juez", ["Erika", "Xiomara", "George", "Mike"])
pasada = st.sidebar.selectbox("Pasada", [f"Pasada {i+1}" for i in range(6)])

# 4. Carga de datos (Corregido bloque de espacios)
if 'df_full' not in st.session_state:
    try:
        st.session_state.df_full = conn.read(worksheet="Inscritos", ttl=0)
    except Exception as e:
        st.sidebar.error(f"Error de conexión: {e}")
        st.stop()

# 5. Pestañas de la App
tab1, tab2 = st.tabs(["📝 CALIFICAR", "📊 RANKING"])

with tab1:
    if 'df_full' in st.session_state:
        df = st.session_state.df_full
        cat_sel = st.selectbox("Categoría", df['Categoria'].unique())
        
        patinadores = df[df['Categoria'] == cat_sel]['Nombre'].tolist()
        np.random.shuffle(patinadores)
        
        grupos = [patinadores[i:i + 5] for i in range(0, len(patinadores), 5)]
        num_grupo = st.number_input(f"Grupo (1 de {len(grupos)})", 1, len(grupos))
        grupo_actual = grupos[int(num_grupo)-1]

        st.header(f"Grupo {num_grupo} - {pasada}")

        notas_pasada = {}
        for p in grupo_actual:
            st.subheader(f"👤 {p}")
            n = st.text_input(f"Puntaje {p}", value="", key=f"n_{p}_{juez}_{pasada}_{num_grupo}")
            notas_pasada[p] = n

        if st.button("🚀 ENVIAR NOTAS A LA NUBE"):
            try:
                nuevos_datos = pd.DataFrame([{
                    "Juez": juez, 
                    "Pasada": pasada, 
                    "Grupo": num_grupo,
                    "Categoria": cat_sel, 
                    "Patinador": p, 
                    "Puntaje": float(val.replace(',','.'))
                } for p, val in notas_pasada.items() if val.strip() != ""])
                
                if not nuevos_datos.empty:
                    df_existente = conn.read(worksheet="Puntajes", ttl=0)
                    df_final = pd.concat([df_existente, nuevos_datos], ignore_index=True)
                    conn.update(worksheet="Puntajes", data=df_final)
                    st.balloons()
                    st.success("✅ ¡Puntajes guardados!")
                else:
                    st.warning("⚠️ Escribe al menos un puntaje.")
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")

with tab2:
    st.header("Ranking Acumulado")
    try:
        res = conn.read(worksheet="Puntajes", ttl=0)
        if not res.empty:
            ranking = res.groupby(["Categoria", "Patinador"])["Puntaje"].sum().reset_index()
            st.table(ranking.sort_values(by="Puntaje", ascending=False))
        else:
            st.info("Aún no hay puntajes registrados.")
    except:
        st.write("Cargando resultados...")

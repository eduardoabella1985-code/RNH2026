
import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="RNH 2026 - Control Total", layout="centered")

LINK_CSV = "https://docs.google.com/spreadsheets/d/1YJn17Yz1mNit90vmG45mrPgE49E8rKKzSQj8wWx8LuU/export?format=csv"
FILE_RESULTADOS = "resultados_rnh.csv"

st.title("🏆 Roll Not Hate 2026")

# --- PANEL LATERAL ---
st.sidebar.header("CONTROL JUEZ")
juez = st.sidebar.selectbox("Juez", ["Erika", "Xiomara", "George", "Mike"])
pasada = st.sidebar.selectbox("Pasada Actual", [f"Pasada {i+1}" for i in range(6)])

if st.sidebar.button("🔄 ACTUALIZAR LISTA INSCRITOS"):
    try:
        st.session_state.df_full = pd.read_csv(LINK_CSV)
        st.sidebar.success("Lista cargada.")
    except:
        st.sidebar.error("Error al conectar con la lista.")

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["📝 PANEL DE CALIFICACIÓN", "📊 RANKING EN VIVO"])

with tab1:
    if 'df_full' in st.session_state:
        df = st.session_state.df_full
        cat_sel = st.selectbox("Categoría", df['Categoria'].unique())
        
        # Generar grupos de 5 (Sincronizado)
        patinadores = df[df['Categoria'] == cat_sel]['Nombre'].tolist()
        np.random.seed(42) # Semilla fija para que el grupo 1 sea siempre el mismo
        np.random.shuffle(patinadores)
        
        grupos = [patinadores[i:i + 5] for i in range(0, len(patinadores), 5)]
        num_grupo = st.number_input(f"Grupo (1 de {len(grupos)})", 1, len(grupos))
        grupo_actual = grupos[int(num_grupo)-1]

        st.header(f"Grupo {num_grupo} - {pasada}")
        st.warning("Escribe el puntaje y presiona 'Enviar' al terminar la pasada.")

        # CAPTURA DE NOTAS (Cajas en blanco)
        notas_pasada = {}
        for p in grupo_actual:
            st.subheader(f"👤 {p}")
            # value="" hace que la caja esté vacía
            n = st.text_input(f"Puntaje {p}", value="", key=f"n_{p}_{juez}_{pasada}_{num_grupo}")
            notas_pasada[p] = n

        if st.button("🚀 ENVIAR PUNTAJES DE ESTA PASADA"):
            try:
                datos = []
                for patinador, puntaje in notas_pasada.items():
                    if puntaje.strip() == "": continue # Salta si está vacío
                    datos.append({
                        "Juez": juez,
                        "Pasada": pasada,
                        "Grupo": num_grupo,
                        "Categoria": cat_sel,
                        "Patinador": patinador,
                        "Puntaje": float(puntaje.replace(',', '.'))
                    })
                
                if datos:
                    df_new = pd.DataFrame(datos)
                    if os.path.exists(FILE_RESULTADOS):
                        df_new.to_csv(FILE_RESULTADOS, mode='a', header=False, index=False)
                    else:
                        df_new.to_csv(FILE_RESULTADOS, index=False)
                    st.balloons()
                    st.success(f"¡{pasada} del Grupo {num_grupo} guardada!")
            except ValueError:
                st.error("Por favor ingresa solo números (ejemplo: 8.5)")

with tab2:
    st.header("Ranking Acumulado")
    if os.path.exists(FILE_RESULTADOS):
        res = pd.read_csv(FILE_RESULTADOS)
        
        # Cálculo de totales: Suma de todas las pasadas y promedios de jueces
        st.subheader("Puntajes Totales (Suma de Pasadas)")
        ranking = res.groupby(["Categoria", "Patinador"])["Puntaje"].sum().reset_index()
        ranking = ranking.sort_values(by="Puntaje", ascending=False)
        st.table(ranking)
        
        with st.expander("Ver detalle por Juez"):
            st.dataframe(res)
            
        if st.button("🗑️ REINICIAR TORNEO (Borrar todo)"):
            os.remove(FILE_RESULTADOS)
            st.rerun()
    else:
        st.info("Esperando los primeros puntajes...")
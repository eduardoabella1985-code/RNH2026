import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="RNH 2026", layout="centered")
st.title("🏆 Roll Not Hate 2026")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Carga la pestaña correcta sin caracteres especiales
    df = conn.read(worksheet="Inscritos", ttl=0)
    st.success("Conexión exitosa")
    st.dataframe(df)
except Exception as e:
    st.error(f"Error: {e}")

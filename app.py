import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

# 👉 LINK DO TEU FORM (já convertido para envio)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfw_A3FyZ7bQzdB_j5vINdtODa3dcBZ0d61B6b03ZMjZOekag/formResponse"

# --- FUNÇÃO DE ENVIO ---
def enviar_para_form(registo):
    requests.post(
        "https://docs.google.com/forms/d/e/1FAIpQLSfw_A3FyZ7bQzdB_j5vINdtODa3dcBZ0d61B6b03ZMjZOekag/formResponse",
        data=registo
    )

# --- ESTADOS ---
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False

if "inicio_unix" not in st.session_state:
    st.session_state.inicio_unix = None

if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False

# --- INTERFACE ---
st.markdown("""
<div style="text-align:center; font-size:34px; font-weight:700;">
🏗️ InstalTime Pro
</div>
<div style="text-align:center;">
by <span style="color:red; font-size:20px; font-weight:700;">E</span>nergipax
</div>
<hr>
""", unsafe_allow_html=True)

obra = st.text_input("Obra")
material = st.text_input("Material")
valor_hora = st.sidebar.number_input("Valor/hora (€)", value=20.0)

# --- CRONÓMETRO ---
c1, c2 = st.columns(2)

with c1:
    if not st.session_state.cronometro_ativo and not st.session_state.modo_guardar:
        if st.button("▶️ INICIAR", use_container_width=True):
            st.session_state.inicio_unix = time.time()
            st.session_state.cronometro_ativo = True
            st.rerun()

with c2:
    if st.session_state.cronometro_ativo:
        if st.button("⏹️ PARAR", use_container_width=True):
            st.session_state.minutos_finais = (time.time() - st.session_state.inicio_unix) / 60
            st.session_state.cronometro_ativo = False
            st.session_state.modo_guardar = True
            st.rerun()

# --- TEMPO ---
if st.session_state.cronometro_ativo:
    tempo = time.time() - st.session_state.inicio_unix
    mins, segs = divmod(int(tempo), 60)
    st.metric("⏳ Tempo", f"{mins:02d}:{segs:02d}")

# --- GUARDAR ---
if st.session_state.modo_guardar:
    qtd = st.number_input("Quantidade", min_value=0.1, value=1.0)

    if st.button("✅ GUARDAR", use_container_width=True):
        minutos = round(st.session_state.minutos_finais, 2)
        custo = round(minutos * (valor_hora / 60), 2)

        registo = {
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Obra": obra,
            "Material": material,
            "Qtd": qtd,
            "Minutos": minutos,
            "Custo": custo
        }

        try:
            enviar_para_form(registo)
            st.success("✅ Gravado na folha!")

            st.session_state.modo_guardar = False
            st.rerun()

        except Exception as e:
            st.error(f"Erro: {e}")

import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

FILE = "dados_instaltime.csv"

# --- CARREGAR DADOS (PROTEGIDO) ---
if "historico" not in st.session_state:
    if os.path.exists(FILE):
        try:
            df_load = pd.read_csv(FILE)
            st.session_state.historico = df_load.to_dict("records")
        except:
            st.session_state.historico = []
    else:
        st.session_state.historico = []

# --- ESTADOS ---
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False

if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False
if "materiais_guardados" not in st.session_state:
    st.session_state.materiais_guardados = []

st.title("🏗️ InstalTime Pro")

# --- SIDEBAR ---
with st.sidebar:
    valor_hora = st.number_input("Valor/hora (€)", value=20.0)

# --- INPUTS ---
obra = st.text_input("Nome da Obra")

# --- MATERIAL PERSONALIZADO ---
material = st.text_input("Material (escreve o que quiseres)")

unidade = st.selectbox(
    "Unidade",
    ["Metros", "Unidades", "Horas", "Outro"]
)

# --- BOTÕES ---
col1, col2 = st.columns(2)

with col1:
    if not st.session_state.cronometro_ativo:
        if st.button("▶️ INICIAR", use_container_width=True):
            st.session_state.inicio = datetime.now()
            st.session_state.cronometro_ativo = True
            st.rerun()

with col2:
    if st.session_state.cronometro_ativo:
        if st.button("💾 PARAR", use_container_width=True):
            st.session_state.fim = datetime.now()
            st.session_state.cronometro_ativo = False
            st.session_state.modo_guardar = True
            st.rerun()

# --- GUARDAR ---
if st.session_state.modo_guardar:
    st.warning(f"Inserir quantidade ({unidade})")

    qtd = st.number_input("Quantidade", min_value=1.0, value=1.0)

    if st.button("✅ CONFIRMAR", use_container_width=True):
        duracao = st.session_state.fim - st.session_state.inicio
        minutos = duracao.total_seconds() / 60
        custo = minutos * (valor_hora / 60)
        performance = minutos / qtd

        registo = {
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Obra": obra,
            "Material": material,
            "Qtd": qtd,
            "Minutos": round(minutos, 2),
            "Min/Un": round(performance, 2),
            "Custo (€)": round(custo, 2)
        }

        st.session_state.historico.append(registo)

        pd.DataFrame(st.session_state.historico).to_csv(FILE, index=False)

        st.session_state.modo_guardar = False
        del st.session_state.fim

        st.success("Registo guardado!")
        st.rerun()

# --- TEMPO EM TEMPO REAL ---
if st.session_state.cronometro_ativo:
    tempo = datetime.now() - st.session_state.inicio
    st.info(f"⏳ Tempo: {str(tempo).split('.')[0]}")

# --- HISTÓRICO ---
if st.session_state.historico:
    st.divider()
    st.subheader("📋 Registos")

    for i in range(len(st.session_state.historico)):
        row = st.session_state.historico[i]

        col1, col2 = st.columns([4,1])

        with col1:
            st.write(f"{row['Data']} | {row['Obra']} | {row['Material']} | {row['Qtd']} | {row['Minutos']} min | {row['Custo (€)']}€")

        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.historico.pop(i)
                pd.DataFrame(st.session_state.historico).to_csv(FILE, index=False)
                st.rerun()

    # --- MÉTRICAS ---
    df = pd.DataFrame(st.session_state.historico)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total €", round(df["Custo (€)"].sum(), 2))
    c2.metric("⏱️ Total Min", round(df["Minutos"].sum(), 1))
    c3.metric("⚡ Média Min/Un", round(df["Min/Un"].mean(), 2))

    # --- EXPORTAR ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exportar", csv, "instaltime.csv", use_container_width=True)

    # --- LIMPAR TUDO ---
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.historico = []
        if os.path.exists(FILE):
            os.remove(FILE)
        st.rerun()

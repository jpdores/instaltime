import streamlit as st
import pandas as p
from datetime import datetime
import os

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

FILE = "dados_instaltime.csv"

if "historico" not in st.session_state:
    if os.path.exists(FILE):
    try:
        df_load = pd.read_csv(FILE)
        st.session_state.historico = df_load.to_dict("records")
    except:
        st.session_state.historico = []
else:
    st.session_state.historico = []
else:
    st.session_state.historico = []
        
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False

st.title("🏗️ InstalTime Pro")

with st.sidebar:
    valor_hora = st.number_input("Valor/hora (€)", value=20.0)

obra = st.text_input("Nome da Obra")

materiais = {
    "Tubagem 20mm": "Metros",
    "Tubagem 25mm": "Metros",
    "Passagem de Fios": "Metros",
    "Tomadas / Interruptores": "Unidades",
    "Tomadas ITED": "Unidades"
}

material = st.selectbox("Material", list(materiais.keys()))
unidade = materiais[material]

col1, col2 = st.columns(2)

with col1:
    if not st.session_state.cronometro_ativo:
        if st.button("▶️ INICIAR"):
            st.session_state.inicio = datetime.now()
            st.session_state.cronometro_ativo = True
            st.rerun()
    else:
        if st.button("⏹️ PARAR"):
            st.session_state.fim = datetime.now()
            st.session_state.cronometro_ativo = False
            st.rerun()

if "fim" in st.session_state and not st.session_state.cronometro_ativo:
    qtd = st.number_input("Quantidade", min_value=1.0, value=1.0)

    if st.button("GUARDAR"):
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

        df_save = pd.DataFrame(st.session_state.historico)
        df_save.to_csv(FILE, index=False)

        del st.session_state.fim
        st.success("Guardado!")
        st.rerun()

if st.session_state.cronometro_ativo:
    tempo = datetime.now() - st.session_state.inicio
    st.info(f"Tempo: {str(tempo).split('.')[0]}")

if st.session_state.historico:
    df = pd.DataFrame(st.session_state.historico)

    st.metric("Total €", round(df["Custo (€)"].sum(), 2))
    st.metric("Total Min", round(df["Minutos"].sum(), 1))

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Exportar", csv, "instaltime.csv")

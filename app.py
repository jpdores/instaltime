import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

FILE = "dados_instaltime.csv"
TIMER_FILE = "timer_estado.csv"

# --- ESTILO ---
st.markdown("""
<style>
button {
    height: 70px !important;
    font-size: 20px !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown("""
<h1 style='text-align: center; margin-bottom:0;'>🏗️ InstalTime Pro</h1>
<p style='text-align: center; font-size:14px; margin-top:0;'>
<span style='color:red; font-weight:bold;'>E</span><span>nergipax</span>
</p>
""", unsafe_allow_html=True)

# --- FUNÇÕES TIMER ---
def guardar_timer(inicio, tempo):
    pd.DataFrame([{"inicio": inicio, "tempo": tempo}]).to_csv(TIMER_FILE, index=False)

def carregar_timer():
    if os.path.exists(TIMER_FILE):
        try:
            df = pd.read_csv(TIMER_FILE)
            return df.iloc[0]["inicio"], df.iloc[0]["tempo"]
        except:
            return None, 0
    return None, 0

# --- CARREGAR DADOS ---
if "historico" not in st.session_state:
    if os.path.exists(FILE):
        try:
            st.session_state.historico = pd.read_csv(FILE).to_dict("records")
        except:
            st.session_state.historico = []
    else:
        st.session_state.historico = []

# --- ESTADOS ---
if "inicio" not in st.session_state:
    inicio, tempo = carregar_timer()
    st.session_state.inicio = inicio
    st.session_state.tempo = tempo if tempo else 0

if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False

if "materiais_guardados" not in st.session_state:
    st.session_state.materiais_guardados = []

# --- SIDEBAR ---
with st.sidebar:
    valor_hora = st.number_input("Valor/hora (€)", value=20.0)

# --- OBRA ---
obra = st.text_input("Obra")

# --- MATERIAL ---
material_existente = st.selectbox(
    "Material existente",
    [""] + st.session_state.materiais_guardados
)

material_novo = st.text_input("Novo material")

material = material_novo if material_novo else material_existente

unidade = st.selectbox("Unidade", ["Metros", "Unidades", "Horas", "Outro"])

# --- BOTÕES ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ INICIAR"):
        st.session_state.inicio = datetime.now().timestamp()
        guardar_timer(st.session_state.inicio, st.session_state.tempo)

with col2:
    if st.button("⏸️ PAUSAR") and st.session_state.inicio:
        pausa = datetime.now().timestamp() - st.session_state.inicio
        st.session_state.tempo += pausa
        st.session_state.inicio = None
        guardar_timer(None, st.session_state.tempo)

with col3:
    if st.button("💾 FINALIZAR"):
        st.session_state.modo_guardar = True

# --- TEMPO ---
tempo_total = st.session_state.tempo
if st.session_state.inicio:
    tempo_total += datetime.now().timestamp() - st.session_state.inicio

st.info(f"⏳ Tempo: {int(tempo_total//60)} min")

# --- GUARDAR ---
if st.session_state.modo_guardar:
    qtd = st.number_input("Quantidade", min_value=1.0, value=1.0)

    if st.button("✅ CONFIRMAR"):
        minutos = tempo_total / 60
        custo = minutos * (valor_hora / 60)

        registo = {
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Obra": obra,
            "Material": material,
            "Qtd": qtd,
            "Minutos": round(minutos, 2),
            "Custo (€)": round(custo, 2)
        }

        st.session_state.historico.append(registo)
        pd.DataFrame(st.session_state.historico).to_csv(FILE, index=False)

        if material and material not in st.session_state.materiais_guardados:
            st.session_state.materiais_guardados.append(material)

        # reset timer
        st.session_state.inicio = None
        st.session_state.tempo = 0
        st.session_state.modo_guardar = False

        if os.path.exists(TIMER_FILE):
            os.remove(TIMER_FILE)

        st.success("Guardado!")
        st.rerun()

# --- FILTRO ---
if st.session_state.historico:
    df = pd.DataFrame(st.session_state.historico)

    filtro = st.selectbox("Filtrar obra", ["Todas"] + list(df["Obra"].unique()))

    if filtro != "Todas":
        df = df[df["Obra"] == filtro]

    st.subheader("Registos")

    for i in df.index:
        row = st.session_state.historico[i]

        col1, col2 = st.columns([4,1])

        with col1:
            st.write(f"{row['Data']} | {row['Obra']} | {row['Material']} | {row['Qtd']} | {row['Minutos']} min | {row['Custo (€)']}€")

        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.historico.pop(i)
                pd.DataFrame(st.session_state.historico).to_csv(FILE, index=False)
                st.rerun()

    # métricas
    st.metric("Total €", round(df["Custo (€)"].sum(), 2))

    # exportar
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Exportar", csv, "dados.csv")

    if st.button("🗑️ Limpar Tudo"):
        st.session_state.historico = []
        if os.path.exists(FILE):
            os.remove(FILE)
        st.rerun()

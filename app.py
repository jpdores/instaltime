import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

# --- LIGAÇÃO ---
URL_FOLHA = "https://docs.google.com/spreadsheets/d/1-JaEy3L1Rhch29AkV-wYFLsqb2o_NX38I2iABNsSN4Q/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- INTERFACE ---
st.markdown("""
<style>
.titulo { text-align: center; font-size: 34px; font-weight: 700; margin-bottom: 0; }
.subtitulo { text-align: center; font-size: 16px; margin-top: 0; }
.stButton>button { border-radius: 10px; height:60px; font-size:18px; }
</style>

<div class="titulo">🏗️ InstalTime Pro</div>
<div class="subtitulo">by <span style="color:red; font-size:20px; font-weight:700;">E</span>nergipax</div>
<hr>
""", unsafe_allow_html=True)

# --- ESTADOS ---
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False

if "inicio_unix" not in st.session_state:
    st.session_state.inicio_unix = None

if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False

# --- INPUTS ---
obra = st.text_input("Obra", "Geral")
material = st.text_input("Material", "Instalação")
valor_hora = st.sidebar.number_input("Valor/hora (€)", value=20.0)

# --- CRONÓMETRO ---
c1, c2 = st.columns(2)

with c1:
    if not st.session_state.cronometro_ativo and not st.session_state.modo_guardar:
        if st.button("▶️ INICIAR", use_container_width=True, type="primary"):
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

# --- MOSTRAR TEMPO ---
if st.session_state.cronometro_ativo:
    tempo = time.time() - st.session_state.inicio_unix
    mins, segs = divmod(int(tempo), 60)
    st.metric("⏳ Tempo", f"{mins:02d}:{segs:02d}")

# --- GUARDAR ---
if st.session_state.modo_guardar:
    with st.container(border=True):
        st.subheader("💾 Finalizar Registo")

        qtd = st.number_input("Quantidade", min_value=0.1, value=1.0)

        if st.button("✅ GUARDAR", use_container_width=True):

            try:
                minutos = round(st.session_state.minutos_finais, 2)
                custo = round(minutos * (valor_hora / 60), 2)
                perf = round(minutos / qtd, 2)

                novo = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Obra": obra,
                    "Material": material,
                    "Qtd": float(qtd),
                    "Minutos": minutos,
                    "Min/Un": perf,
                    "Custo": custo
                }])

                # Limpar valores vazios
                novo = novo.fillna("")

                # 👉 ESCREVER NA FOLHA (APPEND)
                conn.write(
                    spreadsheet=URL_FOLHA,
                    worksheet="Sheet1",
                    data=novo,
                    append=True
                )

                st.success("✅ Gravado com sucesso!")

                # Reset
                st.session_state.modo_guardar = False
                st.session_state.inicio_unix = None

                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao gravar: {e}")

# --- HISTÓRICO ---
st.divider()

try:
    df = conn.read(spreadsheet=URL_FOLHA, worksheet="Sheet1", ttl=0)
    st.subheader("📋 Últimos Registos")
    st.dataframe(df.tail(5), use_container_width=True)

except:
    st.warning("Ainda sem dados ou erro de ligação.")

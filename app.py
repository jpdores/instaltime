import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

# --- LIGAÇÃO FORÇADA ---
URL_FOLHA = "https://docs.google.com/spreadsheets/d/1-JaEy3L1Rhch29AkV-wYFLsqb2o_NX38I2iABNsSN4Q/edit"

try:
    # Tenta ligar usando o URL direto para evitar erro de "spreadsheet not specified"
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Erro crítico na configuração de conexão.")

# --- INTERFACE ---
st.markdown("<h1 style='text-align:center;'>🏗️ InstalTime Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>by <span style='color:red; font-weight:bold;'>Energipax</span></p>", unsafe_allow_html=True)

# Inicialização
for key in ["cronometro_ativo", "inicio_unix", "modo_guardar"]:
    if key not in st.session_state: st.session_state[key] = False

# Inputs
obra = st.text_input("Obra", "Geral")
material = st.text_input("Material", "Instalação")
valor_hora = st.sidebar.number_input("Valor/hora (€)", value=20.0)

# Cronómetro
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

# Gravação
if st.session_state.modo_guardar:
    with st.container(border=True):
        qtd = st.number_input("Quantidade", min_value=0.1, value=1.0)
        if st.button("✅ GUARDAR", use_container_width=True):
            try:
                # Criar linha
                novo = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Obra": obra, "Material": material, "Qtd": float(qtd),
                    "Minutos": round(st.session_state.minutos_finais, 2),
                    "Min/Un": round(st.session_state.minutos_finais/qtd, 2),
                    "Custo": round(st.session_state.minutos_finais * (valor_hora/60), 2)
                }])
                
                # OPERAÇÃO CRÍTICA: Ler e Atualizar com URL direto
            novo = novo.fillna("")

conn.write(
    spreadsheet=URL_FOLHA,
    worksheet="Sheet1",
    data=novo,
    append=True
)
                
                st.session_state.modo_guardar = False
                st.success("Gravado!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gravar: {e}")

# Histórico
st.divider()
try:
    df_ver = conn.read(spreadsheet=URL_FOLHA, worksheet="Sheet1", ttl=0)
    st.dataframe(df_ver.tail(5), use_container_width=True)
except:
    st.warning("Aguardando primeira gravação ou erro de permissão.")

import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

# --- LIGAÇÃO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INICIALIZAÇÃO DE MEMÓRIA ---
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False
if "inicio_unix" not in st.session_state:
    st.session_state.inicio_unix = None
if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False

# --- ESTILO ENERGIPAX ---
st.markdown("""
<style>
    .titulo { text-align: center; font-size: 34px; font-weight: 700; margin-bottom: 0; }
    .subtitulo { text-align: center; font-size: 16px; margin-top: 0; }
    .stButton>button { border-radius: 8px; }
</style>
<div class="titulo">🏗️ InstalTime Pro</div>
<div class="subtitulo">by <span style="color:red; font-size:20px; font-weight:700;">E</span>nergipax</div>
<hr>
""", unsafe_allow_html=True)

# --- SIDEBAR & CONFIGS ---
with st.sidebar:
    st.header("Configurações")
    valor_hora = st.number_input("Valor/hora (€)", value=20.0, step=0.5)

# --- INPUTS ---
col_obra, col_mat = st.columns(2)
with col_obra:
    obra = st.text_input("Nome da Obra", placeholder="Ex: Prédio A")
with col_mat:
    material = st.text_input("Material", placeholder="Ex: Tubo 20mm")

unidade = st.radio("Unidade", ["Metros", "Unidades", "Horas", "Outro"], horizontal=True)

# --- LÓGICA DO CRONÓMETRO ---
st.write("##") 

c1, c2 = st.columns(2)

with c1:
    if not st.session_state.cronometro_ativo and not st.session_state.modo_guardar:
        if st.button("▶️ INICIAR TRABALHO", use_container_width=True, type="primary"):
            st.session_state.inicio_unix = time.time()
            st.session_state.cronometro_ativo = True
            st.rerun()

with c2:
    if st.session_state.cronometro_ativo:
        if st.button("⏹️ PARAR AGORA", use_container_width=True, type="secondary"):
            duracao_segundos = time.time() - st.session_state.inicio_unix
            st.session_state.minutos_finais = duracao_segundos / 60
            st.session_state.cronometro_ativo = False
            st.session_state.modo_guardar = True
            st.rerun()

# --- MOSTRADOR EM TEMPO REAL ---
if st.session_state.cronometro_ativo:
    tempo_passado = time.time() - st.session_state.inicio_unix
    mins, segs = divmod(int(tempo_passado), 60)
    st.metric("⏳ Tempo Decorrido", f"{mins:02d}:{segs:02d}")
    time.sleep(1)
    st.button("🔄 Atualizar Relógio")

# --- JANELA DE FINALIZAÇÃO E ENVIO PARA GOOGLE ---
if st.session_state.modo_guardar:
    with st.container(border=True):
        st.write(f"#### 💾 Finalizar Registo")
        st.write(f"Tempo total: **{st.session_state.minutos_finais:.2f} min**")
        qtd = st.number_input(f"Quantidade instalada ({unidade})", min_value=0.01, value=1.0)
        
        if st.button("✅ CONFIRMAR E GUARDAR NO GOOGLE", use_container_width=True):
            try:
                custo = st.session_state.minutos_finais * (valor_hora / 60)
                perf = st.session_state.minutos_finais / qtd
                
                novo_registo = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Obra": obra if obra else "N/A",
                    "Material": material if material else "N/A",
                    "Qtd": float(qtd),
                    "Minutos": round(float(st.session_state.minutos_finais), 2),
                    "Min/Un": round(float(perf), 2),
                    "Custo": round(float(custo), 2)
                }])
                
                # Lê dados antigos da Google Sheet
                df_antigo = conn.read(worksheet="Sheet1", ttl=0)
                # Junta com o novo
                df_final = pd.concat([df_antigo, novo_registo], ignore_index=True)
                # Atualiza a Google Sheet
                conn.update(worksheet="Sheet1", data=df_final)
                
                st.session_state.modo_guardar = False
                st.success("Dados enviados para a nuvem!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gravar no Google: {e}")

# --- TABELA DE REGISTOS (Vinda do Google) ---
st.divider()
st.subheader("📋 Histórico Geral (Nuvem)")
try:
    df_google = conn.read(worksheet="Sheet1", ttl=0)
    st.dataframe(df_google.tail(10), use_container_width=True, hide_index=True)
except:
    st.info("A aguardar ligação com a Google Sheet...")

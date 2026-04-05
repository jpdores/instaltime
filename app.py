import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

# Configuração da Página Energipax
st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️", layout="centered")

# Ligação ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .titulo { text-align: center; color: #1E1E1E; margin-bottom: 0; }
    .vermelho { color: #FF0000; font-weight: bold; }
    </style>
    <h1 class="titulo">🏗️ InstalTime Pro</h1>
    <p style="text-align: center;">by <span class="vermelho">E</span>nergipax</p>
    <hr>
""", unsafe_allow_html=True)

# Inicializar variáveis de memória
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False
if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False

# --- INPUTS DE OBRA ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        obra = st.text_input("📍 Nome da Obra", value="Geral")
    with col2:
        material = st.text_input("🛠️ Material/Tarefa", value="Instalação")
    
    valor_hora = st.sidebar.number_input("💰 Valor Hora (€)", value=20.0)
    unidade = st.radio("Unidade", ["Metros", "Unidades", "Horas"], horizontal=True)

# --- LÓGICA DO CRONÓMETRO ---
st.write("##")
if not st.session_state.cronometro_ativo and not st.session_state.modo_guardar:
    if st.button("▶️ INICIAR TRABALHO", type="primary"):
        st.session_state.inicio_unix = time.time()
        st.session_state.cronometro_ativo = True
        st.rerun()

if st.session_state.cronometro_ativo:
    tempo_decorrido = (time.time() - st.session_state.inicio_unix) / 60
    st.metric("⏳ Tempo a decorrer", f"{tempo_decorrido:.2f} min")
    
    if st.button("⏹️ PARAR E REGISTAR"):
        st.session_state.minutos_finais = tempo_decorrido
        st.session_state.cronometro_ativo = False
        st.session_state.modo_guardar = True
        st.rerun()
    
    time.sleep(2)
    st.button("🔄 Atualizar Visor")

# --- JANELA DE GRAVAÇÃO (ONDE DAVA O ERRO) ---
if st.session_state.modo_guardar:
    with st.container(border=True):
        st.write("### 💾 Finalizar Registo")
        qtd = st.number_input(f"Quantidade em {unidade}", min_value=0.01, value=1.0)
        
        if st.button("✅ CONFIRMAR E GUARDAR NO GOOGLE"):
            try:
                custo = st.session_state.minutos_finais * (valor_hora / 60)
                
                # Criar nova linha de dados
                nova_linha = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Obra": obra,
                    "Material": material,
                    "Qtd": float(qtd),
                    "Minutos": round(float(st.session_state.minutos_finais), 2),
                    "Min/Un": round(float(st.session_state.minutos_finais/qtd), 2),
                    "Custo": round(float(custo), 2)
                }])
                
                # LER dados atuais (FORÇA Sheet1)
                df_atual = conn.read(worksheet="Sheet1", ttl=0)
                
                # JUNTAR dados
                df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
                
                # ATUALIZAR (O comando que grava na nuvem)
                conn.update(worksheet="Sheet1", data=df_final)
                
                st.session_state.modo_guardar = False
                st.success("🎯 Gravado com sucesso!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao ligar ao Google: {e}")
                st.info("Verifica se a aba da folha se chama 'Sheet1' e se tens permissão de 'Editor'.")

# --- HISTÓRICO ---
st.divider()
st.subheader("📋 Últimos Registos na Nuvem")
try:
    dados = conn.read(worksheet="Sheet1", ttl=0)
    st.dataframe(dados.tail(10), use_container_width=True, hide_index=True)
except:
    st.info("A aguardar dados da Google Sheet...")

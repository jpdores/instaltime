import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

# --- LIGAÇÃO À GOOGLE SHEET ---
# Nota: Precisas de configurar o link da folha nos "Secrets" do Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# Carregar dados existentes do Google Sheets
try:
    df_historico = conn.read(ttl="0s") # ttl=0s força a ler dados novos sempre
except:
    df_historico = pd.DataFrame(columns=["Data", "Obra", "Material", "Qtd", "Minutos", "Min/Un", "Custo"])

# --- ESTADOS DE SESSÃO ---
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False
if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False

# --- DESIGN ENERGIPAX ---
st.markdown('<h1 style="text-align:center;">🏗️ InstalTime Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;">by <span style="color:red; font-weight:bold;">E</span>nergipax</p>', unsafe_allow_html=True)
st.divider()

# --- INPUTS ---
obra = st.text_input("Obra")
material = st.text_input("Material")
valor_hora = st.sidebar.number_input("Valor Hora (€)", value=20.0)

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

if st.session_state.cronometro_ativo:
    st.info(f"⏳ A contar tempo...")
    time.sleep(1)
    st.button("Atualizar Visor")
    
# --- GUARDAR NO GOOGLE SHEETS (VERSÃO FORÇADA) ---
if st.session_state.modo_guardar:
    with st.container(border=True):
        st.write("### 💾 Finalizar Registo")
        qtd = st.number_input("Quantidade Instalada", min_value=0.01, value=1.0)
        
        if st.button("✅ GUARDAR DEFINITIVO", use_container_width=True):
            try:
                custo_total = st.session_state.minutos_finais * (valor_hora / 60)
                
                # Criar a linha de dados
                novo_registo = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Obra": str(obra) if obra else "Energipax",
                    "Material": str(material) if material else "Material",
                    "Qtd": float(qtd),
                    "Minutos": round(float(st.session_state.minutos_finais), 2),
                    "Min/Un": round(float(st.session_state.minutos_finais/qtd), 2),
                    "Custo": round(float(custo_total), 2)
                }])
                
                # Tenta ler a folha "Sheet1"
                df_existente = conn.read(worksheet="Sheet1", ttl=0)
                
                # Junta e Grava
                df_final = pd.concat([df_existente, novo_registo], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df_final)
                
                st.session_state.modo_guardar = False
                st.success("✅ Gravado com sucesso!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error("Falha na gravação.")
                st.info("Dica: Verifique se a aba da Google Sheet se chama 'Sheet1' (com S maiúsculo).")
                # Esta linha abaixo mostra o erro real para sabermos o que é:
                st.write(f"Erro técnico: {e}")
)

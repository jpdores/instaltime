import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="Energipax Pro", page_icon="🏗️")

# 2. Ligação ao Google Sheets
# A forma correta de chamar a ligação configurada nos Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Cabeçalho
st.markdown("<h1 style='text-align:center;'>🏗️ InstalTime Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:red; font-weight:bold;'>Energipax - Gestão de Obra</p>", unsafe_allow_html=True)
st.divider()

# 4. Memória da Sessão
if "cronometro_ativo" not in st.session_state:
    st.session_state.cronometro_ativo = False
if "modo_guardar" not in st.session_state:
    st.session_state.modo_guardar = False

# 5. Inputs de Obra
obra = st.text_input("Nome da Obra", "Geral")
material = st.text_input("Material / Tarefa", "Instalação")
valor_hora = st.sidebar.number_input("Valor Hora (€)", value=20.0)

# 6. Lógica do Cronómetro
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
    tempo_decorrido = (time.time() - st.session_state.inicio_unix) / 60
    st.info(f"⏳ Tempo a decorrer: {tempo_decorrido:.2f} min")
    time.sleep(2)
    st.button("Atualizar Visor")

# 7. Menu de Gravação Definitiva
if st.session_state.modo_guardar:
    with st.container(border=True):
        st.write("### 💾 Guardar Registo")
        qtd = st.number_input("Quantidade Instalada", min_value=0.01, value=1.0)
        
        if st.button("✅ CONFIRMAR E ENVIAR", use_container_width=True):
            try:
                custo = st.session_state.minutos_finais * (valor_hora / 60)
                
                novo_dado = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Obra": obra,
                    "Material": material,
                    "Qtd": float(qtd),
                    "Minutos": round(float(st.session_state.minutos_finais), 2),
                    "Min/Un": round(float(st.session_state.minutos_finais/qtd), 2),
                    "Custo": round(float(custo), 2)
                }])
                
                # Lê a Sheet1, junta o novo dado e atualiza
                df_antigo = conn.read(worksheet="Sheet1", ttl=0)
                df_final = pd.concat([df_antigo, novo_dado], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df_final)
                
                st.session_state.modo_guardar = False
                st.success("✅ Gravado no Google Sheets!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error("Erro na ligação ao Google.")
                st.write(f"Detalhe técnico: {e}")

# 8. Mostrar Tabela de Histórico
st.divider()
st.subheader("📋 Histórico em Tempo Real")
try:
    dados = conn.read(worksheet="Sheet1", ttl=0)
    st.dataframe(dados, use_container_width=True)
except:
    st.info("A aguardar dados da Google Sheet...")

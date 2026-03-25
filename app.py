import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

st.set_page_config(page_title="InstalTime Pro", page_icon="🏗️")

FILE = "dados_instaltime.csv"

# --- INICIALIZAÇÃO DE MEMÓRIA (SESSION STATE) ---
if "historico" not in st.session_state:
    if os.path.exists(FILE):
        try:
            st.session_state.historico = pd.read_csv(FILE).to_dict("records")
        except: st.session_state.historico = []
    else: st.session_state.historico = []

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

unidade = st.segmented_control("Unidade", ["Metros", "Unidades", "Horas", "Outro"], default="Metros")

# --- LÓGICA DO CRONÓMETRO ---
st.write("##") # Espaçamento

c1, c2 = st.columns(2)

with c1:
    if not st.session_state.cronometro_ativo and not st.session_state.modo_guardar:
        if st.button("▶️ INICIAR TRABALHO", use_container_width=True, type="primary"):
            st.session_state.inicio_unix = time.time() # Usa Unix Time para estabilidade
            st.session_state.cronometro_ativo = True
            st.rerun()

with c2:
    if st.session_state.cronometro_ativo:
        if st.button("⏹️ PARAR AGORA", use_container_width=True, type="secondary"):
            # Calcula o tempo final exato no momento do clique
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
    time.sleep(1) # Ajuda a manter a interface viva
    st.button("🔄 Atualizar Relógio")

# --- JANELA DE FINALIZAÇÃO ---
if st.session_state.modo_guardar:
    with st.container(border=True):
        st.write(f"#### 💾 Finalizar Registo")
        st.write(f"Tempo total: **{st.session_state.minutos_finais:.2f} min**")
        qtd = st.number_input(f"Quantidade instalada ({unidade})", min_value=0.01, value=1.0)
        
        if st.button("✅ CONFIRMAR E GUARDAR", use_container_width=True):
            custo = st.session_state.minutos_finais * (valor_hora / 60)
            perf = st.session_state.minutos_finais / qtd
            
            registo = {
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Obra": obra if obra else "N/A",
                "Material": material if material else "N/A",
                "Qtd": qtd,
                "Minutos": round(st.session_state.minutos_finais, 2),
                "Min/Un": round(perf, 2),
                "Custo (€)": round(custo, 2)
            }
            
            st.session_state.historico.append(registo)
            pd.DataFrame(st.session_state.historico).to_csv(FILE, index=False)
            
            st.session_state.modo_guardar = False
            st.success("Dados guardados com sucesso!")
            st.rerun()

# --- TABELA DE REGISTOS ---
if st.session_state.historico:
    st.divider()
    df = pd.DataFrame(st.session_state.historico)
    
    st.subheader("📋 Histórico de Hoje")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Total", f"{df['Custo (€)'].sum():.2f}€")
    m2.metric("⏱️ Minutos", f"{df['Minutos'].sum():.1f}")
    m3.metric("⚡ Média", f"{df['Min/Un'].mean():.2f} min/{unidade[:2]}")

    # Exportar e Limpar
    col_ex, col_limp = st.columns(2)
    with col_ex:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descarregar CSV", csv, "relatorio_energipax.csv", use_container_width=True)
    with col_limp:
        if st.button("🗑️ Limpar Tudo", use_container_width=True):
            st.session_state.historico = []
            if os.path.exists(FILE): os.remove(FILE)
            st.rerun()

import streamlit as st
from logic import executar_pericia, validar_agente # Importando a lógica separada

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="VisionScan Pro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Light"
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"

# Definição de cores para o contraste solicitado
if st.session_state.tema == "Light":
    bg, text, card = "#FFFFFF", "#2D3436", "#F9F9F9"
else:
    bg, text, card = "#0F172A", "#F1F5F9", "#1E293B"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {text}; }}
    .custom-menu {{ display: flex; justify-content: center; gap: 12px; margin-bottom: 40px; }}
    .report-card {{ background-color: {card}; padding: 25px; border-radius: 12px; border: 1px solid #ddd; }}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO E MENU ---
st.markdown("<h1 style='text-align: center; color: #007AFF;'>🛡️ VisionScan Pro</h1>", unsafe_allow_html=True)

st.markdown('<div class="custom-menu">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1: 
    if st.button("🔍 Scanner Free"): st.session_state.pagina = "Home"
with col2: 
    if st.button("🔑 Login"): st.session_state.pagina = "Login"
with col3: 
    if st.button("💎 Premium"): st.session_state.pagina = "Premium"
with col4: 
    if st.button("🛠️ Admin"): st.session_state.pagina = "Admin"
st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE PÁGINAS ---
CHAVE_API = "AIzaSyD6YZVV6CvbJyDU0NirMC5wxYD9zUMszmo"

if st.session_state.pagina == "Home":
    st.subheader("Análise de Evidência")
    file = st.file_uploader("Selecione a imagem para perícia", type=['jpg','png','jpeg'])
    
    if file:
        if st.button("EXECUTAR ANÁLISE FORENSE"):
            with st.status("🔍 Iniciando Motores...", expanded=True) as status:
                # Chama o Back-end passando o arquivo diretamente
                resultado = executar_pericia(file, CHAVE_API)
                status.update(label="Perícia Concluída!", state="complete")
            st.markdown(f"<div class='report-card'>{resultado}</div>", unsafe_allow_html=True)

# ... (outras páginas seguem a mesma lógica de chamar funções do logic.py)
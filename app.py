import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
import PIL.Image
import io

# --- 1. CONFIGURAÇÃO DE TEMA E INTERFACE ---
st.set_page_config(page_title="VisionScan Pro", layout="wide", initial_sidebar_state="collapsed")

# Gerenciamento de Tema (Light/Dark)
if 'tema' not in st.session_state: st.session_state.tema = "Light"
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"

def mudar_tema():
    st.session_state.tema = "Dark" if st.session_state.tema == "Light" else "Light"

# Paleta de Cores Dinâmica
if st.session_state.tema == "Light":
    bg_color, text_color, card_bg = "#F8F9FA", "#2D3436", "#FFFFFF"
    border_color, accent_color = "#E9ECEF", "#007AFF"
else:
    bg_color, text_color, card_bg = "#0F172A", "#F1F5F9", "#1E293B"
    border_color, accent_color = "#334155", "#00D4FF"

# Injeção de CSS Moderno e Menu com Gap de 12px
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Inter', sans-serif;
    }}
    
    /* Títulos */
    h1, h2, h3 {{ color: {accent_color}; font-weight: 800; }}

    /* Container do Menu Centralizado */
    .custom-menu-container {{
        display: flex;
        justify-content: center;
        gap: 12px; /* Espaçamento solicitado de 12px */
        margin: 20px 0 40px 0;
        flex-wrap: wrap;
    }}

    /* Estilização dos Botões de Menu (Cards) */
    .stButton>button {{
        background-color: {card_bg};
        color: {text_color};
        border: 1px solid {border_color};
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }}
    
    .stButton>button:hover {{
        border-color: {accent_color};
        color: {accent_color};
        transform: translateY(-2px);
        box-shadow: 0px 6px 12px rgba(0,0,0,0.1);
    }}

    /* Estilo do Relatório de IA */
    .report-card {{
        background-color: {card_bg};
        padding: 30px;
        border-radius: 16px;
        border: 1px solid {border_color};
        box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
        color: {text_color};
    }}

    /* Ajuste de Colunas para Menu */
    [data-testid="column"] {{
        width: auto !important;
        flex: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS E SEGURANÇA ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, password TEXT, plan TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS usage_control (ip TEXT PRIMARY KEY, used INTEGER)')
    conn.commit(); conn.close()

init_db()

# --- 3. LÓGICA DE PERFORMANCE (IA) ---
CHAVE_API = "AIzaSyD6YZVV6CvbJyDU0NirMC5wxYD9zUMszmo"

def otimizar_imagem(img):
    # Reduz o peso da imagem para acelerar o processamento
    max_size = (1024, 1024)
    img.thumbnail(max_size, PIL.Image.LANCZOS)
    return img

def processar_ia(img, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Atue como perito OSINT. Analise esta imagem detalhadamente: localize, identifique placas, marcas e objetos."
        response = model.generate_content([prompt, img])
        return response.text if response else "⚠️ Erro na resposta da IA."
    except Exception as e:
        return f"❌ Erro Técnico: {str(e)}"

# --- 4. RENDERIZAÇÃO DA INTERFACE ---

# Cabeçalho Superior
col_logo, col_theme = st.columns([9, 1])
with col_logo:
    st.markdown(f"<h1>🛡️ VisionScan Pro</h1>", unsafe_allow_html=True)
    st.caption("Inteligência Artificial Forense para Profissionais")
with col_theme:
    label_tema = "🌙 Dark" if st.session_state.tema == "Light" else "☀️ Light"
    st.button(label_tema, on_click=mudar_tema)

# MENU DE NAVEGAÇÃO COM GAP DE 12PX
st.markdown('<div class="custom-menu-container">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🔍 Scanner Free"): st.session_state.pagina = "Home"
with c2:
    if st.button("🔑 Login"): st.session_state.pagina = "Login"
with c3:
    if st.button("💎 Premium"): st.session_state.pagina = "Premium"
with c4:
    if st.button("🛠️ Admin"): st.session_state.pagina = "Admin"
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. PÁGINAS DO SISTEMA ---

if st.session_state.pagina == "Home":
    st.markdown("### 🔍 Escaneamento de Evidência")
    file = st.file_uploader("Arraste ou selecione sua imagem", type=['jpg','png','jpeg'])
    
    if file:
        st.image(file, width=400)
        if st.button("EXECUTAR ANÁLISE FORENSE"):
            with st.status("🔍 Periciando...", expanded=True) as status:
                img_pil = otimizar_imagem(PIL.Image.open(file))
                status.write("IA processando pixels e metadados...")
                resultado = processar_ia(img_pil, CHAVE_API)
                status.update(label="Análise Concluída!", state="complete")
            
            st.markdown(f"<div class='report-card'>{resultado}</div>", unsafe_allow_html=True)

elif st.session_state.pagina == "Login":
    st.markdown("### 🔑 Acesso ao Terminal")
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.text_input("E-mail do Agente")
        st.text_input("Senha de Acesso", type="password")
        st.button("Validar Credenciais")

elif st.session_state.pagina == "Premium":
    st.markdown("### 💎 Plano Investigador")
    st.write("Acesso ilimitado à API Gemini 1.5 Pro com maior resolução e histórico de nuvem.")
    st.button("Assinar via Checkout Seguro")

elif st.session_state.pagina == "Admin":
    st.markdown("### 🛠️ Gestão do Sistema")
    st.info("Acesse como admin@admin.com para gerenciar usuários e limpar logs de IP.")
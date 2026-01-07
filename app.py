import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
import PIL.Image
import io

# --- 1. CONFIGURAÇÃO DE UI/UX ---
st.set_page_config(page_title="VisionScan AI Pro", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    [data-testid="stAppViewContainer"] { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT, password TEXT, birth TEXT, plan TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS usage_control (ip TEXT PRIMARY KEY, used INTEGER)')
    conn.commit()
    conn.close()

init_db()

# --- 3. CÉREBRO DA IA (SOLUÇÃO DEFINITIVA PARA O ERRO 404) ---
def processar_ia(img, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # LÓGICA DE AUTO-DETECÇÃO: 
        # Em vez de escrever o nome, vamos buscar na lista oficial do Google o que está ativo
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prioridade 1: Tenta o Flash 1.5 (Mais rápido/barato)
        # Prioridade 2: Tenta qualquer modelo que contenha 'flash'
        # Prioridade 3: Pega o primeiro da lista
        target_model = None
        for m in available_models:
            if 'gemini-1.5-flash' in m:
                target_model = m
                break
        
        if not target_model:
            for m in available_models:
                if 'flash' in m:
                    target_model = m
                    break
        
        if not target_model and available_models:
            target_model = available_models[0]

        if not target_model:
            return "❌ Erro: Nenhum modelo de IA disponível para esta chave."

        # Inicializa o modelo com o nome exato fornecido pelo Google
        model = genai.GenerativeModel(model_name=target_model)
        prompt = "Atue como perito OSINT profissional. Analise detalhadamente esta imagem: identifique placas, marcas, localização aproximada e detalhes de fundo úteis para investigação."
        
        response = model.generate_content([prompt, img])
        
        if response and response.text:
            return response.text
        return "⚠️ A IA processou, mas o relatório veio vazio."
        
    except Exception as e:
        # Se o erro for 404, mostramos quais modelos a chave REALMENTE possui
        if "404" in str(e):
            try:
                models = [m.name for m in genai.list_models()]
                return f"❌ Erro 404: O modelo solicitado não existe. Modelos disponíveis na sua chave: {models}"
            except:
                pass
        return f"❌ Erro Crítico: {str(e)}"

# --- 4. INTERFACE ---
st.title("🛡️ VisionScan Pro")

# Chave API que você forneceu
CHAVE_CLIENTE = "AIzaSyCHOfkp2KXaiiFIDFrHV_PsdgrZLliSXb8"

if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    tab1, tab2, tab3 = st.tabs(["🔍 Scanner Free", "🔑 Entrar", "📝 Assinar"])
    
    with tab1:
        st.subheader("Teste Gratuito")
        file = st.file_uploader("Escolha a foto", type=['jpg','png','jpeg'], key="free_up")
        if file and st.button("Analisar Gratuitamente"):
            with st.spinner("IA Analisando..."):
                img_pil = PIL.Image.open(file)
                st.markdown(processar_ia(img_pil, CHAVE_CLIENTE))

    with tab2:
        e_l = st.text_input("E-mail", key="l_email")
        p_l = st.text_input("Senha", type="password", key="l_pass")
        if st.button("Login"):
            conn = sqlite3.connect('database.db'); c = conn.cursor()
            c.execute("SELECT name, plan FROM users WHERE email=? AND password=?", (e_l, p_l))
            user = c.fetchone()
            if user:
                st.session_state.logado = True
                st.session_state.user_data = {"name": user[0], "plan": user[1], "email": e_l}
                st.rerun()
            else:
                st.error("Login inválido.")
            conn.close()

    with tab3:
        n_n = st.text_input("Nome", key="r_name")
        n_e = st.text_input("E-mail", key="r_email")
        n_p = st.text_input("Senha", type="password", key="r_pass")
        if st.button("Cadastrar"):
            conn = sqlite3.connect('database.db')
            plano = "master" if n_e == "admin@admin.com" else "premium"
            try:
                conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (n_e, n_n, n_p, "", plano))
                conn.commit()
                st.success("Cadastrado com sucesso! Vá em Entrar.")
            except:
                st.error("Erro no cadastro.")
            conn.close()

else:
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"logado": False}))
    if st.session_state.user_data['plan'] == "master":
        st.header("👑 Painel Master")
        conn = sqlite3.connect('database.db')
        st.dataframe(pd.read_sql_query("SELECT * FROM users", conn))
        conn.close()
    else:
        st.header(f"🚀 Premium: {st.session_state.user_data['name']}")
        file_p = st.file_uploader("Suba evidência", type=['jpg','png'], key="p_up")
        if file_p and st.button("Análise Profunda"):
             with st.spinner("Processando..."):
                st.markdown(processar_ia(PIL.Image.open(file_p), CHAVE_CLIENTE))
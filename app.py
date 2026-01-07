import streamlit as st
from logic import executar_pericia, validar_agente, registar_utilizador, check_ip_limit, register_ip_usage

# --- 1. CONFIGURAÇÃO DE TEMA E SESSÃO ---
st.set_page_config(page_title="VisionScan Pro", layout="wide", initial_sidebar_state="collapsed")

if 'tema' not in st.session_state: st.session_state.tema = "Light"
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'usuario_logado' not in st.session_state: st.session_state.usuario_logado = None

def alternar_tema():
    st.session_state.tema = "Dark" if st.session_state.tema == "Light" else "Light"

# Paleta de Cores de Alto Contraste
if st.session_state.tema == "Light":
    bg, text, card, border = "#FFFFFF", "#1E293B", "#F8FAFC", "#E2E8F0"
    input_bg, input_text, btn_bg = "#FFFFFF", "#1E293B", "#1E293B"
    header_bg = "#FFFFFF"
else:
    bg, text, card, border = "#0F172A", "#F8FAFC", "#1E293B", "#334155"
    input_bg, input_text, btn_bg = "#1E293B", "#F8FAFC", "#334155"
    header_bg = "#0F172A"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {text}; transition: 0.3s; }}
    header[data-testid="stHeader"] {{ background-color: {header_bg} !important; }}
    .stButton > button {{ background-color: {btn_bg} !important; color: white !important; border-radius: 8px !important; }}
    .stButton > button p {{ color: white !important; }}
    div[data-baseweb="input"] {{ background-color: {input_bg} !important; border: 1px solid {border} !important; }}
    input {{ color: {input_text} !important; -webkit-text-fill-color: {input_text} !important; }}
    label {{ color: {text} !important; font-weight: 600; }}
    .title-btn > button {{ background: none !important; border: none !important; color: #007AFF !important; font-size: 2.2rem !important; font-weight: bold !important; }}
    @keyframes pulse {{ 0% {{ transform: scale(1); }} 70% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
    .premium-btn > button {{ animation: pulse 2s infinite; background-color: #007AFF !important; color: white !important; }}
    .report-card {{ background-color: {card}; padding: 25px; border-radius: 12px; border: 1px solid {border}; color: {text}; border-left: 5px solid #007AFF; margin-top: 20px; }}
</style>
""", unsafe_allow_html=True)

# --- 2. CABEÇALHO ---
h_col1, h_col2, h_col3 = st.columns([6, 2, 2])
with h_col1:
    st.markdown('<div class="title-btn">', unsafe_allow_html=True)
    if st.button("🛡️ VisionScan Pro"):
        st.session_state.pagina = "Home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with h_col2:
    st.button("🌙 Dark" if st.session_state.tema == "Light" else "☀️ Light", on_click=alternar_tema, use_container_width=True)
with h_col3:
    if st.session_state.usuario_logado:
        with st.expander(f"👤 {st.session_state.usuario_logado['name'].split()[0]}"):
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.usuario_logado = None
                st.session_state.pagina = "Home"
                st.rerun()
    else:
        if st.button("🔑 Acesso Agente", use_container_width=True):
            st.session_state.pagina = "Acesso"
            st.rerun()

st.markdown("---")

# --- 3. LOGICA DE IP E SECRETS ---
try:
    user_ip = st.context.headers.get("x-forwarded-for", "127.0.0.1").split(",")[0]
except:
    user_ip = "127.0.0.1"

if "GEMINI_API_KEY" in st.secrets:
    CHAVE_API = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Configure GEMINI_API_KEY no secrets.toml.")
    st.stop()

# --- 4. NAVEGAÇÃO ---
if st.session_state.pagina == "Home":
    st.markdown("### 🧪 Central de Assistente de Pesquisa")
    pode_analisar = False
    ip_ja_usou = check_ip_limit(user_ip)

    if not st.session_state.usuario_logado:
        if ip_ja_usou:
            st.error("⚠️ Para realizar novas pesquisas, cadastre-se.")
            if st.button("Criar minha conta"):
                st.session_state.pagina = "Acesso"
                st.rerun()
        else:
            st.info("Você possui 1 consulta gratuita disponível.")
            pode_analisar = True
    else:
        if st.session_state.usuario_logado['plan'] == 'free':
            st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
            if st.button("💎 ADERIR AO PREMIUM PRO"):
                st.session_state.pagina = "Premium"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            pode_analisar = False
        else:
            st.success("💎 Modo Assistente Pro Ativado.")
            pode_analisar = True

    file = st.file_uploader("Upload de Evidência", type=['jpg','png','jpeg'])
    if file:
        st.image(file, width=500)
        if st.button("EXECUTAR PESQUISA PROFUNDA", disabled=not pode_analisar):
            with st.status("🔍 Consultando fontes globais...", expanded=True) as status:
                resultado = executar_pericia(file, CHAVE_API)
                if not st.session_state.usuario_logado: register_ip_usage(user_ip)
                status.update(label="Pesquisa Concluída!", state="complete")
            
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown(resultado)
            st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.pagina == "Acesso":
    st.markdown("### 🔐 Área de Acesso")
    t_login, t_reg = st.tabs(["🔑 Login", "📝 Cadastro"])
    with t_login:
        email = st.text_input("E-mail", key="log_em")
        senha = st.text_input("Senha", type="password", key="log_pw")
        if st.button("Entrar"):
            user = validar_agente(email, senha)
            if user:
                st.session_state.usuario_logado = user
                st.session_state.pagina = "Home"
                st.rerun()
            else: st.error("E-mail ou senha inválidos.")
    with t_reg:
        n = st.text_input("Nome Completo", key="reg_n")
        e = st.text_input("E-mail Profissional", key="reg_e")
        s = st.text_input("Senha Segura", type="password", key="reg_s")
        if st.button("Criar Minha Conta"):
            ok, msg = registar_utilizador(n, e, s)
            if ok: st.success("Conta criada! Faça o login na aba ao lado.")
            else: st.error(msg)

elif st.session_state.pagina == "Premium":
    st.markdown("### 💎 Plano Assistente de Pesquisa Pro")
    st.write("Libere acesso ao modelo Gemini 1.5 Pro e pesquisas ilimitadas.")
    if st.button("Voltar para Início"):
        st.session_state.pagina = "Home"
        st.rerun()
import streamlit as st

# =========================================================
# CONFIGURAÇÃO GLOBAL
# =========================================================
st.set_page_config(
    page_title="VisionScan Pro | OSINT AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# IMPORTS DO CORE
# =========================================================
from logic import (
    registar_utilizador,
    executar_pericia,
    auth_login,
    auth_get_user,
    auth_logout,
    get_user_data
)

# =========================================================
# SESSION STATE DEFAULTS
# =========================================================
defaults = {
    "tema": "Light",
    "pagina": "Home",
    "usuario_logado": None,
    "resultado": None,
    "uploader_key": 0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================================================
# FUNÇÕES DE NAVEGAÇÃO / UI
# =========================================================
def alternar_tema():
    st.session_state.tema = "Dark" if st.session_state.tema == "Light" else "Light"

def ir_home():
    st.session_state.pagina = "Home"

def ir_planos():
    st.session_state.pagina = "Planos"

def ir_acesso():
    st.session_state.pagina = "Acesso"

def logout():
    auth_logout()
    st.session_state.clear()
    # st.rerun() não é necessário em callbacks

# =========================================================
# TEMA / CORES — REESTRUTURADO PARA CONTRASTE PERFEITO
# =========================================================
if st.session_state.tema == "Light":
    # Paleta Light
    bg = "#FFFFFF"
    text = "#0F172A"
    card = "#F8FAFC"
    border = "#E5E7EB"
    sub = "#64748B"
    button_bg = "#EFF6FF"          # Azul claro suave
    button_text = "#2563EB"        # Azul escuro (legível)
    button_hover = "#DBEAFE"       # Hover mais claro
    primary = "#2563EB"
else:
    # Paleta Dark
    bg = "#0F172A"                 # Fundo escuro elegante (não preto puro)
    text = "#F8FAFC"               # Texto claro
    card = "#1E293B"               # Card um pouco mais claro que o fundo
    border = "#334155"             # Borda sutil
    sub = "#94A3B8"                # Texto secundário
    button_bg = "#1E3A8A"          # Azul escuro rico
    button_text = "#BFDBFE"        # Azul claro suave (legível)
    button_hover = "#1D4ED8"       # Hover mais intenso
    primary = "#3B82F6"

# =========================================================
# CSS GLOBAL — COMPATÍVEL COM STREAMLIT MODERNO
# =========================================================
st.markdown(f"""
<style>
/* Fundo e texto global */
.stApp {{
    background-color: {bg} !important;
    color: {text} !important;
}}

/* Botões - novo seletor para Streamlit >=1.36 */
button[kind="secondary"] {{
    background-color: {button_bg} !important;
    color: {button_text} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
}}

button[kind="secondary"]:hover {{
    background-color: {button_hover} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
}}

/* Header */
header {{
    background-color: {bg} !important;
    color: {text} !important;
}}

/* Cards personalizados */
.hero, .plano-card-3d, .report-card, .pricing-card {{
    background-color: {card} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
}}

/* Inputs */
input, select {{
    background-color: {card} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
}}

/* Labels dos inputs */
.stTextInput > label,
.stPasswordInput > label {{
    color: {text} !important;
    font-weight: 600 !important;
    display: block !important;
    margin-bottom: 0.5rem !important;
}}

/* Mensagens */
div[data-testid="stNotification"] {{
    color: {text} !important;
}}

/* Estilos da Home */
.hero h1 {{
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.2;
    color: {text} !important;
}}
.hero p {{
    color: {sub} !important;
    font-size: 1.15rem;
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
h1, h2, h3 = st.columns([6,2,2])

with h1:
    st.button("🛡️ VisionScan Pro", key="nav_home", on_click=ir_home)

with h2:
    st.button(
        "🌙 Dark Mode" if st.session_state.tema == "Light" else "☀️ Light Mode",
        key="nav_theme",
        on_click=alternar_tema
    )

with h3:
    if st.session_state.usuario_logado:
        st.markdown(f"👤 **{st.session_state.usuario_logado['name']}**")
        st.button("🚪 Sair", key="nav_logout", on_click=logout)
    else:
        st.button("🔑 Acesso Agente", key="nav_login", on_click=ir_acesso)

st.markdown("---")

# =========================================================
# HOME
# =========================================================
if st.session_state.pagina == "Home":

    # ===========================
    # HERO SECTION
    # ===========================
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 16px; margin-bottom: 40px;">
        <h1 style="font-size: 2.8rem; font-weight: 800; color: #0f172a; line-height: 1.2;">Transforme pixels em evidências.</h1>
        <p style="font-size: 1.2rem; color: #64748b; max-width: 600px; margin: 20px auto;">Análise pericial OSINT com IA multimodal. Geolocalização, busca ativa e laudos estruturados — tudo em segundos.</p>
    </div>
    """, unsafe_allow_html=True)

    # 🔒 FORÇAR LOGIN PARA QUALQUER ANÁLISE REAL
    if st.session_state.usuario_logado is None:
        st.info("🔑 Faça login para usar sua consulta gratuita.")
    else:
        # Buscar dados ATUALIZADOS do banco (fonte de verdade)
        db_user = get_user_data(st.session_state.usuario_logado["email"])
        if not db_user:
            st.error("❌ Erro ao carregar seus dados. Faça logout e login novamente.")
        else:
            plan = db_user.get("plan", "free")
            credits = db_user.get("credits", 0)
            pode_analisar = (plan != "free") or (credits > 0)

            if not pode_analisar:
                st.error("❌ Sua consulta gratuita já foi utilizada.")
            else:
                st.info("🎁 Você possui 1 consulta gratuita disponível.")
                file = st.file_uploader(
                    "Arraste sua evidência aqui",
                    type=["jpg","jpeg","png","webp","heic"],
                    key=f"upload_file_{st.session_state.uploader_key}"
                )

                # Botão de análise (só aparece se houver arquivo)
                if st.button("🔍 EXECUTAR PESQUISA PROFUNDA", key="btn_analisar"):
                    with st.spinner("🔍 Analisando imagem..."):
                        resultado = executar_pericia(file, st.secrets["GEMINI_API_KEY"])
                        from logic import consumir_credito, get_user_data
        
                        # Consumir crédito no banco
                        sucesso = consumir_credito(st.session_state.usuario_logado["id"])
                        if sucesso:
                            # ATUALIZAR DADOS FRESH DO BANCO IMEDIATAMENTE
                            db_user_atualizado = get_user_data(st.session_state.usuario_logado["email"])
                            if db_user_atualizado:
                                st.session_state.usuario_logado["credits"] = db_user_atualizado.get("credits", 0)
                            st.session_state.resultado = resultado
                        else:
                            st.warning("⚠️ Análise concluída, mas houve erro ao registrar uso.")
                            st.session_state.resultado = resultado

    # Exibir preview da imagem (só se houver arquivo)
    if 'file' in locals() and file:
        st.image(file, use_container_width=True)

    # RESULTADO (NUNCA VAZA)
    if st.session_state.resultado:
        if st.session_state.usuario_logado is None:
            st.session_state.resultado = None
        else:
            st.markdown(
                f"<div class='report-card'>{st.session_state.resultado}</div>",
                unsafe_allow_html=True
            )

    # ===========================
    # BENEFÍCIOS / DIFERENCIAIS
    # ===========================
    st.markdown("## 🔍 Por que usar o VisionScan Pro?")
    cols = st.columns(3)

    with cols[0]:
        st.markdown("""
        <div style="padding:20px; background:#f8fafc; border-radius:12px; border-left:4px solid #2563eb; height:100%;">
            <h3 style="color:#0f172a; font-size:1.2rem; margin-bottom:10px;">🌐 Busca Ativa</h3>
            <p style="color:#64748b; font-size:0.95rem;">Validação em tempo real. Rastreamento automático em redes sociais, fóruns, marketplaces e mais.</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown("""
        <div style="padding:20px; background:#f8fafc; border-radius:12px; border-left:4px solid #10b981; height:100%;">
            <h3 style="color:#0f172a; font-size:1.2rem; margin-bottom:10px;">📍 Geolocalização</h3>
            <p style="color:#64748b; font-size:0.95rem;">Análise contextual avançada. Identificação de ruas, placas, vegetação, sombras e clima — até mesmo em fotos desfocadas.</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown("""
        <div style="padding:20px; background:#f8fafc; border-radius:12px; border-left:4px solid #8b5cf6; height:100%;">
            <h3 style="color:#0f172a; font-size:1.2rem; margin-bottom:10px;">🛡️ Rigor Técnico</h3>
            <p style="color:#64748b; font-size:0.95rem;">Laudos estruturados, com nível de confiança e hipóteses alternativas — prontos para uso em processos legais.</p>
        </div>
        """, unsafe_allow_html=True)

    
    # ===========================
    # PLANOS DE INVESTIGAÇÃO — 3D MODERN CARD
    # ===========================
    st.markdown("## 📊 Planos de Investigação")
    st.markdown("Créditos não expiram. Acumulam. Uso sob demanda.")

    planos = [
        ("10 Consultas", "R$ 29,90", "https://checkout.exemplo/10", "#F59E0B"),
        ("25 Consultas", "R$ 59,90", "https://checkout.exemplo/25", "#10B981"),
        ("50 Consultas", "R$ 69,90", "https://checkout.exemplo/50", "#3B82F6"),
        ("100 Consultas", "R$ 89,90", "https://checkout.exemplo/100", "#8B5CF6"),
    ]

    # CSS personalizado para efeitos 3D e hover
    st.markdown("""
    <style>
    .plano-card-3d {
        background: white;
        border-radius: 16px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 
            0 10px 20px rgba(0,0,0,0.08),
            0 4px 6px rgba(0,0,0,0.05);
        transform-style: preserve-3d;
        backface-visibility: hidden;
    }
    
    .plano-card-3d::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-color);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.5s ease;
    }
    
    .plano-card-3d:hover {
        transform: translateY(-8px) rotateX(2deg);
        box-shadow: 
            0 20px 40px rgba(0,0,0,0.15),
            0 8px 16px rgba(0,0,0,0.1);
        z-index: 10;
    }
    
    .plano-card-3d:hover::before {
        transform: scaleX(1);
    }
    
    .plano-card-3d .glow {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, var(--primary-color)20%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
        pointer-events: none;
        z-index: -1;
    }
    
    .plano-card-3d:hover .glow {
        opacity: 0.15;
    }
    
    .btn-comprar-plano {
        display: block;
        width: 100%;
        padding: 12px;
        text-align: center;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        outline: none;
        margin-top: 16px;
        font-size: 0.95rem;
    }
    
    .btn-comprar-plano.logado {
        background: var(--primary-color);
        color: white;
    }
    
    .btn-comprar-plano.logado:hover {
        background: var(--primary-color-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .btn-comprar-plano.deslogado {
        background: #f3f4f6;
        color: #6b7280;
        border: 1px solid #d1d5db;
    }
    
    .btn-comprar-plano.deslogado:hover {
        background: #e5e7eb;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (nome, preco, link, cor) in enumerate(planos):
        col = cols[i % 2]
        with col:
            # Card 3D
            st.markdown(f"""
            <div class="plano-card-3d" style="--primary-color: {cor}; --primary-color-dark: {cor}dd;">
                <div class="glow"></div>
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
                    <div style="width:10px; height:10px; background:{cor}; border-radius:50%;"></div>
                    <h3 style="font-size:1.25rem; font-weight:700; color:#0f172a; margin:0;">{nome}</h3>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:{cor}; margin:16px 0;">{preco}</div>
                <p style="color:#64748b; font-size:0.9rem; margin-bottom:20px;">Créditos não expiram</p>
            """, unsafe_allow_html=True)

            if st.session_state.usuario_logado:
                if st.button(
                    "Comprar agora",
                    key=f"comprar_{nome.replace(' ', '_')}",
                    use_container_width=True,
                    help="Clique para ser redirecionado ao checkout"
                ):
                    st.markdown(f'<script>window.open("{link}", "_blank");</script>', unsafe_allow_html=True)
            else:
                if st.button(
                    "Comprar agora",
                    key=f"login_{nome.replace(' ', '_')}",
                    use_container_width=True,
                    help="Faça login para comprar"
                ):
                    st.session_state.pagina = "Acesso"

            st.markdown("</div>", unsafe_allow_html=True)

    # ===========================
    # TESTEMUNHO / CONFIANÇA
    # ===========================
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:30px; background:#f8fafc; border-radius:16px; margin-top:40px;">
        <h3 style="color:#0f172a; font-size:1.4rem; margin-bottom:10px;">✅ Já utilizado por mais de 500 agentes de investigação</h3>
        <p style="color:#64748b; font-size:1rem;">Tecnologia confiável, resultados precisos e laudos admissíveis em tribunal.</p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PLANOS
# =========================================================
elif st.session_state.pagina == "Planos":

    st.markdown("## 💳 Planos & Créditos")
    st.markdown("""
    - Créditos não expiram  
    - Acumulam  
    - Uso sob demanda  
    """)

    # Definir planos
    planos = [
        ("10 Consultas", "R$ 29,90", "https://checkout.exemplo/10", "#F59E0B"),
        ("25 Consultas", "R$ 59,90", "https://checkout.exemplo/25", "#10B981"),
        ("50 Consultas", "R$ 69,90", "https://checkout.exemplo/50", "#3B82F6"),
        ("100 Consultas", "R$ 89,90", "https://checkout.exemplo/100", "#8B5CF6"),
    ]

    # CSS personalizado para cards e botões
    st.markdown("""
    <style>
    .plano-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 20px;
        border: 2px solid transparent;
    }
    .plano-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border-color: var(--primary-color);
    }
    .plano-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    .plano-preco {
        font-size: 1.6rem;
        font-weight: 800;
        color: var(--primary-color);
        margin: 12px 0;
    }
    .btn-comprar {
        display: block;
        width: 100%;
        padding: 12px;
        text-align: center;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
        border: none;
        outline: none;
    }
    .btn-comprar:hover {
        transform: scale(1.02);
    }
    .btn-comprar.deslogado {
        background: #f3f4f6;
        color: #6b7280;
        border: 1px solid #d1d5db;
    }
    .btn-comprar.deslogado:hover {
        background: #e5e7eb;
    }
    .btn-comprar.logado {
        background: var(--primary-color);
        color: white;
    }
    .btn-comprar.logado:hover {
        background: var(--primary-color-dark);
    }
    </style>
    """, unsafe_allow_html=True)

    # Mensagem para usuário deslogado
    if not st.session_state.usuario_logado:
        st.info("🔒 Faça login para comprar créditos e acessar planos premium.")
        st.markdown("---")

    # Renderizar planos
    cols = st.columns(2)
    for i, (nome, preco, link, cor) in enumerate(planos):
        col = cols[i % 2]
        with col:
            st.markdown(f"""
            <div class="plano-card" style="--primary-color: {cor}; --primary-color-dark: {cor}dd;">
                <div class="plano-title">🎟️ {nome}</div>
                <div class="plano-preco">{preco}</div>
            """, unsafe_allow_html=True)

            if st.session_state.usuario_logado:
                # Botão para comprar (logado)
                if st.button(
                    "Comprar agora",
                    key=f"comprar_{nome.replace(' ', '_')}",
                    use_container_width=True,
                    help="Clique para ser redirecionado ao checkout"
                ):
                    st.markdown(f'<script>window.open("{link}", "_blank");</script>', unsafe_allow_html=True)
            else:
                # Botão para login (deslogado)
                if st.button(
                    "Comprar agora",
                    key=f"login_{nome.replace(' ', '_')}",
                    use_container_width=True,
                    help="Faça login para comprar"
                ):
                    st.session_state.pagina = "Acesso"

            st.markdown("</div>", unsafe_allow_html=True)

    # Botão voltar
    st.markdown("---")
    st.button("⬅️ Voltar", key="voltar_home", on_click=ir_home)

# =========================================================
# LOGIN / CADASTRO — SEM TABS (FIX VISUAL)
# =========================================================
elif st.session_state.pagina == "Acesso":

    st.markdown("## 🔐 Área do Agente")

    # Estado para controlar qual aba está ativa
    if "aba_ativa" not in st.session_state:
        st.session_state.aba_ativa = "entrar"

    # Botões manuais para simular tabs
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Entrar", key="btn_entrar", use_container_width=True):
            st.session_state.aba_ativa = "entrar"
    with col2:
        if st.button("Criar Conta", key="btn_criar_conta", use_container_width=True):
            st.session_state.aba_ativa = "criar_conta"

    # Linha de separação
    st.markdown("---")

    # Conteúdo baseado na aba ativa
    if st.session_state.aba_ativa == "entrar":
        st.markdown("### 👤 Entrar")
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        if st.button("Entrar", key="btn_login"):
            try:
                from logic import supabase
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": senha
                })
                
                if not getattr(res.user, 'email_confirmed_at', None):
                    st.warning("⚠️ E-mail não confirmado. Verifique sua caixa de entrada.")
                    st.stop()
                    
                # BUSCA APENAS OS DADOS EXISTENTES
                db_user = get_user_data(res.user.email)
                
                if not db_user:
                    # USUÁRIO NUNCA LOGOU ANTES - CRIA COM CREDITOS = 1
                    name = res.user.user_metadata.get("name") if res.user.user_metadata else res.user.email.split("@")[0]
                    supabase.table("users").insert({
                        "id": res.user.id,
                        "email": res.user.email,
                        "name": name,
                        "plan": "free",
                        "credits": 1
                    }).execute()
                    db_user = get_user_data(res.user.email)
                
                if db_user:
                    st.session_state.usuario_logado = {
                        "id": db_user["id"],
                        "email": db_user["email"],
                        "name": db_user.get("name", res.user.email.split("@")[0]),
                        "plan": db_user.get("plan", "free"),
                        "credits": db_user.get("credits", 0)
                    }
                    st.session_state.pagina = "Home"
                    st.rerun()
                else:
                    st.error("Erro ao carregar dados do usuário.")
                    
            except Exception as auth_error:
                error_msg = str(auth_error).lower()
                if "invalid credentials" in error_msg or "user not found" in error_msg:
                    st.error("Credenciais inválidas ou usuário não encontrado.")
                else:
                    st.error(f"Erro de autenticação: {str(auth_error)}")

    else:  # Criar Conta
        st.markdown("### 🆕 Criar Conta")
        nome = st.text_input("Nome completo", key="cad_nome")
        email = st.text_input("E-mail", key="cad_email")
        senha = st.text_input("Senha", type="password", key="cad_senha")

        if st.button("Criar conta", key="btn_cadastrar"):
            ok, msg = registar_utilizador(nome, email, senha)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
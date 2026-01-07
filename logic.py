import google.generativeai as genai
from supabase import create_client, Client
import PIL.Image
import streamlit as st

# --- 1. CONFIGURAÇÃO SUPABASE (VIA SECRETS) ---
try:
    # Busca as credenciais no arquivo .streamlit/secrets.toml
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Erro ao carregar segredos do Supabase: {e}")

# --- 2. LÓGICA DE SEGURANÇA E IP ---
def check_ip_limit(ip):
    """Verifica se o IP já realizou uma consulta gratuita"""
    try:
        res = supabase.table("access_logs").select("*").eq("ip_address", ip).execute()
        return len(res.data) > 0
    except: return False

def register_ip_usage(ip):
    """Registra o uso do IP para a barreira de segurança"""
    try: supabase.table("access_logs").insert({"ip_address": ip}).execute()
    except: pass

# --- 3. LÓGICA DE IA (SISTEMA DE FALLBACK CONTRA ERRO 404) ---
def executar_pericia(img_file, api_key):
    """Executa análise profunda usando o melhor modelo disponível para a chave"""
    try:
        genai.configure(api_key=api_key)
        
        # Lista dinamicamente os modelos permitidos para evitar erro 404
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prioridades: Pro (Com Busca) -> Flash (Rápido)
        prioridades = ["models/gemini-1.5-pro", "models/gemini-1.5-flash"]
        modelo_escolhido = next((p for p in prioridades if p in modelos_disponiveis), modelos_disponiveis[0])

        # Habilita Google Search Grounding apenas nos modelos compatíveis
        tools = [{"google_search_retrieval": {}}] if "1.5" in modelo_escolhido else None
        
        model = genai.GenerativeModel(model_name=modelo_escolhido, tools=tools)
        
        img = PIL.Image.open(img_file)
        img.thumbnail((1024, 1024), PIL.Image.LANCZOS)
        
        prompt = f"""
        Você é um Assistente de Pesquisa Profissional. Analise esta imagem com rigor técnico:
        1. LOCALIZAÇÃO: Identifique país, cidade e bairro através de arquitetura e vegetação.
        2. PESQUISA ATIVA: Use o Google para validar nomes de estabelecimentos e marcas locais.
        3. SENSIBILIDADE: Detecte detalhes em reflexos, placas e equipamentos de segurança.
        4. CONCLUSÃO: Apresente um laudo estruturado com fontes e links.
        (Análise processada via: {modelo_escolhido})
        """
        
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"❌ Erro Crítico na IA: {str(e)}"

# --- 4. GESTÃO DE USUÁRIOS ---
def validar_agente(email, senha):
    try:
        res = supabase.table("users").select("*").eq("email", email).eq("password", senha).execute()
        return res.data[0] if res.data else None
    except: return None

def registar_utilizador(nome, email, senha, plano="free"):
    try:
        data = {"name": nome, "email": email, "password": senha, "plan": plano}
        supabase.table("users").insert(data).execute()
        return True, "Sucesso"
    except Exception as e:
        return False, "E-mail já cadastrado." if "already exists" in str(e).lower() else (False, str(e))
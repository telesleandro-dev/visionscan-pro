import google.generativeai as genai
from supabase import create_client, Client
import PIL.Image
import streamlit as st
from uuid import UUID

# =========================================================
# SUPABASE
# =========================================================
supabase: Client | None = None
try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
except Exception as e:
    st.error(f"Erro de conexão com o banco: {e}")

# =========================================================
# MOTOR DE PERÍCIA OSINT (ESTÁVEL)
# =========================================================
def executar_pericia(img_file, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)

        modelos_disponiveis = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]

        preferidos = [
            "models/gemini-1.5-flash",
            "models/gemini-1.0-pro",
            "models/gemini-pro"
        ]

        modelo_escolhido = next(
            (m for m in preferidos if m in modelos_disponiveis),
            modelos_disponiveis[0]
        )

        model = genai.GenerativeModel(model_name=modelo_escolhido)

        prompt = """
Você é um PERITO OSINT SÊNIOR especializado em geolocalização por imagem.

Objetivo: identificar a LOCALIZAÇÃO MAIS PROVÁVEL da imagem.

Regras:
1. Analise arquitetura, vegetação, placas, clima, relevo, sombras e tráfego.
2. Compare países e regiões semelhantes.
3. Evite respostas genéricas. Seja específico.
4. Se houver incerteza, declare explicitamente.

Apresente obrigatoriamente:
- Local mais provável (país + região)
- Até 2 hipóteses alternativas
- Evidências técnicas observáveis
- Nível de confiança (%)

Formato:
## Local mais provável
## Hipóteses alternativas
## Evidências técnicas
## Nível de confiança
        """

        img = PIL.Image.open(img_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail((1024, 1024), PIL.Image.LANCZOS)

        response = model.generate_content([prompt, img])
        return response.text

    except Exception as e:
        return f"❌ Erro na análise: {str(e)}"


# =========================================================
# AUTH (SUPABASE NATIVO)
# =========================================================

def auth_login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        # Verifica se o e-mail foi confirmado
        if not getattr(res.user, 'email_confirmed_at', None):
            return "not_confirmed"
        return res.user
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid credentials" in error_msg or "user not found" in error_msg:
            return None
        # Qualquer outro erro
        return None

def auth_get_user():
    try:
        res = supabase.auth.get_user()
        return res.user
    except Exception:
        return None

def auth_logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass


# =========================================================
# DADOS DO USUÁRIO
# =========================================================

def get_user_data(email):
    """Busca dados de negócio pelo email."""
    try:
        res = supabase.table("users").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


# =========================================================
# CADASTRO SEGURO (SÓ NO AUTH)
# =========================================================

def registar_utilizador(nome, email, senha):
    try:
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {"data": {"name": nome}}
        })
        return True, "Cadastro realizado com sucesso. Verifique seu e-mail e faça login."
    except Exception as e:
        msg_erro = str(e)
        if "User already registered" in msg_erro or "Email rate limit exceeded" in msg_erro:
            return False, "E-mail já cadastrado. Verifique sua caixa de entrada."
        return False, "Erro ao criar conta. Tente outro e-mail."


# =========================================================
# CONTROLE DE CRÉDITOS — POR USER.ID (IMUTÁVEL)
# =========================================================

def consumir_credito(user_id: str):
    """
    Decrementa 1 crédito do usuário pelo ID (UUID).
    Retorna True se bem-sucedido, False caso contrário.
    """
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        res = supabase.table("users").select("credits").eq("id", user_id).execute()
        
        if not res.data:
            return False

        current = res.data[0]["credits"]
        if current <= 0:
            return False

        supabase.table("users").update({"credits": current - 1}).eq("id", user_id).execute()
        return True

    except Exception:
        return False
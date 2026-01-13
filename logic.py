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
# MOTOR DE PERÍCIA OSINT (Atualizado)
# =========================================================
def executar_pericia(img_file, api_key: str) -> str:
    if img_file is None:
        return "❌ Nenhuma imagem foi fornecida para análise."
    
    try:
        genai.configure(api_key=api_key)
        
        # Prompt completo diretamente na função
        prompt = """

Você é um Especialista Sênior em Análise e Interpretação de Imagens, com experiência avançada em:
visão computacional, análise ambiental, geografia visual, leitura de padrões urbanos e rurais, inferência contextual e OSINT visual.

Sua função não é adivinhar, mas inferir probabilidades com base em evidências visuais observáveis, explicando claramente o raciocínio utilizado.

Objetivo da Análise

Analise a imagem fornecida de forma técnica, cuidadosa e estruturada, identificando pistas visuais relevantes que permitam inferir características do ambiente e possíveis localizações geográficas, sempre de forma probabilística.

Diretrizes Obrigatórias:

Não faça afirmações categóricas ou absolutas
Não assuma informações que não estejam visivelmente sustentadas
Diferencie claramente observação, inferência e hipótese
Utilize linguagem técnica clara, acessível e objetiva
Quando houver incerteza, declare explicitamente
Não cite leis, normas ou autoridades externas
Não inclua julgamentos morais ou opiniões pessoais

Aspectos que DEVEM ser analisados (quando visíveis):

Tipo de ambiente:

Urbano, rural, periurbano, natural, industrial
Características ambientais
Vegetação (densidade, tipo aparente, padrão)
Solo (cor, textura aparente, umidade)
Relevo (plano, ondulado, montanhoso)
Clima sugerido (árido, tropical, temperado, úmido)

Etnias das pessoas e seu contexto na geolocalização

Elementos construídos:

Arquitetura predominante
Materiais aparentes
Infraestrutura (fiação, pavimentação, sinalização)
Pistas culturais ou regionais
Estilo construtivo
Organização urbana ou rural
Elementos que indiquem região do mundo (sem afirmar país específico, salvo alta confiança)

Consistência visual:

Harmonia ou discrepância entre os elementos
Possíveis indícios de edição ou manipulação (se aplicável)
Estrutura OBRIGATÓRIA do Relatório de Saída

1. Observações Visuais Objetivas
Descreva apenas o que é diretamente visível na imagem, sem interpretação.

2. Análise Interpretativa
Explique o que os elementos observados sugerem em termos de ambiente, região e contexto, sempre justificando cada inferência.

3. Inferência Geográfica Probabilística:

Indique possíveis regiões ou zonas geográficas compatíveis com os padrões observados, utilizando termos como:
baixa probabilidade
média probabilidade
alta probabilidade

4. Fatores de Incerteza
Liste claramente os elementos que limitam a precisão da análise (ângulo da imagem, resolução, ausência de referências, etc.).

5. Conclusão Técnica
Apresente uma síntese clara, objetiva e prudente, reforçando que se trata de uma inferência baseada em padrões visuais, não de confirmação factual.

6. Possíveis Países/Estados/cidades/Região.

liste 4 possibilidades de localização obdecendo a ordem do mais provavel ao menos provavel.


7.Tom e Linguagem
Técnico, claro e profissional
Sem sensacionalismo
Sem promessas de precisão absoluta
Adequado para relatórios de inteligência visual
"""
        
        # Lista modelos disponíveis (nomes SEM "models/" prefixo)
        modelos_disponiveis = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        preferidos = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]

        # Encontra o primeiro modelo disponível na lista de preferidos
        modelo_escolhido = next(
            (m for m in preferidos if m in modelos_disponiveis),
            modelos_disponiveis[0] if modelos_disponiveis else "gemini-pro"
        )

        print(f"🔍 Modelo selecionado: {modelo_escolhido}")  # Debug útil

        model = genai.GenerativeModel(model_name=modelo_escolhido)

        img = PIL.Image.open(img_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Redimensiona apenas se necessário (mantém proporção e mais pixels)
        max_pixels = 3500000  # Limite do Gemini
        current_pixels = img.width * img.height
        if current_pixels > max_pixels:
            ratio = (max_pixels / current_pixels) ** 0.5
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), PIL.Image.LANCZOS)

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
    except Exception:
        # Qualquer erro de autenticação retorna None
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
    # Validação básica de formato de e-mail
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Email inválido"
    
    try:
        # Tenta fazer login para verificar se usuário existe e está confirmado
        try:
            login_result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha  # Usa a senha que o usuário está tentando cadastrar
            })
            # Se login funcionou, significa que usuário já existe e está confirmado
            supabase.auth.sign_out()  # Desloga imediatamente
            return False, "Esse email já possui conta, por favor faça login"
        except Exception:
            # Login falhou - pode ser senha errada ou usuário não existe
            pass
        
        # Tenta cadastrar
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {"data": {"name": nome}}
        })
        
        return True, "Cadastro realizado com sucesso. Verifique seu e-mail e faça login."
        
    except Exception as e:
        msg_erro = str(e)
        if "Email rate limit exceeded" in msg_erro:
            return False, "Limite diário de e-mails atingido. Tente amanhã."
        elif "invalid email format" in msg_erro.lower():
            return False, "Email inválido. Verifique o email e tente novamente"
        elif "User already registered" in msg_erro or "user already exists" in msg_erro.lower():
            return False, "Esse email já possui conta, por favor faça login"
        else:
            return False, "Erro ao criar conta. Tente novamente."

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
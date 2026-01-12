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

Você é um PERITO OSINT SÊNIOR ESPECIALISTA de experiência em geolocalização forense por imagem. Sua especialidade é extrair evidências técnicas de qualquer imagem, mesmo as mais desafiadoras.

## 🔍 OBJETIVO PRINCIPAL
Identificar a LOCALIZAÇÃO GEOGRÁFICA MAIS PROVÁVEL com precisão máxima, usando TODAS as pistas disponíveis.

## 📋 ANÁLISE OBRIGATÓRIA (em ordem de prioridade)

### 1. INFRAESTRUTURA URBANA/RURAL
- Tipo de solo/terreno (asfalto, concreto, terra, grama, areia, pedras)
- Estilo arquitetônico das edificações (colonial, moderno, soviético, islâmico, etc.)
- Materiais de construção predominantes
- Altura média dos prédios
- Presença de infraestrutura específica (postes, fios elétricos, semáforos, placas)

### 2. SINALIZAÇÃO E TEXTOS
- Idioma predominante em placas, outdoors, letreiros
- Alfabeto utilizado (latino, cirílico, árabe, mandarim, etc.)
- Formato de placas de trânsito e veículos
- Números de telefone visíveis (códigos de área)
- Moedas ou preços visíveis

### 3. VEÍCULOS (se presentes)
- Marcas e modelos específicos
- Cores predominantes
- Placas de licenciamento (formato, cores, país)
- Análise de incidência: "Esses veículos são comuns em quais regiões?"
- Probabilidade geográfica baseada na frota local

### 4. POPULAÇÃO (se presente)
- Fenótipo/etnia predominante
- Roupas típicas ou culturais
- Linguagem corporal e comportamento social
- Idade média do grupo
- Acessórios culturais/religiosos visíveis

### 5. VEGETAÇÃO E AMBIENTE
- Tipos de árvores, plantas, flores
- Gramado (natural vs artificial)
- Clima aparente (úmido, seco, tropical, temperado)
- Estação do ano
- Topografia (montanhas, planícies, litoral, desertos)

### 6. INDICADORES TEMPORAIS
- Hora aproximada (baseada na posição e ângulo das sombras)
- Data aproximada (baseada em eventos, roupas sazonais, vegetação)
- Metadados da imagem (se disponíveis): data, hora, coordenadas GPS, modelo da câmera

### 7. ELEMENTOS CULTURAIS
- Bandeiras, símbolos nacionais
- Propaganda/comercial local
- Esportes populares visíveis
- Religião predominante (igrejas, templos, símbolos)
- Nível socioeconômico aparente

## 🎯 METODOLOGIA DE ANÁLISE

1. **ELIMINAÇÃO**: Descarte regiões que não correspondem às características observadas
2. **CORRELAÇÃO**: Combine múltiplas pistas para estreitar possibilidades  
3. **VALIDAÇÃO**: Cruze informações com conhecimento geográfico mundial
4. **PROBABILIDADE**: Atribua níveis de confiança baseados em evidências concretas

## 📝 FORMATO DE RESPOSTA OBRIGATÓRIO

## 🌍 Localização Mais Provável
[Precisão máxima possível: País → Estado/Província → Cidade/Região → Bairro/Área específica]

## 🚗 Análise de Veículos
- [Lista detalhada com marcas, modelos e análise de incidência regional]

## 👥 Análise Demográfica  
- [Etnia/fenótipo predominante e justificativa cultural]

## 🏗️ Infraestrutura e Ambiente
- [Solo, edificações, vegetação, clima]

## ⏰ Indicadores Temporais
- Hora aproximada: [HH:MM]
- Estação/Data aproximada: [Mês/Estação]
- Metadados relevantes: [Se disponíveis]

## 🔍 Hipóteses Alternativas (Top 2)
1. [Segunda localização mais provável com justificativa]
2. [Terceira localização mais provável com justificativa]

## 📊 Nível de Confiança
- [Alto/Médio/Baixo] com justificativa baseada em:
  - Número de pistas independentes
  - Qualidade/resolução da imagem  
  - Consistência entre diferentes elementos

## ⚠️ Limitações da Análise
- [Fatores que reduzem a precisão: baixa resolução, ângulo limitado, etc.]

## 💡 Recomendações para Investigação Adicional
- [Sugestões específicas para confirmar a localização: buscar imagens de satélite, verificar registros de veículos, etc.]

## REGRAS ABSOLUTAS:
- NUNCA invente informações que não estão na imagem
- SEJA específico e técnico, evite generalizações
- QUANTIFIQUE sempre que possível (ex: "80% de confiança")
- ADMITA incertezas explicitamente
- PRIORIZE evidências concretas sobre suposições
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
    try:
        # Tenta cadastrar diretamente
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {"data": {"name": nome}}
        })
        
        # Se chegou aqui, o cadastro foi aceito pelo Supabase
        return True, "Cadastro realizado com sucesso. Verifique seu e-mail e faça login."
        
    except Exception as e:
        msg_erro = str(e)
        
        # Trata erros específicos conhecidos
        if "Email rate limit exceeded" in msg_erro:
            return False, "Limite diário de e-mails atingido. Tente amanhã."
        elif "invalid email format" in msg_erro.lower():
            return False, "Formato de e-mail inválido."
        elif "User already registered" in msg_erro:
            return False, "E-mail já cadastrado. Verifique sua caixa de entrada."
        else:
            # Qualquer outro erro - tenta interpretar
            error_lower = msg_erro.lower()
            if "already registered" in error_lower or "user exists" in error_lower:
                return False, "E-mail já cadastrado. Verifique sua caixa de entrada."
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
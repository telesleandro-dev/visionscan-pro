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

        # =========================================================
        # EXTRAÇÃO DE METADADOS EXIF
        # =========================================================
        exif_info = ""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            def convert_gps_info(gps_info):
                """Converte coordenadas GPS do formato EXIF para graus decimais"""
                def _convert_to_degrees(value):
                    d = float(value[0])
                    m = float(value[1])
                    s = float(value[2])
                    return d + (m / 60.0) + (s / 3600.0)
                
                if not gps_info:
                    return None
                
                gps_latitude = gps_info.get(GPSTAGS.get("GPSLatitude"))
                gps_latitude_ref = gps_info.get(GPSTAGS.get("GPSLatitudeRef"))
                gps_longitude = gps_info.get(GPSTAGS.get("GPSLongitude"))
                gps_longitude_ref = gps_info.get(GPSTAGS.get("GPSLongitudeRef"))
                
                if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                    lat = _convert_to_degrees(gps_latitude)
                    if gps_latitude_ref != "N":
                        lat = -lat
                    
                    lon = _convert_to_degrees(gps_longitude)
                    if gps_longitude_ref != "E":
                        lon = -lon
                    
                    return f"{lat:.6f}, {lon:.6f}"
                return None
            
            # Resetar e abrir imagem
            img_file.seek(0)
            img_temp = Image.open(img_file)
            
            # Obter todos os metadados
            exifdata = img_temp.getexif()
            if exifdata:
                exif_dict = {}
                
                # Processar tags principais
                for tag_id, value in exifdata.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    exif_dict[str(tag)] = value
                
                # Processar GPS separadamente
                gps_info = img_temp.getexif().get_ifd(0x8825)  # GPSInfo IFD
                if gps_info:
                    gps_coords = convert_gps_info(gps_info)
                    if gps_coords:
                        exif_dict["GPS Coordinates"] = gps_coords
                
                # Formatar como texto
                exif_info = "\nMETADADOS EXIF ENCONTRADOS:\n"
                for key, value in exif_dict.items():
                    exif_info += f"- {key}: {value}\n"
            else:
                exif_info = "\nNenhum metadado EXIF encontrado na imagem.\n"
                
        except Exception as exif_error:
            exif_info = f"\nErro ao extrair metadados EXIF: {str(exif_error)}\n"
        
        # Prompt completo diretamente na função
        prompt = f"""

Você é um Analista Sênior em Inteligência Visual e Geolocalização por Imagem, especializado em precisão técnica, rastreabilidade de evidências e inferência baseada em dados objetivos.
Sua função não é gerar respostas genéricas, mas produzir conclusões claras, justificáveis e hierarquizadas, sempre deixando explícita a base de cada decisão.

REGRA FUNDAMENTAL 
{exif_info}
Se a imagem contiver metadados (EXIF), eles devem ser avaliados antes de qualquer inferência visual e tratados como evidência primária.
A inferência visual:

Deve complementar, confirmar ou questionar os metadados
Nunca deve substituí-los sem justificativa técnica clara

🧾 ESTRUTURA OBRIGATÓRIA DO RELATÓRIO

1. CONCLUSÃO TÉCNICA (RESUMO EXECUTIVO)

Apresente imediatamente:

Localização mais provável (cidade, região ou zona geográfica compatível)

Fonte principal da inferência:
Metadados
Análise visual
Cruzamento entre ambos
Grau geral de confiança (em %)
Observação crítica sobre a confiabilidade do resultado (quando aplicável)

⚠️ Esta seção deve ser direta, objetiva e conclusiva.
Nenhuma explicação longa deve aparecer aqui.

2. VERIFICAÇÃO E ANÁLISE DE METADADOS

Informe explicitamente:
Se existem ou não metadados na imagem
Caso existam, liste:
Coordenadas GPS
Data e hora de captura
Dispositivo ou câmera

Avalie:

Consistência interna

Indícios de remoção ou alteração

Classifique os metadados como:

Confiáveis

Parcialmente confiáveis

Inconclusivos

⚠️ Se houver GPS válido e consistente, ele deve ser considerado a base principal da conclusão, salvo forte evidência contrária.

3. OBSERVAÇÕES VISUAIS OBJETIVAS

Descreva somente o que é visível, sem interpretação:

Vegetação

Solo

Construções

Infraestrutura

Relevo

Clima aparente

Elementos culturais ou estruturais visíveis

Nenhuma inferência deve aparecer nesta seção.

4. CRUZAMENTO ENTRE METADADOS E ANÁLISE VISUAL

Avalie se os elementos visuais confirmam ou contradizem os metadados

Aponte convergências e divergências

Caso haja conflito:

Explique qual evidência tem maior peso

Justifique tecnicamente a decisão

5. INFERÊNCIA GEOGRÁFICA COMPLEMENTAR

Somente execute esta etapa se:

Não houver metadados
OU

Os metadados forem inconclusivos
OU

A validação visual for necessária

Indique:

Regiões compatíveis

Classificação de probabilidade:

Alta

Média

Baixa

6. LIMITAÇÕES DA ANÁLISE

Liste objetivamente os fatores que reduzem a precisão:

Resolução da imagem

Ângulo ou enquadramento

Iluminação

Ausência de referências claras

Possível compressão ou edição

⛔ RESTRIÇÕES ABSOLUTAS

Proibido usar linguagem vaga sem justificativa

Proibido pular etapas

Proibido ignorar metadados existentes

Proibido substituir evidência por opinião

Proibido apresentar hipóteses como fatos
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

        # Rebobinar o arquivo para reutilizar na análise visual
        img_file.seek(0)
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
    
# =========================================================
# RECUPERAÇÃO DE SENHA
# =========================================================

def enviar_link_recuperacao(email):
    """Envia link de recuperação de senha via Supabase Auth"""
    try:
        from supabase import create_client
        supabase_local = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
        # Usa método nativo do Supabase
        supabase_local.auth.reset_password_email(email)
        return True, "Link de recuperação enviado para seu e-mail!"
    except Exception as e:
        error_msg = str(e).lower()
        if "user not found" in error_msg:
            return False, "E-mail não encontrado em nossa base."
        else:
            return False, "Erro ao enviar link de recuperação. Tente novamente."
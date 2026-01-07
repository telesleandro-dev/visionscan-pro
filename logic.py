import google.generativeai as genai
import sqlite3
import PIL.Image

# Função para encontrar o modelo disponível e evitar erro 404
def obter_modelo_ia(api_key):
    try:
        genai.configure(api_key=api_key)
        # Lista modelos que suportam geração de conteúdo
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prioridade de modelos estáveis
        for m in ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash", "models/gemini-pro"]:
            if m in models:
                return m
        return models[0] if models else "models/gemini-1.5-flash"
    except Exception:
        return "models/gemini-1.5-flash"

# Lógica principal de perícia
def executar_pericia(img_file, api_key):
    try:
        nome_modelo = obter_modelo_ia(api_key)
        model = genai.GenerativeModel(nome_modelo)
        
        # Abrir e otimizar imagem internamente
        img = PIL.Image.open(img_file)
        img.thumbnail((1024, 1024), PIL.Image.LANCZOS)
        
        prompt = "Atue como perito OSINT. Identifique localização, placas e objetos relevantes."
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"❌ Erro no Processamento: {str(e)}"

# Gestão de usuários
def validar_agente(email, senha):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name, plan FROM users WHERE email=? AND password=?", (email, senha))
    user = c.fetchone()
    conn.close()
    return user
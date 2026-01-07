import google.generativeai as genai
import sqlite3
import PIL.Image

# Configurações de Segurança e IA
def configurar_ia(api_key):
    try:
        genai.configure(api_key=api_key)
        # Busca dinâmica para evitar o erro 404
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Tenta o flash-latest, se não o flash comum, se não o primeiro disponível
        for m in ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash", "models/gemini-pro"]:
            if m in models: return m
        return models[0]
    except:
        return "models/gemini-1.5-flash"

def processar_analise(img, api_key):
    try:
        nome_modelo = configurar_ia(api_key)
        model = genai.GenerativeModel(nome_modelo)
        
        # Redimensionamento para performance no Back-end
        img.thumbnail((1024, 1024), PIL.Image.LANCZOS)
        
        prompt = "Atue como perito OSINT. Analise esta imagem: localize, identifique placas e objetos."
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"❌ Erro na Lógica: {str(e)}"

# Gestão de Dados
def verificar_login(email, senha):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name, plan FROM users WHERE email=? AND password=?", (email, senha))
    user = c.fetchone()
    conn.close()
    return user
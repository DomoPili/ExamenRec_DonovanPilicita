import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar  API KEY
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: No se encontró la GOOGLE_API_KEY en el archivo .env")
else:
    genai.configure(api_key=api_key)
    
    print("🔍 Buscando modelos disponibles para tu API Key...\n")
    try:
        for m in genai.list_models():
            # Solo nos interesan los modelos que sirven para generar contenido (texto)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Nombre válido: {m.name}")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")


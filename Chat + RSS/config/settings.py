import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """
    Configuración centralizada de la aplicación
    """
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Modelos
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    GEMINI_MODEL_NAME = "gemini-2.5-flash"
    
    # Configuración de chunks
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100
    
    # Configuración de búsqueda
    RETRIEVAL_TOP_K = 4  # Número de fragmentos a recuperar
    
    # ChromaDB
    COLLECTION_NAME = "pdf_rag"
    
    # Streamlit
    PAGE_TITLE = "Chat PDF con Gemini"
    PAGE_ICON = "📄"
    
    @classmethod
    def validate(cls):
        """
        Valida que las configuraciones necesarias estén presentes
        """
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY no está configurada en el archivo .env")
        
        return True


# Instancia global de configuración
settings = Settings()


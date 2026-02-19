from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

from config.settings import settings


class EmbeddingService:
    """
    Servicio para generar embeddings (vectores) de texto
    """
    
    def __init__(self):
        """
        Inicializa el modelo de embeddings
        """
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        print(f" Modelo de embeddings cargado: {settings.EMBEDDING_MODEL_NAME}")
    
    def encode_text(self, text: str) -> List[float]:
        """
        Convierte un texto en un vector (embedding)
        
        Args:
            text: Texto a convertir
            
        Returns:
            Lista de números (vector)
        """
        embedding = self.model.encode([text])
        return embedding[0].tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Convierte múltiples textos en vectores (más eficiente)
        
        Args:
            texts: Lista de textos a convertir
            
        Returns:
            Lista de vectores
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula la similitud entre dos embeddings (cosine similarity)
        
        Args:
            embedding1: Primer vector
            embedding2: Segundo vector
            
        Returns:
            Score de similitud (0 a 1, más alto = más similar)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Similitud coseno
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)


##  Explicación rápida:

##- **`__init__()`**: Carga el modelo de embeddings al iniciar
##- **`encode_text()`**: Convierte 1 texto en vector
##- **`encode_batch()`**: Convierte muchos textos de una vez (más rápido)
##- **`calculate_similarity()`**: Calcula qué tan parecidos son dos textos


##¿Por qué necesitamos embeddings?

##Los embeddings convierten palabras en números. Textos similares tienen números similares.

##Ejemplo:
##- "¿Cómo está el clima?" → `[0.2, 0.8, 0.1, ...]`
##- "¿Qué tal el tiempo?" → `[0.3, 0.7, 0.2, ...]` (números parecidos!)
##- "Comprar zapatos" → `[0.9, 0.1, 0.5, ...]` (números diferentes)

##Así la computadora puede "entender" qué textos son similares.



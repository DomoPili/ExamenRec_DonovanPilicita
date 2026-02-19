import chromadb
from typing import List, Optional

from models.document import Document, Chunk, RetrievalResult
from services.embedding_service import EmbeddingService
from config.settings import settings


class DatabaseService:
    """
    Servicio para manejar ChromaDB (base de datos vectorial)
    """
    
    def __init__(self, embedding_service: EmbeddingService):
        """
        Inicializa el cliente de ChromaDB
        """
        self.client = chromadb.Client()
        self.embedding_service = embedding_service
        self.collection = None
        print("Base de datos ChromaDB inicializada")
    
    def create_collection(self, document: Document) -> None:
        """
        Crea una colección en ChromaDB con los chunks del documento
        
        Args:
            document: Documento con sus chunks a almacenar
        """
        # Eliminar colección anterior si existe
        try:
            self.client.delete_collection(settings.COLLECTION_NAME)
            print(f"Colección anterior '{settings.COLLECTION_NAME}' eliminada")
        except:
            pass
        
        # Crear nueva colección
        self.collection = self.client.create_collection(name=settings.COLLECTION_NAME)
        print(f"Nueva colección '{settings.COLLECTION_NAME}' creada")
        
        # Preparar datos
        texts = [chunk.content for chunk in document.chunks]
        chunk_ids = [chunk.id for chunk in document.chunks]
        
        # Generar embeddings
        print(f"Generando embeddings para {len(texts)} chunks...")
        embeddings = self.embedding_service.encode_batch(texts)
        
        # Preparar metadatos
        metadatas = [
            {
                "chunk_index": i,
                "start_index": chunk.start_index,
                "chunk_size": chunk.size
            }
            for i, chunk in enumerate(document.chunks)
        ]
        
        # Agregar a la colección
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=chunk_ids,
            metadatas=metadatas
        )
        
        print(f"Colección creada con {len(texts)} chunks")
    
    def retrieve_context(self, query: str, k: Optional[int] = None) -> RetrievalResult:
        """
        Busca los chunks más relevantes para una pregunta
        
        Args:
            query: Pregunta del usuario
            k: Número de chunks a recuperar (usa settings.RETRIEVAL_TOP_K por defecto)
            
        Returns:
            RetrievalResult con los chunks encontrados
        """
        if self.collection is None:
            raise ValueError("No hay colección creada. Primero procesa un PDF.")
        
        if k is None:
            k = settings.RETRIEVAL_TOP_K
        
        # Generar embedding de la pregunta
        query_embedding = self.embedding_service.encode_text(query)
        
        # Buscar en la colección
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Crear objeto RetrievalResult
        retrieval_result = RetrievalResult(
            chunks=results["documents"][0],
            chunk_ids=results["ids"][0],
            distances=results["distances"][0] if "distances" in results else []
        )
        
        print(f"Recuperados {len(retrieval_result.chunks)} chunks para la pregunta")
        
        return retrieval_result
    
    def get_collection_info(self) -> dict:
        """
        Obtiene información sobre la colección actual
        
        Returns:
            Diccionario con información de la colección
        """
        if self.collection is None:
            return {"exists": False}
        
        count = self.collection.count()
        return {
            "exists": True,
            "name": settings.COLLECTION_NAME,
            "total_chunks": count
        }


## Explicación rápida:

##`create_collection()`**: Guarda todos los chunks del PDF en ChromaDB con sus embeddings
##`retrieve_context()`**: Busca los chunks más parecidos a la pregunta del usuario
##`get_collection_info()`**: Da información sobre lo que está guardado



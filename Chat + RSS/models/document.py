from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chunk:
    """
    Representa un fragmento (pedazo) del documento PDF
    """
    id: str
    content: str
    start_index: int
    size: int
    page_number: Optional[int] = None
    
    def __repr__(self):
        return f"Chunk(id={self.id}, size={self.size}, page={self.page_number})"


@dataclass
class Document:
    """
    Representa un documento PDF completo
    """
    file_name: str
    file_hash: str
    full_text: str
    chunks: List[Chunk]
    total_pages: int
    
    def __repr__(self):
        return f"Document(name={self.file_name}, pages={self.total_pages}, chunks={len(self.chunks)})"
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """
        Busca un chunk por su ID
        """
        for chunk in self.chunks:
            if chunk.id == chunk_id:
                return chunk
        return None
    
    def get_total_chunks(self) -> int:
        """
        Retorna el número total de chunks
        """
        return len(self.chunks)


@dataclass
class ConversationMessage:
    """
    Representa un mensaje en el historial de conversación
    """
    role: str  # "Usuario" o "Asistente"
    content: str
    
    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Message({self.role}: {preview})"


@dataclass
class RetrievalResult:
    """
    Representa el resultado de una búsqueda en la base de datos vectorial
    """
    chunks: List[str]  # Contenido de los chunks encontrados
    chunk_ids: List[str]  # IDs de los chunks
    distances: List[float]  # Distancias/scores de similitud
    
    def get_context_text(self) -> str:
        """
        Une todos los chunks en un solo texto para contexto
        """
        return "\n\n".join(self.chunks)
    
    def __repr__(self):
        return f"RetrievalResult(found={len(self.chunks)} chunks)"


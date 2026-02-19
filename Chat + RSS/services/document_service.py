import hashlib
from typing import List
from models.document import Document, Chunk
from config.settings import settings
from services.extractor_service import ExtractorService 

class DocumentService:
    """
    Servicio unificado para procesar cualquier documento
    """
    def __init__(self):
        self.extractor = ExtractorService()

    @staticmethod
    def hash_file(file) -> str:
        # Crea una huella digital del archivo
        return hashlib.sha256(file.getvalue()).hexdigest()

    def chunk_text(self, text: str) -> List[Chunk]:
        # Divide el texto en pedazos
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            chunk_text = text[start:start + chunk_size]
            chunk = Chunk(
                id=f"chunk_{chunk_id}", 
                content=chunk_text, 
                start_index=start, 
                size=len(chunk_text)
            )
            chunks.append(chunk)
            chunk_id += 1
            start += chunk_size - overlap
        return chunks

    def process_file(self, file, file_name: str) -> Document:
        # Detectar extensión
        extension = file_name.split(".")[-1].lower()
        file_hash = self.hash_file(file)
        
        # Resetear el puntero del archivo tras el hash
        file.seek(0)
        
        # 1. Extraer texto (usando el nuevo servicio)
        full_text = self.extractor.extract_text(file, extension)
        
        # 2. Trocear texto
        chunks = self.chunk_text(full_text)
        
        return Document(
            file_name=file_name,
            file_hash=file_hash,
            full_text=full_text,
            chunks=chunks,
            total_pages=1 
        )

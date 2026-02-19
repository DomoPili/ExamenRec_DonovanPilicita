from .document import Chunk, Document, ConversationMessage, RetrievalResult

__all__ = [
    'Chunk',
    'Document', 
    'ConversationMessage',
    'RetrievalResult'
]



##  ¿Qué acabamos de crear?

#1. **Chunk**: Representa un pedazo del PDF
#2. **Document**: Representa el PDF completo con todos sus chunks
#3. **ConversationMessage**: Un mensaje del chat (pregunta o respuesta)
#4. **RetrievalResult**: Resultado de buscar en la base de datos



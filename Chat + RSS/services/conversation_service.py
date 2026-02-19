from typing import List
from models.document import ConversationMessage


class ConversationService:
    """
    Servicio para manejar el historial de conversación
    """
    
    def __init__(self):
        """
        Inicializa el historial vacío
        """
        self.history: List[ConversationMessage] = []
        print("Servicio de conversación inicializado")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Agrega un mensaje al historial
        
        Args:
            role: "Usuario" o "Asistente"
            content: Contenido del mensaje
        """
        message = ConversationMessage(role=role, content=content)
        self.history.append(message)
    
    def add_user_message(self, content: str) -> None:
        """
        Agrega un mensaje del usuario
        
        Args:
            content: Pregunta o mensaje del usuario
        """
        self.add_message("Usuario", content)
    
    def add_assistant_message(self, content: str) -> None:
        """
        Agrega un mensaje del asistente
        
        Args:
            content: Respuesta del asistente
        """
        self.add_message("Asistente", content)
    
    def get_history(self) -> List[ConversationMessage]:
        """
        Obtiene todo el historial
        
        Returns:
            Lista de mensajes
        """
        return self.history
    
    def clear_history(self) -> None:
        """
        Limpia todo el historial
        """
        self.history = []
        print("Historial limpiado")
    
    def get_last_n_messages(self, n: int) -> List[ConversationMessage]:
        """
        Obtiene los últimos N mensajes
        
        Args:
            n: Número de mensajes a obtener
            
        Returns:
            Lista de los últimos N mensajes
        """
        return self.history[-n:] if len(self.history) >= n else self.history
    
    def get_message_count(self) -> int:
        """
        Obtiene el número total de mensajes en el historial
        
        Returns:
            Cantidad de mensajes
        """
        return len(self.history)
    
    def format_for_display(self) -> List[dict]:
        """
        Formatea el historial para mostrarlo en Streamlit
        
        Returns:
            Lista de diccionarios con role y content
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.history
        ]


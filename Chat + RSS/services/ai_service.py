import google.generativeai as genai
from typing import List

from models.document import ConversationMessage
from config.settings import settings


class AIService:
    """
    Servicio para comunicarse con Gemini (IA de Google)
    """

    def __init__(self):
        """
        Inicializa el cliente de Gemini
        """
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        print(f"Gemini configurado: {settings.GEMINI_MODEL_NAME}")

    def generate_response(
        self, 
        context: str, 
        question: str, 
        history: List[ConversationMessage]
    ) -> str:
        """
        Genera una respuesta usando Gemini basándose en el contexto y el historial
        
        Args:
            context: Fragmentos del PDF relevantes
            question: Pregunta actual del usuario
            history: Historial de conversación
            
        Returns:
            Respuesta generada por Gemini
        """
        # Formatear el historial
        chat_history_formatted = self._format_history(history)
        
        # Crear el prompt
        prompt = self._build_prompt(context, question, chat_history_formatted)
        
        # Generar respuesta
        response = self.model.generate_content(prompt)
        
        return response.text

    def _format_history(self, history: List[ConversationMessage]) -> str:
        """
        Formatea el historial de conversación en texto
        
        Args:
            history: Lista de mensajes
            
        Returns:
            Historial formateado como string
        """
        if not history:
            return "No hay historial previo."
        
        formatted = ""
        for msg in history:
            formatted += f"{msg.role}: {msg.content}\n"
        
        return formatted

    def _build_prompt(self, context: str, question: str, history: str) -> str:
        """
        Construye el prompt completo para Gemini
        
        Args:
            context: Contexto del PDF
            question: Pregunta actual
            history: Historial formateado
            
        Returns:
            Prompt completo
        """
        prompt = f"""
Eres un asistente que responde basándose en el contexto del PDF y en el historial de nuestra charla.
Si la respuesta no está en el contexto, indícalo claramente.

HISTORIAL DE LA CONVERSACIÓN:
{history}

CONTEXTO DEL DOCUMENTO:
{context}

PREGUNTA ACTUAL:
{question}

Instrucciones:
- Responde de forma clara y concisa
- Si la información no está en el contexto, dilo honestamente
- Si hay información en el historial que ayude a responder, úsala
- Mantén un tono amigable y profesional
"""
        return prompt

    def generate_simple_response(self, prompt: str) -> str:
        """
        Genera una respuesta simple sin contexto ni historial
        
        Args:
            prompt: Pregunta o instrucción directa
            
        Returns:
            Respuesta generada
        """
        response = self.model.generate_content(prompt)
        return response.text

    def generate_rss_analysis(self, rss_text: str) -> str:
        """
        Analiza contenido RSS y genera un resumen estructurado
        """
        prompt = f"""
Analiza el siguiente contenido RSS y genera:

1) Un resumen general breve.
2) Los 3 puntos más relevantes encontrados.

Contenido:
{rss_text}

Responde en formato claro y estructurado.
"""
        response = self.model.generate_content(prompt)
        return response.text

import streamlit as st
from config.settings import settings

from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.database_service import DatabaseService
from services.ai_service import AIService
from services.conversation_service import ConversationService
from services.rss_service import RSSService   #  NUEVO


class ChatApp:

    def __init__(self):
        self.document_service = DocumentService()
        self.embedding_service = EmbeddingService()
        self.database_service = DatabaseService(self.embedding_service)
        self.ai_service = AIService()
        self.conversation_service = ConversationService()
        self.rss_service = RSSService()  #  NUEVO

    def initialize_session_state(self):
        if "document" not in st.session_state:
            st.session_state.document = None
        if "file_processed" not in st.session_state:
            st.session_state.file_processed = False
        if "file_hash" not in st.session_state:
            st.session_state.file_hash = None
        if "conversation_service" not in st.session_state:
            st.session_state.conversation_service = self.conversation_service
        if "database_service" not in st.session_state:
            st.session_state.database_service = None

    # -------------------------
    # PROCESAMIENTO DOCUMENTO
    # -------------------------

    def process_document(self, uploaded_file):
        with st.spinner(f"Procesando {uploaded_file.name}..."):
            document = self.document_service.process_file(uploaded_file, uploaded_file.name)

            self.database_service.create_collection(document)

            st.session_state.database_service = self.database_service
            st.session_state.document = document
            st.session_state.file_processed = True
            st.session_state.file_hash = document.file_hash

            st.session_state.conversation_service.clear_history()

        st.success(f"Archivo procesado: {len(document.chunks)} fragmentos generados.")

    def handle_question(self, question: str):
        with st.spinner("Pensando..."):
            db_service = st.session_state.database_service

            if db_service is None:
                st.error("Primero debes procesar un documento.")
                return "", None

            retrieval_result = db_service.retrieve_context(question)
            context_text = retrieval_result.get_context_text()

            history = st.session_state.conversation_service.get_history()

            answer = self.ai_service.generate_response(context_text, question, history)

            st.session_state.conversation_service.add_user_message(question)
            st.session_state.conversation_service.add_assistant_message(answer)

            return answer, retrieval_result

    # -------------------------
    # PROCESAMIENTO RSS
    # -------------------------

    def handle_rss(self, rss_url: str):
        with st.spinner("Analizando RSS..."):
            rss_text = self.rss_service.fetch_and_format(rss_url)

            result = self.ai_service.generate_rss_analysis(rss_text)

            return result

    # -------------------------
    # INTERFAZ
    # -------------------------

    def render_ui(self):

        st.title("Chat Multi-Formato + RSS")

        tab1, tab2 = st.tabs(["📄 Documento", "📰 RSS"])

        # =============================
        # TAB 1 - DOCUMENTOS (RAG)
        # =============================
        with tab1:

            st.markdown("Soporta: **PDF, Excel (.xlsx), Word (.docx), Texto (.txt)**")

            uploaded_file = st.file_uploader(
                "Sube tu archivo",
                type=["pdf", "docx", "xlsx", "txt"]
            )

            if uploaded_file:
                current_hash = self.document_service.hash_file(uploaded_file)

                if st.session_state.file_hash != current_hash:
                    st.session_state.file_hash = current_hash
                    st.session_state.file_processed = False
                    st.session_state.document = None
                    st.session_state.database_service = None
                    st.session_state.conversation_service.clear_history()

            if uploaded_file and not st.session_state.file_processed:
                if st.button("Procesar Archivo"):
                    self.process_document(uploaded_file)

            if st.session_state.file_processed:
                st.divider()
                question = st.chat_input("Pregunta sobre tu documento...")

                if question:
                    with st.chat_message("user"):
                        st.write(question)

                    answer, retrieval_result = self.handle_question(question)

                    if answer:
                        with st.chat_message("assistant"):
                            st.write(answer)

                            with st.expander("Ver contexto utilizado"):
                                for chunk in retrieval_result.chunks:
                                    st.text(chunk)

        # =============================
        # TAB 2 - RSS
        # =============================
        with tab2:

            st.markdown("Ingresa una URL RSS para analizar su contenido.")

            rss_url = st.text_input("URL del RSS")

            if st.button("Analizar RSS"):
                if rss_url:
                    try:
                        result = self.handle_rss(rss_url)
                        st.success("Análisis completado")
                        st.write(result)

                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Debes ingresar una URL válida.")

    def run(self):
        st.set_page_config(page_title=settings.PAGE_TITLE, page_icon="📚")
        self.initialize_session_state()
        self.render_ui()


if __name__ == "__main__":
    app = ChatApp()
    app.run()


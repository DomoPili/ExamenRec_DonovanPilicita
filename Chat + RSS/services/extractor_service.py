import pandas as pd
from docx import Document as DocxReader
from pypdf import PdfReader
import io

class ExtractorService:
    """
    Clase especializada en extraer texto de diferentes formatos.
    """
    @staticmethod
    def extract_text(file, extension: str) -> str:
        if extension == "pdf":
            reader = PdfReader(file)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        
        elif extension == "docx":
            doc = DocxReader(file)
            return "\n".join([para.text for para in doc.paragraphs])
        
        elif extension == "xlsx":
            # Convertimos el Excel a un formato de texto legible (CSV tabulado)
            df_dict = pd.read_excel(file, sheet_name=None)
            full_text = ""
            for sheet_name, df in df_dict.items():
                full_text += f"\n--- Hoja: {sheet_name} ---\n"
                full_text += df.to_csv(index=False, sep="\t")
            return full_text
        
        elif extension == "txt":
            # Leemos el contenido del archivo de texto
            return file.getvalue().decode("utf-8")
        
        return ""


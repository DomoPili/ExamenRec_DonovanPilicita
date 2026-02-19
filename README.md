# Recuperación Desarrollo de Sistemas
# Donovan Pilicita

## Descripción General

Este proyecto integra dos módulos principales:

1. **Scraper**
2. **Chat IA con RAG + RSS**

El sistema permite extraer información mediante scraping y posteriormente analizar contenido utilizando Inteligencia Artificial con embeddings y base de datos vectorial.

---

## Estructura del Proyecto

```
ExamenRec_DonovanPilicita/
│
├── Scraper/
│   ├── scripts de extracción
│   └── lógica de obtención de datos solicitados
│
├── Chat + RSS/
│   ├── config/
│   ├── models/
│   ├── services/
│   ├── main.py
│   └── requirements.txt
│
└── README.md
```

---

## 1️⃣ Módulo Scraper

La carpeta **Scraper/** contiene los scripts encargados de:

- Extraer los datos solicitados.
- Automatizar la navegación cuando es necesario.
- Guardar la información estructurada para su posterior análisis.

Se utiliza automatización y procesamiento de datos según lo requerido en el deber.

---

## 2️⃣ Módulo Chat IA (RAG)

La carpeta **Chat + RSS/** implementa un sistema de análisis basado en IA utilizando la arquitectura **RAG (Retrieval Augmented Generation)**.

### Flujo del sistema:

1. El usuario carga un documento (PDF, DOCX, XLSX o TXT).
2. El sistema:
   - Extrae el texto.
   - Divide el contenido en **chunks**.
   - Genera **embeddings** usando Sentence Transformers.
   - Guarda los vectores en **ChromaDB**.
3. Cuando el usuario realiza una pregunta:
   - Se generan embeddings de la pregunta.
   - Se recuperan los fragmentos más relevantes.
   - Se envían junto con el contexto a **Gemini (Google Generative AI)**.
4. Gemini genera:
   - Resúmenes
   - Respuestas contextualizadas
   - Análisis del contenido

---

## 3️⃣ Módulo RSS

Se agregó un componente adicional que permite:

- Ingresar una URL RSS.
- Extraer el contenido del feed.
- Analizarlo mediante IA.
- Generar:
  - Un resumen general
  - Los 3 puntos más relevantes encontrados

---

## Tecnologías Utilizadas

- Python
- Streamlit
- ChromaDB
- Sentence-Transformers
- Google Generative AI (Gemini)
- Feedparser
- Pandas
- PyPDF
- Python-docx

---

## Ejecución

Instalar dependencias:

```
pip install -r requirements.txt
```

Ejecutar aplicación:

```
streamlit run main.py
```

---

## Autor

Donovan Pilicita

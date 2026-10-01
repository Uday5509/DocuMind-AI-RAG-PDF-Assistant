# DocuMind AI — RAG PDF Assistant

A beginner-friendly Retrieval-Augmented Generation foundation project.

## Current version

- Flask web app
- PDF text extraction with PyMuPDF
- Text chunking
- Sentence Transformer embeddings
- FAISS vector similarity search
- Source page display
- No paid LLM API required for the starter version

## Run

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

http://127.0.0.1:5000

Upload a text-based PDF, click **Index PDF**, then ask questions.

## Next upgrades

1. Connect an LLM provider.
2. Add LangChain.
3. Add multi-PDF collections.
4. Add conversation memory.
5. Add reranking and evaluation.
6. Dockerize and deploy to AWS.

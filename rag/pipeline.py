import os
import pickle
import fitz
import faiss
from sentence_transformers import SentenceTransformer

INDEX_PATH = os.path.join("vectorstore", "index.faiss")
DOCS_PATH = os.path.join("vectorstore", "documents.pkl")

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def extract_pages(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": page_number, "text": text})
    return pages

def chunk_text(text, chunk_size=900, overlap=150):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks

def ingest_pdf(pdf_path):
    pages = extract_pages(pdf_path)
    documents = []
    for item in pages:
        for chunk in chunk_text(item["text"]):
            documents.append({"text": chunk, "page": item["page"], "source": os.path.basename(pdf_path)})

    if not documents:
        raise ValueError("No readable text was found in the PDF.")

    embeddings = get_model().encode(
        [d["text"] for d in documents],
        normalize_embeddings=True,
        show_progress_bar=False
    )
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    os.makedirs("vectorstore", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(documents, f)

    return {"message": f"Indexed {len(documents)} chunks from {os.path.basename(pdf_path)}."}

def retrieve(question, k=4):
    if not os.path.exists(INDEX_PATH) or not os.path.exists(DOCS_PATH):
        raise ValueError("Upload and index a PDF first.")
    index = faiss.read_index(INDEX_PATH)
    with open(DOCS_PATH, "rb") as f:
        documents = pickle.load(f)

    q = get_model().encode([question], normalize_embeddings=True)
    scores, ids = index.search(q, min(k, len(documents)))
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx >= 0:
            item = documents[int(idx)].copy()
            item["score"] = float(score)
            results.append(item)
    return results

def answer_question(question):
    results = retrieve(question)
    context = "\n\n".join(
        f"[Page {r['page']}] {r['text']}" for r in results
    )
    # This starter version provides retrieved context without requiring a paid LLM API.
    answer = (
        "Relevant information found in your document:\n\n"
        + context
        + "\n\n"
        "Note: This starter project performs semantic retrieval. "
        "Connect an LLM provider in rag/llm.py to generate a natural-language answer."
    )
    return {
        "answer": answer,
        "sources": [{"page": r["page"], "score": round(r["score"], 3), "source": r["source"]} for r in results]
    }

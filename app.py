import os
from flask import Flask, render_template, request, jsonify
from rag.pipeline import ingest_pdf, answer_question

app = Flask(__name__)
UPLOAD_DIR = os.path.join("data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/upload")
def upload():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file."}), 400
    path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(path)
    result = ingest_pdf(path)
    return jsonify(result)

@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Enter a question."}), 400
    try:
        return jsonify(answer_question(question))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

if __name__ == "__main__":
    app.run(debug=True)

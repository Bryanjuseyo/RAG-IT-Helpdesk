import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg

from rag.ingest import ingest_folder
from rag.ollama_client import embed, generate
from rag.retrieve import retrieve_similar
from rag.prompt import build_prompt
from flask import request

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set in backend/.env")
    return psycopg.connect(DATABASE_URL)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/db-check")
def db_check():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.execute("SELECT extname FROM pg_extension WHERE extname='vector';")
                has_vector = cur.fetchone() is not None
        return jsonify({"db": "ok", "pgvector_enabled": has_vector})
    except Exception as e:
        return jsonify({"db": "error", "error": str(e)}), 500

@app.post("/api/seed")
def seed():
    count = ingest_folder()
    return {"status": "ok", "chunk_inserted": count}

@app.post("/api/chat")
def chat():
    data = request.json
    question = data.get("question")

    if not question:
        return {"error": "question is required"}, 400

    q_embedding = embed(question)
    contexts = retrieve_similar(q_embedding)

    prompt = build_prompt(question, contexts)
    answer = generate(prompt)

    return {
        "answer": answer,
        "sources": contexts,
    }

@app.get("/api/dbstats")
def dbstats():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM documents;")
            docs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM chunks;")
            chunks = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM chunks WHERE embedding IS NULL;")
            null_embeddings = cur.fetchone()[0]

            cur.execute("SELECT content FROM chunks LIMIT 1;")
            sample = cur.fetchone()
            sample = sample[0] if sample else None

    return {
        "documents": docs,
        "chunks": chunks,
        "null_embeddings": null_embeddings,
        "sample_chunk": sample
    }

if __name__ == "__main__":
    app.run(port=5000, debug=True)
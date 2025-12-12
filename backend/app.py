import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg

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

if __name__ == "__main__":
    app.run(port=5000, debug=True)
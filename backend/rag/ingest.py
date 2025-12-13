from pathlib import Path
from .db import get_conn
from .ollama_client import embed
from psycopg.types.json import Jsonb
from pgvector.psycopg import Vector

SEED_PATH = "../backend/rag/seed_docs"

def chunk_text(text, max_chars=800):
    para = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    buf = ""

    for p in para:
        if len(buf) + len(p) <= max_chars:
            buf += "\n\n" + p
        else:
            chunks.append(buf.strip())
            buf = p

    if buf:
        chunks.append(buf.strip())

    return chunks

def ingest_folder(path=SEED_PATH):
    path = Path(path)
    inserted = 0

    with get_conn() as conn:
        with conn.cursor() as cur:
            for file in path.glob("*.md"):
                content = file.read_text(encoding="utf-8")

                cur.execute(
                    "INSERT INTO documents (title, source) VALUES (%s, %s) RETURNING id",
                    (file.stem, str(file)),
                )

                doc_id = cur.fetchone()[0]

                chunks = chunk_text(content)

                for i, chunk in enumerate(chunks):
                    embedding = embed(chunk)
                    cur.execute(
                        """
                        INSERT INTO chunks
                        (document_id, chunk_index, content, embedding, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (doc_id, i, chunk, Vector(embedding), Jsonb({"source": file.name})),
                    )
                    inserted += 1
        conn.commit()

    return inserted
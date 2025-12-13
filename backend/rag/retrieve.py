from .db import get_conn
from pgvector.psycopg import Vector

def retrieve_similar(query_embedding, limit=5):
    sql = """
    SELECT c.content, c.metadata,
        1 - (c.embedding <-> %s) AS score
    FROM chunks c
    ORDER BY c.embedding <-> %s
    LIMIT %s;
    """



    qv = Vector(query_embedding)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM chunks;")

            cur.execute("SELECT pg_typeof(embedding) FROM chunks LIMIT 1;")

            cur.execute(sql, (qv, qv, limit))
            rows = cur.fetchall()
    return [
        {"content": r[0], "metadata": r[1], "score": float(r[2])}
        for r in rows
        
    ]

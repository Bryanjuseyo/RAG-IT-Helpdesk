CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS chunks;
DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
  id bigserial PRIMARY KEY,
  title text NOT NULL,
  source text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE chunks (
  id bigserial PRIMARY KEY,
  document_id bigint REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index int NOT NULL,
  content text NOT NULL,
  embedding vector(768),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX chunks_document_id_idx ON chunks(document_id);
CREATE INDEX chunks_embedding_idx
  ON chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

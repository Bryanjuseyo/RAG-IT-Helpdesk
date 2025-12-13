import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def embed(text: str, model="nomic-embed-text") -> list[float]:
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": model,
            "prompt": text,   # ✅ FIXED
        },
        timeout=60,
    )
    r.raise_for_status()

    embedding = r.json().get("embedding")
    if not embedding:
        raise RuntimeError("Ollama returned empty embedding")

    return embedding

def generate(prompt: str, model="llama3.1") -> str:
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    r.raise_for_status()

    return r.json()["response"]

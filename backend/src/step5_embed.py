"""
Step 5: Vector Encoding (Embeddings)
---------------------------------------
Turns each chunk's "text" (the question phrasing) into a 384-dimensional
vector using all-MiniLM-L6-v2 (free, runs locally on CPU, no API cost).

IMPORTANT — run this on your own laptop / Colab, not in a locked-down
sandbox: the first run downloads the model (~90 MB) from HuggingFace,
so you need normal internet access just once. After that it's cached
locally and works offline.

Install once:
    pip install sentence-transformers
"""

import json
import numpy as np
from . import config


def embed_chunks(enriched_chunks: list, model_name: str = config.EMBEDDING_MODEL_NAME) -> np.ndarray:
    from sentence_transformers import SentenceTransformer  # imported here so steps 1-4 don't need torch installed

    print(f"[Step 5] Loading embedding model: {model_name} (first run downloads it)")
    model = SentenceTransformer(model_name)

    texts = [c["text"] for c in enriched_chunks]
    print(f"[Step 5] Encoding {len(texts)} texts...")
    vectors = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,   # so cosine similarity == dot product
    )
    print(f"[Step 5] Done. Vector shape: {vectors.shape}")
    return vectors


def load_enriched_chunks(path: str = config.ENRICHED_CHUNKS_PATH) -> list:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def save_embeddings(vectors: np.ndarray, path: str = config.EMBEDDINGS_PATH) -> None:
    np.save(path, vectors)
    print(f"[Step 5] Saved embeddings -> {path}")


if __name__ == "__main__":
    enriched = load_enriched_chunks()
    vectors = embed_chunks(enriched)
    save_embeddings(vectors)

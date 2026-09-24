"""
Step 6: Database Ingestion & Indexing (Qdrant)
--------------------------------------------------
Pushes every (vector, metadata) pair into a Qdrant collection, and gives
you a ready-to-use search() function your teammate's frontend (or your
own generate_response() layer) can call.

Local mode (default): Qdrant runs embedded, storing data on disk in
./qdrant_storage — no server to install or manage, perfect for a
college project and for local dev.

Server mode: point QDRANT_URL at a real Qdrant instance (self-hosted
Docker container or Qdrant Cloud free tier) when you deploy the actual
website. Nothing else in this file changes — just flip config.QDRANT_MODE.
"""

import json
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from . import config


def get_client() -> QdrantClient:
    if config.QDRANT_MODE == "local":
        return QdrantClient(path=config.QDRANT_LOCAL_PATH)
    else:
        return QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)


def create_collection(client: QdrantClient, dim: int = config.EMBEDDING_DIM) -> None:
    client.recreate_collection(
        collection_name=config.COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    print(f"[Step 6] Created collection '{config.COLLECTION_NAME}' (dim={dim}, cosine distance)")


def ingest(client: QdrantClient, enriched_chunks: list, vectors: np.ndarray, batch_size: int = 256) -> None:
    assert len(enriched_chunks) == len(vectors), "chunks and vectors must be the same length and same order"

    total = len(enriched_chunks)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        points = [
            PointStruct(
                id=start + i,
                vector=vectors[start + i].tolist(),
                payload=enriched_chunks[start + i],
            )
            for i in range(end - start)
        ]
        client.upsert(collection_name=config.COLLECTION_NAME, points=points)
        print(f"[Step 6] Ingested {end}/{total}")

    print(f"[Step 6] Done. {total} points indexed in '{config.COLLECTION_NAME}'.")


def search(client: QdrantClient, query_vector, top_k: int = 5, service_id: str = None):
    """
    Search by vector. Optionally filter to a single service_id (useful once
    the conversation already knows which service the customer is asking about).
    Returns the top_k matching payloads, each already containing the
    approved_answer + guardrail your business-rules layer needs.
    """
    query_filter = None
    if service_id:
        query_filter = Filter(
            must=[FieldCondition(key="service_id", match=MatchValue(value=service_id))]
        )

    response = client.query_points(
        collection_name=config.COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=top_k,
    )
    return [{"score": r.score, **r.payload} for r in response.points]


def load_enriched_chunks(path: str = config.ENRICHED_CHUNKS_PATH) -> list:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def load_embeddings(path: str = config.EMBEDDINGS_PATH) -> np.ndarray:
    return np.load(path)


if __name__ == "__main__":
    enriched = load_enriched_chunks()
    vectors = load_embeddings()

    client = get_client()
    create_collection(client, dim=vectors.shape[1])
    ingest(client, enriched, vectors)

    # demo search: reuse the embedding of chunk 0 as a fake "user query"
    # (in real use, embed the incoming customer message with the same model)
    demo_result = search(client, vectors[0].tolist(), top_k=3)
    print("\n[Step 6] Demo search result for a sample query:")
    print(json.dumps(demo_result, indent=2, ensure_ascii=False))

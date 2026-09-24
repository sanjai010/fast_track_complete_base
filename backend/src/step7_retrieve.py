"""
Step 7: Retrieval
----------------------
Turns a live customer message into search results against the Qdrant
collection your Steps 1-6 already built and populated on your machine.

This file is READ-ONLY with respect to Qdrant: it only ever calls
get_client() and search() from step6_ingest_qdrant.py — it never calls
create_collection()/recreate_collection(), so it cannot touch or rebuild
your existing "fasttracks_knowledge" collection.

    customer message -> embed with all-MiniLM-L6-v2 (same model as Step 5)
    -> search Qdrant -> top-k matches, each with a similarity score

Does not read or change config.py beyond config.EMBEDDING_MODEL_NAME and
config.COLLECTION_NAME, both of which already existed for your Step 5/6
runs. Steps 1-6 are untouched.
"""

from . import config
from .step6_ingest_qdrant import get_client, search
from enhancements.query_normalizer import normalize_query
import numpy as np
_model = None  # loaded once per process, reused across calls


def _get_model():
    """Lazy-load so importing this file doesn't require sentence-transformers
    unless you actually call embed_query()."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"[Step 7] Loading embedding model: {config.EMBEDDING_MODEL_NAME}")
        _model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    return _model


def embed_query(text: str) -> np.ndarray:
    model = _get_model()
    normalized_text = normalize_query(text)

    return model.encode(
        normalized_text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )


def retrieve(message: str, top_k: int = 5, service_id: str = None, client=None) -> list:
    """
    Main entry point for Step 7.

    message    - the customer's raw text
    top_k      - how many matches to return
    service_id - optional filter, e.g. "SVC-01", to search within one service only
    client     - reuse an existing QdrantClient if you have one open already;
                otherwise a new read-only connection to the local collection
                    is opened for you.

    Returns a list of dicts, best match first. Each dict is the full stored
    payload (canonical_id, service, intent, approved_answer, risk, guardrail,
    expected_action, category, the original matched question text as "text")
    plus a "score" field (cosine similarity, roughly -1 to 1, higher = closer).
    """
    if client is None:
        client = get_client()

    query_vector = embed_query(message)
    results = search(client, query_vector, top_k=top_k, service_id=service_id)
    return results


def print_results(message: str, results: list) -> None:
    """Pretty-prints retrieval results to the console."""
    print(f"\nQuery: {message!r}")
    print("-" * 70)
    if not results:
        print("  (no results — collection may be empty)")
        return
    for rank, r in enumerate(results, start=1):
        print(f"#{rank}  score={r['score']:.4f}")
        print(f"   canonical_id     : {r.get('canonical_id')}")
        print(f"   service          : {r.get('service')}  (service_id={r.get('service_id')})")
        print(f"   intent           : {r.get('intent')}")
        print(f"   matched question : {r.get('text')}")
        print(f"   approved_answer  : {r.get('approved_answer')}")
        print(f"   risk             : {r.get('risk')}")
        print(f"   guardrail        : {r.get('guardrail')}")
        print(f"   expected_action  : {r.get('expected_action')}")
        print()


if __name__ == "__main__":
    client = get_client()
    demo_message = "How much does ceramic coating cost and how long will it take?"
    results = retrieve(demo_message, top_k=10, client=client)
    print_results(demo_message, results)

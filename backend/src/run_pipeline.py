"""
run_pipeline.py
------------------
Runs Steps 1-6 end to end. This is the file you actually run.

    python -m src.run_pipeline

Splits cleanly at Step 5: everything before it (parsing, cleaning,
chunking, metadata) needs no internet and no heavy libraries. Step 5
needs the embedding model downloaded once. Step 6 needs qdrant-client
(pip install qdrant-client) but no server if you're using local mode.
"""

import time
from . import config
from .step1_parse import load_canonical_knowledge, load_questions, validate
from .step2_clean import clean_canonical, clean_questions
from .step3_chunk import build_chunks
from .step4_metadata import enrich_chunks, save_enriched
from .step5_embed import embed_chunks, save_embeddings
from .step6_ingest_qdrant import get_client, create_collection, ingest, search


def main():
    t0 = time.time()

    # Step 1
    canonical = load_canonical_knowledge()
    questions = load_questions()
    validate(canonical, questions)

    # Step 2
    canonical = clean_canonical(canonical)
    questions = clean_questions(questions)

    # Step 3
    chunks = build_chunks(questions)

    # Step 4
    questions_by_id = {q["id"]: q for q in questions}
    enriched = enrich_chunks(chunks, questions_by_id, canonical)
    save_enriched(enriched)

    # Step 5 (needs internet on first run to fetch the model)
    vectors = embed_chunks(enriched)
    save_embeddings(vectors)

    # Step 6
    client = get_client()
    create_collection(client, dim=vectors.shape[1])
    ingest(client, enriched, vectors)

    print(f"\nPipeline finished in {time.time() - t0:.1f}s")
    print(f"Collection '{config.COLLECTION_NAME}' is ready to query.")

    # quick sanity search
    demo = search(client, vectors[0].tolist(), top_k=3)
    print("\nSample search result:")
    for r in demo:
        print(f"  score={r['score']:.3f}  {r['service']} / {r['intent']} -> {r['approved_answer'][:80]}...")


if __name__ == "__main__":
    main()

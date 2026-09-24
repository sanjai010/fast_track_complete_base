"""
Step 4: Metadata Enriching
-----------------------------
This is the most important step for your business-rules layer later.
Every chunk gets joined with its canonical record so that, at retrieval
time, you get everything the LLM / rules layer needs in one shot —
no second lookup required.

Final payload per chunk (this is exactly what lands in Qdrant in Step 6):

  chunk_id            - e.g. "FT_00001"                (traceability)
  text                - the question text that was embedded
  canonical_id        - e.g. "SVC-01_DISCOVERY"
  service_id          - e.g. "SVC-01"
  service             - e.g. "Luxury Recliners"
  intent              - e.g. "DISCOVERY" / "PRICE" / "BOOKING" ...
  approved_answer     - the ONLY answer text allowed to be shown for this canonical_id
  risk                - "low" / "medium" / "high" / ...
  guardrail           - the rule text the business-rules layer checks against
  expected_action     - e.g. "ANSWER" / "BOOKING_REQUEST" / "ESCALATE_COMPLAINT"
  what_the_user_needs - short description of user intent, useful for logging
  category            - content_type/category from the question dataset (useful for analytics)
  source               - provenance string, useful for debugging bad answers
"""

from . import config
from .step1_parse import load_canonical_knowledge, load_questions, validate
from .step2_clean import clean_canonical, clean_questions
from .step3_chunk import build_chunks
import json


def enrich_chunks(chunks: list, questions_by_id: dict, canonical: dict) -> list:
    enriched = []
    for chunk in chunks:
        q = questions_by_id[chunk["chunk_id"]]
        c = canonical[chunk["canonical_id"]]

        enriched.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "canonical_id": chunk["canonical_id"],
            "service_id": c["service_id"],
            "service": c["service"],
            "intent": c["intent"],
            "approved_answer": c["approved_answer"],
            "risk": c["risk"],
            "guardrail": c["guardrail"],
            "expected_action": c["expected_action"],
            "what_the_user_needs": c.get("what_the_user_needs", ""),
            "category": q.get("category", ""),
            "source": c.get("source", ""),
        })
    print(f"[Step 4] Enriched {len(enriched)} chunks with canonical metadata")
    return enriched


def save_enriched(enriched: list, path: str = config.ENRICHED_CHUNKS_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in enriched:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[Step 4] Saved enriched chunks -> {path}")


if __name__ == "__main__":
    canonical = load_canonical_knowledge()
    questions = load_questions()
    validate(canonical, questions)
    canonical = clean_canonical(canonical)
    questions = clean_questions(questions)
    chunks = build_chunks(questions)

    questions_by_id = {q["id"]: q for q in questions}
    enriched = enrich_chunks(chunks, questions_by_id, canonical)
    save_enriched(enriched)
    print("Sample enriched chunk:")
    print(json.dumps(enriched[0], indent=2, ensure_ascii=False))

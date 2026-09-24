"""
Step 1: Document Parsing & Extraction
--------------------------------------
Your knowledge is already in clean JSON (not a PDF or a website), so
"parsing" here just means: load both files and confirm their shape is
what the rest of the pipeline expects. This is also where you'd plug in
a PDF/HTML parser later if new source documents show up.

Two files:
  1. canonical_knowledge.json -> 427 approved answers (one per canonical_id)
  2. questions.json           -> 10,000 real-world phrasings of those questions,
                                  each one tagged with the canonical_id it maps to
"""

import json
from . import config


def load_canonical_knowledge(path: str = config.CANONICAL_KNOWLEDGE_PATH) -> dict:
    """Returns {canonical_id: record_dict, ...}"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data["records"]
    print(f"[Step 1] Loaded {len(records)} canonical knowledge records from {path}")
    return records


def load_questions(path: str = config.QUESTIONS_PATH) -> list:
    """Returns a list of question-variant dicts."""
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    print(f"[Step 1] Loaded {len(questions)} question variants from {path}")
    return questions


def validate(canonical: dict, questions: list) -> None:
    """Basic sanity checks so a bad file fails loudly, not silently."""
    canon_ids = set(canonical.keys())
    q_ids = set(q["canonical_id"] for q in questions)

    orphan_questions = q_ids - canon_ids
    unused_canonical = canon_ids - q_ids

    if orphan_questions:
        raise ValueError(
            f"[Step 1] {len(orphan_questions)} questions reference a canonical_id "
            f"that doesn't exist in canonical_knowledge.json: {list(orphan_questions)[:5]}..."
        )

    print(f"[Step 1] Validation passed: every question maps to a real canonical_id.")
    if unused_canonical:
        print(f"[Step 1] Note: {len(unused_canonical)} canonical answers have no question "
              f"variant yet (still fine, just won't be reachable via question-matching).")


if __name__ == "__main__":
    canonical = load_canonical_knowledge()
    questions = load_questions()
    validate(canonical, questions)

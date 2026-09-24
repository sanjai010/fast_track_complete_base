"""
Step 2: Document Normalization & Cleaning
-------------------------------------------
Your data is already well-formed (no HTML tags, no page headers/footers,
no OCR noise), so cleaning is light. Still worth doing so you're not
embedding text with stray whitespace, curly-quote mismatches, etc.

What this step does to every text field we plan to embed or show to users:
  - strips leading/trailing whitespace
  - collapses multiple spaces/newlines into one space
  - normalizes unicode (so "—" typed two different ways becomes one form)
"""

import unicodedata
import re
from . import config
from .step1_parse import load_canonical_knowledge, load_questions


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


TEXT_FIELDS_QUESTIONS = ["question", "answer", "follow_up", "customer_reply", "what_the_user_needs"]
TEXT_FIELDS_CANONICAL = ["approved_answer", "what_the_user_needs"]


def clean_questions(questions: list) -> list:
    cleaned = []
    for q in questions:
        q = dict(q)  # don't mutate original
        for field in TEXT_FIELDS_QUESTIONS:
            if field in q:
                q[field] = clean_text(q[field])
        cleaned.append(q)
    print(f"[Step 2] Cleaned text fields on {len(cleaned)} question records")
    return cleaned


def clean_canonical(canonical: dict) -> dict:
    cleaned = {}
    for cid, record in canonical.items():
        record = dict(record)
        for field in TEXT_FIELDS_CANONICAL:
            if field in record:
                record[field] = clean_text(record[field])
        cleaned[cid] = record
    print(f"[Step 2] Cleaned text fields on {len(cleaned)} canonical records")
    return cleaned


if __name__ == "__main__":
    canonical = load_canonical_knowledge()
    questions = load_questions()
    clean_canonical(canonical)
    clean_questions(questions)

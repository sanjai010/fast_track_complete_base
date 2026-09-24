"""
Step 3: Semantic Chunking
---------------------------
Normally this step is hard: you have to decide where to cut a long PDF
so each piece is a complete, self-contained idea. You don't have that
problem, because your data already comes pre-chunked at exactly the
right level:

    1 canonical answer  <->  ~23 real customer phrasings of that question

The design decision this step makes: what is the unit we search over?

  Option A: embed the 427 approved_answer texts.
  Option B: embed the 10,000 question phrasings, each pointing to its
            canonical answer.

We go with B. Reason: a customer's incoming message ("whats luxury
recliners", "do yall do this for a bmw x5") looks like a QUESTION, not
like an ANSWER. Matching question-to-question is far more reliable than
matching question-to-answer, especially with the casual/typo/vehicle-
specific phrasings you deliberately built into the 10k dataset. This is
the standard pattern for FAQ-style RAG: index the question, serve the
answer.

So a "chunk" here = one question variant. Its text is what gets
embedded in Step 5. Everything else about it (the actual answer, risk
level, guardrail, etc.) gets attached in Step 4.
"""

from . import config
from .step1_parse import load_canonical_knowledge, load_questions, validate
from .step2_clean import clean_canonical, clean_questions


def build_chunks(questions: list) -> list:
    """
    Turns each cleaned question record into a minimal chunk:
    just an id and the text that will be embedded.
    Step 4 attaches everything else.
    """
    chunks = []
    for q in questions:
        chunks.append({
            "chunk_id": q["id"],
            "text": q["question"],
            "canonical_id": q["canonical_id"],
        })
    print(f"[Step 3] Built {len(chunks)} chunks (one per question variant)")
    return chunks


if __name__ == "__main__":
    canonical = load_canonical_knowledge()
    questions = load_questions()
    validate(canonical, questions)
    questions = clean_questions(questions)
    chunks = build_chunks(questions)
    print("Sample chunk:", chunks[0])

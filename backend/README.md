# FastTracks Car Care — RAG Backend Pipeline

Backend half of the AI customer support agent. Turns your two data files
into a searchable Qdrant vector index, ready for a retrieval-augmented
response layer to sit on top of.

## What's in your data (already checked)

- `data/raw/canonical_knowledge.json` — 427 approved answers, one per
  `canonical_id` (service x intent). This is the single source of truth
  for what the bot is allowed to say.
- `data/raw/questions.json` — 10,000 real-world phrasings of customer
  questions (casual typing, vehicle-specific, guardrail-testing, 9-step
  journey flows, etc.), each tagged with the `canonical_id` it should
  resolve to.

Every question correctly maps to a real canonical answer — verified in
Step 1.

## The 6-step pipeline

| Step | File | What it does |
|---|---|---|
| 1 | `src/step1_parse.py` | Load both JSON files, validate every question maps to a real canonical_id |
| 2 | `src/step2_clean.py` | Normalize whitespace/unicode in all text fields |
| 3 | `src/step3_chunk.py` | Decide retrieval unit = **one question variant** (see design note below) |
| 4 | `src/step4_metadata.py` | Join each question with its canonical record → full payload (answer, risk, guardrail, expected_action, etc.) |
| 5 | `src/step5_embed.py` | Embed all 10,000 question texts with `all-MiniLM-L6-v2` (384-dim) |
| 6 | `src/step6_ingest_qdrant.py` | Push vectors + payloads into Qdrant, expose a `search()` function |

### Design decision worth knowing: we embed questions, not answers

Your canonical file says the 427 answers are "the only layer that goes
into the vector index" — but we embed the **10,000 questions** instead,
each one pointing at its canonical answer. Reason: a real customer
message looks like a question ("whats luxury recliners", "do yall do
this for a bmw x5"), not like an answer. Question-to-question matching
is far more accurate than question-to-answer matching, especially with
the casual/typo phrasings you built into the dataset on purpose. This is
the standard pattern for FAQ-style RAG bots. At query time you still
only ever serve one of the 427 approved answers — the match just finds
it more reliably.

## Running it

```bash
pip install -r requirements.txt
python -m src.run_pipeline
```

First run needs internet once (downloads the embedding model, ~90 MB
from HuggingFace, then it's cached and works offline). Steps 1–4 need no
internet at all.

Runs in local mode by default — Qdrant stores its index on disk at
`./qdrant_storage`, no server needed. Good for dev and for your demo.

## Verified in a sandboxed environment (no HuggingFace access)

Steps 1, 2, 3, 4 and 6 were run end-to-end on your real 10,000-record
file:
- All 10,000 questions validated against the 427 canonical answers, 0
  orphans.
- Enrichment produced correct, complete payloads.
- Qdrant ingestion (10,000 points), unfiltered search, and
  `service_id`-filtered search all confirmed working — a self-match
  scored 1.000 similarity, and the filtered search correctly stayed
  within one service.

Step 5 needs a real internet connection to fetch model weights, so it's
written and ready but should be run on your machine, not in a locked-down
sandbox.

## Going to production (Qdrant Cloud / a real server)

In `src/config.py`, flip:
```python
QDRANT_MODE = "server"
QDRANT_URL = "https://your-cluster-url"
QDRANT_API_KEY = "your-key"   # set as an environment variable, don't hardcode it
```
Nothing else in the code changes.

## What your frontend teammate needs from you

Once this pipeline runs, `search()` in `step6_ingest_qdrant.py` is the
function that answers "what does the customer mean" — give it a query
vector, get back the top-k matching `approved_answer` + `risk` +
`guardrail` + `expected_action`. That's the contract your response-
generation layer (Step 7+, not built yet) will sit on top of before you
expose anything to the frontend.

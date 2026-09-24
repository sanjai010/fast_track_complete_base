"""
config.py

Central place for all paths and settings.

Change things here instead of hunting through every file.
"""

import os
from dotenv import load_dotenv


# ---- folders ----

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


# ---- load environment variables from .env ----

ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


# ---- API keys ----

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")


# ---- input files (Step 1 reads these) ----

CANONICAL_KNOWLEDGE_PATH = os.path.join(
    RAW_DIR,
    "canonical_knowledge.json"
)

QUESTIONS_PATH = os.path.join(
    RAW_DIR,
    "questions.json"
)


# ---- intermediate output files ----

CLEANED_QUESTIONS_PATH = os.path.join(
    PROCESSED_DIR,
    "step2_cleaned_questions.json"
)

CHUNKS_PATH = os.path.join(
    PROCESSED_DIR,
    "step3_chunks.json"
)

ENRICHED_CHUNKS_PATH = os.path.join(
    PROCESSED_DIR,
    "step4_enriched_chunks.jsonl"
)

EMBEDDINGS_PATH = os.path.join(
    PROCESSED_DIR,
    "step5_embeddings.npy"
)


# ---- embedding model (Step 5) ----

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

EMBEDDING_DIM = 384


# ---- Qdrant (Step 6) ----

# Local mode: no server needed, stores on disk in this project folder.

QDRANT_MODE = "local"

QDRANT_LOCAL_PATH = os.path.join(
    BASE_DIR,
    "qdrant_storage"
)

# If you later move to a real Qdrant server / Qdrant Cloud,
# set QDRANT_MODE = "server" and fill these in.

QDRANT_URL = os.environ.get(
    "QDRANT_URL",
    "http://localhost:6333"
)

QDRANT_API_KEY = os.environ.get(
    "QDRANT_API_KEY"
)

COLLECTION_NAME = "fasttracks_knowledge"
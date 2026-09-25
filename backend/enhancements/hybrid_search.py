"""Hybrid retrieval: dense (vector) + BM25 (keyword) merged with RRF.

This layer runs *alongside* the existing Step 7 dense retrieval. It keeps
the original pipeline untouched and adds exact-token matches that pure
vector search often misses (e.g. "ppf", "x5", "recliners", typos).

    customer message
        |
        |-- dense pass -> Qdrant cosine search (top 30)
        |-- bm25 pass -> in-memory BM25 over question texts (top 30)
        |
        V
    RRF merge by chunk_id -> final top-k payloads

The ``score`` field stays the original cosine score so Step 8's confidence
threshold keeps working. A fused ``fused_score`` is attached for ordering.

Failure-safe: any exception falls back to plain dense retrieval, so the
chat endpoint never breaks because of this layer.

Only depends on data that already exists (``step4_enriched_chunks.jsonl``),
so no re-indexing or collection changes are required.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

from src.step6_ingest_qdrant import load_enriched_chunks
from src.step7_retrieve import retrieve

from .query_normalizer import normalize_query


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DENSE_TOP_K = 30
BM25_TOP_K = 30
RRF_K = 60

BM25_K1 = 1.5
BM25_B = 0.75

# Small set of pure function words only. Intent-bearing words such as
# "how", "much", "not", "ppf" are deliberately kept.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "for", "in", "on", "at", "of",
    "to", "is", "are", "was", "were", "be", "been", "am", "it", "its",
    "that", "this", "these", "those", "with", "me", "i", "we", "you",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Normalize chat text and split into lowercase word tokens."""
    normalized = normalize_query(text).lower()
    return [
        token
        for token in _TOKEN_RE.findall(normalized)
        if len(token) >= 2 and token not in STOPWORDS
    ]


# ---------------------------------------------------------------------
# BM25 corpus (loaded lazily once per process)
# ---------------------------------------------------------------------

_corpus = None


def _load_corpus() -> dict:
    """Load and tokenize the enriched chunks once, reused across calls."""
    global _corpus

    if _corpus is None:
        chunks = load_enriched_chunks()

        tokenized = [_tokenize(chunk.get("text") or "") for chunk in chunks]
        doc_lens = [len(tokens) for tokens in tokenized]

        doc_freq: Counter = Counter()
        for tokens in tokenized:
            doc_freq.update(set(tokens))

        _corpus = {
            "chunks": chunks,
            "tokenized": tokenized,
            "doc_lens": doc_lens,
            "doc_freq": dict(doc_freq),
            "num_docs": len(chunks),
            "avgdl": (sum(doc_lens) / len(chunks)) if chunks else 0.0,
        }

    return _corpus


def resettable_reset_corpus() -> None:
    """Drop the cached corpus (used by tests to reload data)."""
    global _corpus
    _corpus = None


# ---------------------------------------------------------------------
# BM25 scoring
# ---------------------------------------------------------------------

def _bm25_scores(query_tokens: list[str], corpus: dict) -> list[float]:
    k1 = BM25_K1
    b = BM25_B
    num_docs = corpus["num_docs"]
    avgdl = corpus["avgdl"] or 1.0

    scores = [0.0] * num_docs

    query_terms = set(query_tokens)

    for idx in range(num_docs):
        tokens = corpus["tokenized"][idx]
        if not tokens:
            continue

        tf_map = Counter(tokens)
        doc_len = corpus["doc_lens"][idx]
        doc_len_norm = 1 - b + b * (doc_len / avgdl)

        total = 0.0
        for term in query_terms:
            tf = tf_map.get(term)
            if not tf:
                continue

            df = corpus["doc_freq"].get(term, 0)
            idf = math.log(1.0 + (num_docs - df + 0.5) / (df + 0.5))
            denominator = tf + k1 * doc_len_norm
            total += idf * (tf * (k1 + 1.0)) / denominator

        scores[idx] = total

    return scores


def bm25_top_indices(query_tokens: list[str], top_k: int = BM25_TOP_K) -> list[int]:
    """Return the indices of the best-matching chunks for the query tokens."""
    if not query_tokens:
        return []

    corpus = _load_corpus()
    scores = _bm25_scores(query_tokens, corpus)

    ranked = sorted(
        range(len(scores)),
        key=lambda idx: scores[idx],
        reverse=True,
    )

    return [idx for idx in ranked if scores[idx] > 0.0][:top_k]


# ---------------------------------------------------------------------
# RRF fusion
# ---------------------------------------------------------------------

def _rrf_merge(ranked_id_lists: list[list[str]], k: int = RRF_K) -> list[tuple[str, float]]:
    """
    Reciprocal Rank Fusion.

    Each ranked list contributes 1 / (k + rank) per item; items in more
    lists (and higher up) accumulate a larger fused score.
    """
    fused: dict[str, float] = defaultdict(float)

    for ranked_ids in ranked_id_lists:
        for rank, chunk_id in enumerate(ranked_ids):
            fused[chunk_id] += 1.0 / (k + rank + 1)

    return sorted(fused.items(), key=lambda item: item[1], reverse=True)


# ---------------------------------------------------------------------
# Hybrid retrieval entry point
# ---------------------------------------------------------------------

def hybrid_retrieve(
    message: str,
    top_k: int = 10,
    client=None,
) -> list[dict]:
    """
    Retrieve the best-matching knowledge payloads for a customer message.

    Combines dense Qdrant search with an in-memory BM25 keyword pass,
    merged by reciprocal rank fusion.

    Returns a list of dicts identical to ``src.step7_retrieve.retrieve``
    (payload + ``score``) but ranked by the fused signal, plus a
    ``fused_score`` key. Falls back to pure dense retrieval on any error.
    """
    try:
        dense_results = retrieve(message, top_k=DENSE_TOP_K, client=client)

        if not dense_results:
            return []

        dense_ids = [r.get("chunk_id") for r in dense_results]

        # Every enriched chunk is expected to carry a chunk_id. If any are
        # missing (old index), do not risk corrupt ordering -> dense only.
        if not dense_ids or len(dense_ids) != len(dense_results):
            return dense_results[:top_k]

        query_tokens = _tokenize(message)
        bm25_indices = bm25_top_indices(query_tokens, top_k=BM25_TOP_K)

        if bm25_indices:
            corpus = _load_corpus()
            bm25_ids = [corpus["chunks"][idx]["chunk_id"] for idx in bm25_indices]
        else:
            bm25_ids = None

        if bm25_ids:
            fused_list = _rrf_merge([dense_ids, bm25_ids])
        else:
            fused_list = _rrf_merge([dense_ids])

        payload_by_id = {r.get("chunk_id"): r for r in dense_results}

        fused_results = []
        for chunk_id, fused_score in fused_list:
            payload = payload_by_id.get(chunk_id)
            if payload is None:
                continue

            result = dict(payload)
            result["fused_score"] = fused_score
            result["score"] = float(payload.get("score", 0.0))
            fused_results.append(result)

            if len(fused_results) >= top_k:
                break

        if fused_results:
            return fused_results

        return dense_results[:top_k]

    except Exception as exc:
        print(
            f"[HYBRID_SEARCH] Hybrid retrieval failed, "
            f"falling back to dense: {type(exc).__name__}: {exc}"
        )
        return retrieve(message, top_k=top_k, client=client)
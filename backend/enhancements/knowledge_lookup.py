"""Deterministic knowledge lookup by service + intent.

Vector retrieval can rank a *related* record first (e.g. COMPATIBILITY
when the customer actually asked for PRICE). When the customer's wording
contains an explicit intent signal ("how much", "discount", "book"), this
module resolves the exact approved record directly from the canonical
knowledge file instead of depending on embedding rank.

Read-only: loads ``canonical_knowledge.json`` once and never writes.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache

from src import config

# Direct lookup is an exact canonical match, not a similarity guess, so it
# carries a confidence well above Step 8's threshold.
LOOKUP_SCORE = 0.95


@lru_cache(maxsize=1)
def _records() -> tuple[dict, ...]:
    with open(config.CANONICAL_KNOWLEDGE_PATH, "r", encoding="utf-8") as source:
        raw = json.load(source)["records"]
    return tuple(raw.values())


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


def find_service_record(service: str, intent: str) -> dict | None:
    """Exact record for a service + intent, e.g. ("PPF", "PRICE")."""

    service_key = _normalise(service)
    intent_key = _normalise(intent).upper()

    if not service_key or not intent_key:
        return None

    for record in _records():
        if (
            _normalise(record.get("service")) == service_key
            and str(record.get("intent") or "").upper() == intent_key
        ):
            return record

    return None


def find_uniform_intent_record(intent: str) -> dict | None:
    """Policy record for an intent that is identical for every service.

    Only returns a record when the knowledge base states the *same*
    approved answer for that intent across all services (e.g. DISCOUNT,
    where every record carries the single approved policy). If the
    answers differ per service this returns None so a service-specific
    answer is never guessed.
    """

    intent_key = _normalise(intent).upper()

    if not intent_key:
        return None

    matches = [
        record
        for record in _records()
        if str(record.get("intent") or "").upper() == intent_key
    ]

    if not matches:
        return None

    answers = {
        _normalise(record.get("approved_answer"))
        for record in matches
        if _normalise(record.get("approved_answer"))
    }

    if len(answers) == 1:
        return matches[0]

    return None


def lookup_by_intent(service: str, intent: str) -> dict | None:
    """Resolve the approved record an explicit intent signal points to."""

    return find_service_record(service, intent) or find_uniform_intent_record(
        intent
    )


def record_as_result(record: dict) -> dict:
    """Shape a canonical record like a Step 7 retrieval result.

    Lets the caller pass the record through the normal
    ``apply_business_rules`` path without special cases.
    """

    return {
        "chunk_id": f"lookup_{record.get('canonical_id')}",
        "canonical_id": record.get("canonical_id"),
        "service_id": record.get("service_id"),
        "service": record.get("service"),
        "intent": str(record.get("intent") or "").upper(),
        "expected_action": record.get("expected_action"),
        "approved_answer": record.get("approved_answer"),
        "approved_answer_variants": record.get("approved_answer_variants", []),
        "guardrail": record.get("guardrail"),
        "score": LOOKUP_SCORE,
        "source": "intent_lookup",
    }

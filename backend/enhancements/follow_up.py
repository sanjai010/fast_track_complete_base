"""Follow-up question resolution.

Gives the bot ChatGPT-style conversation memory: when a customer says
"what about the other one?" or "and the warranty?" the referent is
resolved against the previously discussed topic.

Two tiers, failure-safe:

  Tier 1 (deterministic, always available, zero cost):
      rewrite the retrieval query using the last resolved service
      from conversation memory.

  Tier 2 (LLM rewriter, only when a follow-up is detected):
      one OpenRouter call rephrases the follow-up into a self-contained
      question for better retrieval. Falls back to Tier 1 on any failure.

Nothing here calls Step 9 or the retail response generation - this is
purely about making the *retrieval* understand pronouns and shortcuts.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request

from src import config as src_config


# Same model contract as Step 9.
OPENROUTER_REWRITER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# ---------------------------------------------------------------------
# Follow-up detection
# ---------------------------------------------------------------------

FOLLOW_UP_STARTERS = [
    r"^(?:and|also|then|so|plus|too)\b",
    r"^(?:what|whats|what's|how)\s+about\b",
    r"^(?:what)\s+abt\b",
]

FOLLOW_UP_MENTIONS = [
    r"\bthe\s+other\s+one\b",
    r"\bthe\s+other\b",
    r"\bthat\s+one\b",
    r"\bthis\s+one\b",
    r"\bboth\s+too\b",
    r"\bthat\s+too\b",
    r"\bthis\s+too\b",
    r"\bit\s+also\b",
    r"\bwhat\s+about\s+(?:it|that|this)\b",
    r"\b(?:it|that|this)\s+too\b",
]

# Short pronoun-led questions: "is it waterproof?", "does it work on an x5?"
DEICTIC_SHORT = [
    r"^(?:is|does|can|could|will|would)\s+(?:it|that|this)\b",
]

# Messages longer than this are (almost always) fresh questions, not
# ambiguous follow-ups. Keeps antecedent injection conservative.
MAX_FOLLOW_UP_WORDS = 12


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def is_follow_up(message: str, recent_turn: dict | None) -> bool:
    """
    Whether a message should be treated as a follow-up resolving against
    the most recent resolved turn. Never True without a referent.
    """
    if not message or recent_turn is None:
        return False

    text = message.strip().lower()

    if len(text.split()) > MAX_FOLLOW_UP_WORDS:
        return False

    return (
        _matches_any(text, FOLLOW_UP_STARTERS)
        or _matches_any(text, FOLLOW_UP_MENTIONS)
        or _matches_any(text, DEICTIC_SHORT)
    )


# ---------------------------------------------------------------------
# Tier 1: deterministic antecedent injection
# ---------------------------------------------------------------------

def inject_antecedent(message: str, recent_turn: dict) -> str:
    """
    Rebuild the retrieval query so it is self-contained.

    "what about the other one?" + turn(service=Luxury Recliners)
        -> "Luxury Recliners, what about the other one?"
    """
    service = (recent_turn.get("service") or "").strip()
    message = (message or "").strip()

    if service:
        return f"{service} - {message}"

    return message


# ---------------------------------------------------------------------
# Tier 2: LLM rewrite (failure-safe -> returns None)
# ---------------------------------------------------------------------

def _history_text(history: list[dict]) -> str:
    if not history:
        return ""

    lines = []
    for turn in history[-4:]:
        role = turn.get("role", "")
        content = (turn.get("content") or "").strip()
        if role == "user":
            lines.append(f"Customer: {content}")
        elif role == "assistant":
            lines.append(f"Agent: {content[:200]}")
    return "\n".join(lines)


def rewrite_follow_up(
    message: str,
    history: list[dict],
    recent_turn: dict,
) -> str | None:
    """
    Ask the LLM to rephrase the customer's follow-up as one standalone
    question. Returns None (-> caller falls back to Tier 1) on any
    failure or missing API key.
    """
    if not src_config.OPENROUTER_API_KEY:
        return None

    service = (recent_turn.get("service") or "the previous topic").strip()
    intent = (recent_turn.get("intent") or "").strip()

    history_block = _history_text(history)

    prompt = (
        "You rewrite follow-up messages for a car-care FAQ assistant.\n"
        "Rephrase the customer's follow-up as ONE self-contained question "
        "that stands alone without the history. Keep it under 20 words.\n"
        "Do not add facts, prices, or topics that are not present.\n\n"
        f"Previous topic: {service}"
        + (f" ({intent})" if intent else "")
        + "\n"
        + (f"\nConversation so far:\n{history_block}\n" if history_block else "")
        + f"\nCustomer's follow-up: {message}\n\n"
        "Return ONLY the rewritten question."
    )

    payload = {
        "model": OPENROUTER_REWRITER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {src_config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "FastTracks Car Care AI Assistant",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")

        result = json.loads(raw)

        choices = result.get("choices") or []
        rewritten = (choices[0].get("message") or {}).get("content")

        if rewritten:
            return rewritten.strip()

    except Exception as exc:
        print(
            f"[FOLLOW_UP] Rewriter failed, using deterministic "
            f"antecedent: {type(exc).__name__}: {exc}"
        )

    return None


# ---------------------------------------------------------------------
# Conversation-state note for the response generator
# ---------------------------------------------------------------------

def build_conversation_state(referent: dict) -> str:
    """
    A short, model-safe note describing what the customer is following
    up on, injected into the response prompt alongside the history.
    """
    service = (referent.get("service") or "").strip()
    intent = (referent.get("intent") or "").strip()
    answer = (referent.get("approved_answer") or "").strip()

    parts = ["The customer is following up on"]
    parts.append(
        f"the previously discussed topic" + (f" {service}" if service else "")
        + (f" ({intent.lower()})" if intent else "")
        + "."
    )

    if answer:
        snippet = answer[:180]
        parts.append(f"Previously shared: {snippet}{'...' if len(answer) > 180 else ''}")

    return " ".join(parts)


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

def resolve_follow_up(
    message: str,
    session_id: str | None,
    history: list[dict],
) -> dict | None:
    """
    Try to resolve a message as a follow-up to the last topic.

    Returns None when the message is not a follow-up (or there is no
    referent) - the normal chat flow then runs unchanged.

    Otherwise returns:
        {
            "resolved_query": str,      # self-contained retrieval query
            "referent": dict,           # last resolved turn + thread type
            "rewrite_source": str       # "llm" | "deterministic"
        }
    """
    from .conversation_memory import get_recent_turn, get_thread_type

    recent_turn = get_recent_turn(session_id)

    if not is_follow_up(message, recent_turn):
        return None

    referent = dict(recent_turn)
    referent["thread_type"] = get_thread_type(session_id)

    llm_query = rewrite_follow_up(message, history, recent_turn)

    if llm_query:
        return {
            "resolved_query": llm_query,
            "referent": referent,
            "rewrite_source": "llm",
        }

    return {
        "resolved_query": inject_antecedent(message, recent_turn),
        "referent": referent,
        "rewrite_source": "deterministic",
    }
"""In-memory, per-session conversation memory.

Lets the bot resolve follow-up questions ("what about the other one?",
"and the warranty?", "can I book that too?") against whatever the
customer was previously discussing.

What is stored per session:
  - a rolling list of resolved turns (service, intent, canonical_id,
    the approved answer that was served, retrieval score)
  - an active thread type (ENQUIRY | COMPLAINT | BOOKING) so complaint
    and booking conversations keep their guardrails across turns

Memory is intentionally in-memory: it resets on server restart, which is
fine for this project. A 30-minute TTL prunes stale sessions.
"""

from __future__ import annotations

import time
import uuid


# ---------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------

MEMORY_TTL_SECONDS = 30 * 60
MAX_TURNS_PER_SESSION = 20

THREAD_ENQUIRY = "ENQUIRY"
THREAD_COMPLAINT = "COMPLAINT"
THREAD_BOOKING = "BOOKING"

# decision values that mark a complaint / booking thread
_COMPLAINT_DECISIONS = {
    "ESCALATE_COMPLAINT",
    "COLLECT_COMPLAINT_DETAILS",
}

_BOOKING_DECISIONS = {
    "BOOKING_REQUEST",
    "COLLECT_REQUIRED_DATA",
    "VERIFY_AVAILABILITY",
}


_sessions: dict[str, dict] = {}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def thread_type_for_decision(decision: str) -> str:
    """Map a Step 8 decision to a conversation thread type."""
    decision = (decision or "").upper()

    if decision in _COMPLAINT_DECISIONS:
        return THREAD_COMPLAINT

    if decision in _BOOKING_DECISIONS:
        return THREAD_BOOKING

    return THREAD_ENQUIRY


def _now() -> float:
    return time.time()


def _new_session() -> dict:
    return {
        "turns": [],
        "thread_type": THREAD_ENQUIRY,
        "last_activity": _now(),
    }


def _prune() -> None:
    """Drop sessions that have been idle past the TTL."""
    cutoff = _now() - MEMORY_TTL_SECONDS

    for session_id in list(_sessions):
        session = _sessions.get(session_id)
        if session and session["last_activity"] < cutoff:
            del _sessions[session_id]


def _touch(session_id: str) -> None:
    if session_id in _sessions:
        _sessions[session_id]["last_activity"] = _now()


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def new_session_id() -> str:
    return str(uuid.uuid4())


def record_turn(
    session_id: str,
    *,
    service: str | None,
    intent: str | None,
    canonical_id: str | None,
    approved_answer: str | None,
    score: float = 0.0,
    decision: str | None = None,
    message: str = "",
) -> None:
    """
    Store the resolved outcome of a turn under a session.

    ``decision`` optionally flips the active thread type (complaint /
    booking threads persist their guardrails across turns).
    """
    if not session_id:
        return

    _prune()

    session = _sessions.setdefault(session_id, _new_session())

    if decision:
        session["thread_type"] = thread_type_for_decision(decision)

    session["turns"].append(
        {
            "service": service,
            "intent": intent,
            "canonical_id": canonical_id,
            "approved_answer": approved_answer,
            "score": float(score or 0.0),
            "decision": decision,
            "message": message,
            "timestamp": _now(),
        }
    )

    # Keep only the most recent turns to bound memory.
    if len(session["turns"]) > MAX_TURNS_PER_SESSION:
        session["turns"] = session["turns"][-MAX_TURNS_PER_SESSION:]

    _touch(session_id)


def set_thread_type(session_id: str, thread_type: str) -> None:
    """Force an active thread type (e.g. when a complaint is routed)."""
    if not session_id:
        return

    _prune()

    session = _sessions.setdefault(session_id, _new_session())
    session["thread_type"] = thread_type
    _touch(session_id)


def get_recent_turn(session_id: str) -> dict | None:
    """
    The most recently resolved RAG turn, or None.

    This is what follow-up questions resolve their pronouns against.
    """
    if not session_id:
        return None

    _prune()

    session = _sessions.get(session_id)

    if not session or not session["turns"]:
        return None

    _touch(session_id)
    return session["turns"][-1]


def get_turns(session_id: str) -> list[dict]:
    if not session_id:
        return []

    _prune()

    session = _sessions.get(session_id)
    return list(session["turns"]) if session else []


def get_thread_type(session_id: str) -> str:
    if not session_id:
        return THREAD_ENQUIRY

    _prune()

    session = _sessions.get(session_id)
    return session["thread_type"] if session else THREAD_ENQUIRY


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def reset_memory() -> None:
    """Drop all sessions (used by tests)."""
    _sessions.clear()
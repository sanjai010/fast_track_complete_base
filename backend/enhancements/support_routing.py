"""Small deterministic routes for messages that should not rely on similarity alone.

This module reads the approved canonical knowledge but never writes to it.
It is deliberately separate from ``src`` so the original project remains
unchanged.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache

from src import config


POST_SERVICE_SIGNALS = (
    "after service",
    "after the service",
    "after my service",
    "aftercare",
    "issue",
    "problem",
    "not working",
    "not done properly",
    "not done right",
    "check again",
    "check it again",
    "recheck",
    "re-check",
    "complaint",
    "unhappy",
    "not happy",
    "refund",
)

# Product-failure language. Kept deliberately separate from words like
# "scratch" / "fade" / "crack" that also appear in discovery questions
# ("is it scratch proof?") - wrong matches would force customers into
# the complaint flow.
COMPLAINT_FAILURE_PATTERNS = (
    r"\bpeel(?:ing|ed|s)?\b",
    r"\bbubbl(?:ing|es|ed)?\b",
    r"\bhazing\b",
    r"\bhazy\b",
    r"\bstreakings?\b",
    r"\bswirl\s+marks?\b",
    r"\bfad(?:ing|ed)\b",
    r"\bdull(?:ing|ed)\b",
    r"\bdiscolou?r(?:ation|ing|ed)?\b",
    r"\byellowing\b",
    r"\blifting\b",
    r"\bdelamination\b",
)

SERVICE_ALIASES = {
    "ceramic coating": ("ceramic", "ceramic coating"),
    "paint protection film": ("paint protection film", "ppf"),
    "window tinting": ("window tint", "tinting", "tint"),
    "car detailing": ("car detailing", "detailing", "detail"),
    "car spa": ("car spa", "spa service"),
}


@dataclass(frozen=True)
class SupportRoute:
    """A safe deterministic response chosen before vector retrieval."""

    name: str
    response: str
    decision: str
    canonical_id: str | None = None


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


@lru_cache(maxsize=1)
def _complaint_records() -> tuple[dict, ...]:
    """Load only the existing approved complaint records, read-only."""
    with open(config.CANONICAL_KNOWLEDGE_PATH, "r", encoding="utf-8") as source:
        records = json.load(source)["records"]
    return tuple(
        record
        for record in records.values()
        if record.get("intent") == "COMPLAINT"
    )


def _message_has_post_service_signal(message: str) -> bool:
    normalised = _normalise(message)
    if any(signal in normalised for signal in POST_SERVICE_SIGNALS):
        return True
    return any(
        re.search(pattern, message, re.IGNORECASE)
        for pattern in COMPLAINT_FAILURE_PATTERNS
    )


def _find_service_complaint(message: str) -> dict | None:
    normalised = _normalise(message)
    matches: list[tuple[int, dict]] = []

    for record in _complaint_records():
        service = _normalise(record.get("service", ""))
        aliases = {service, *SERVICE_ALIASES.get(service, ())}
        for alias in aliases:
            # Word boundaries avoid treating a short service name as part of
            # an unrelated word.
            if alias and re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", normalised):
                matches.append((len(alias), record))
                break

    return max(matches, key=lambda item: item[0])[1] if matches else None


def route_post_service_issue(message: str) -> SupportRoute | None:
    """Route post-service complaints without guessing a service.

    A service-specific message uses the existing approved complaint answer.
    A generic message asks for the minimum details required for a human
    follow-up. Neither path asserts fault or promises a repair.
    """
    if not _message_has_post_service_signal(message):
        return None

    record = _find_service_complaint(message)
    if record:
        service = record["service"]
        return SupportRoute(
            name="SERVICE_COMPLAINT",
            decision="ESCALATE_COMPLAINT",
            canonical_id=record["canonical_id"],
            response=(
                f"I understand your concern regarding the {service}. "
                f"{record['approved_answer']} "
                "To help us resolve this promptly, could you please share "
                "your vehicle make and model, the date of service, and a "
                "brief description of the issue? You may also include "
                "photos if available."
            ),
        )

    return SupportRoute(
        name="GENERAL_POST_SERVICE_ISSUE",
        decision="COLLECT_COMPLAINT_DETAILS",
        response=(
            "I'm sorry to hear you're experiencing an issue after your "
            "service. Our team takes post-service concerns very seriously, "
            "and I'd like to help get this resolved for you.\n\n"
            "Could you please share:\n"
            "• The FastTracks service you received\n"
            "• Your vehicle make and model\n"
            "• The date of service\n"
            "• A brief description of the issue\n\n"
            "Photos can be included if available, and our team will "
            "review the details promptly."
        ),
    )


def helpful_unknown_response() -> str:
    """Useful, truthful fallback for genuinely unsupported questions."""
    return (
        "I want to make sure I give you accurate information. I can best "
        "assist with details about FastTracks services, pricing, bookings, "
        "studio information, and post-service support.\n\n"
        "Could you let me know which of these you need help with? "
        "Alternatively, I can connect you with our team directly for "
        "more specialized assistance."
    )


def suggested_actions(route_name: str) -> list[str]:
    """Stable labels a frontend can render as quick-action buttons."""
    if route_name in {"SERVICE_COMPLAINT", "GENERAL_POST_SERVICE_ISSUE"}:
        return ["Share service details", "Share vehicle details", "Contact the team"]
    return ["Book a service", "Ask about a service", "Check prices", "Post-service support"]

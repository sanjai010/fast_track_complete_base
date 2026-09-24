"""
Basic conversation and out-of-scope routing.

This layer runs BEFORE RAG retrieval.

It handles:
- greetings
- basic conversational questions
- thanks
- goodbye
- "what can you do?"
- clearly out-of-scope questions

Business/service questions are allowed to continue
through the normal RAG pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ConversationDecision:
    route: str
    response: str


# -------------------------------------------------------------------
# Basic conversation patterns
# -------------------------------------------------------------------

GREETING_PATTERNS = [
    r"^\s*(hi|hello|hey|heyy|heyyy)\s*[!.]*\s*$",

    r"^\s*(hi|hello|hey|heyy|heyyy)\s+(there|everyone|bro|dude|man|guys|buddy)\s*[!.]*\s*$",

    r"^\s*(yo|sup|wassup|what's up|whats up)\s*[!.?]*\s*$",

    r"^\s*(yo|sup|wassup|what's up|whats up)\s+(bro|dude|man|guys|buddy)\s*[!.?]*\s*$",

    r"^\s*good\s+morning\s*[!.]*\s*$",
    r"^\s*good\s+afternoon\s*[!.]*\s*$",
    r"^\s*good\s+evening\s*[!.]*\s*$",
]

THANKS_PATTERNS = [
    r"\bthank\s*you\b",
    r"\bthanks\b",
    r"\bthanku\b",
    r"\bthx\b",
]


GOODBYE_PATTERNS = [
    r"^\s*(bye|goodbye|see you|see ya|take care)\s*[!.]*\s*$",
]


CAPABILITY_PATTERNS = [
    r"\bwhat can you do\b",
    r"\bhow can you help\b",
    r"\bwhat do you do\b",
    r"\bwhat are you capable of\b",
    r"\bwhat services can you help\b",
]


IDENTITY_PATTERNS = [
    r"\bwho are you\b",
    r"\bwhat are you\b",
    r"\bare you a bot\b",
    r"\bare you an ai\b",
]


def _matches_any(
    text: str,
    patterns: list[str],
) -> bool:
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )


def route_basic_conversation(
    message: str,
) -> ConversationDecision | None:
    """
    Check whether a message is basic conversation.

    Returns:
        ConversationDecision if handled here.
        None if the message should continue to RAG.
    """

    text = message.strip()

    if not text:
        return None

    # ---------------------------------------------------------------
    # Greetings
    # ---------------------------------------------------------------

    if _matches_any(text, GREETING_PATTERNS):
        return ConversationDecision(
            route="CONVERSATION",
            response=(
                "Welcome to FastTracks! I'm here to help with any questions "
                "about our services, pricing, bookings, or studio details. "
                "What can I assist you with today?"
            ),
        )

    # ---------------------------------------------------------------
    # Thanks
    # ---------------------------------------------------------------

    if _matches_any(text, THANKS_PATTERNS):
        return ConversationDecision(
            route="CONVERSATION",
            response=(
                "Happy to help! If you have any other questions about "
                "our services or need assistance with a booking, feel "
                "free to reach out anytime."
            ),
        )

    # ---------------------------------------------------------------
    # Goodbye
    # ---------------------------------------------------------------

    if _matches_any(text, GOODBYE_PATTERNS):
        return ConversationDecision(
            route="CONVERSATION",
            response=(
                "Thank you for reaching out to FastTracks! Have a great day, "
                "and we look forward to helping you with your car."
            ),
        )

    # ---------------------------------------------------------------
    # What can you do?
    # ---------------------------------------------------------------

    if _matches_any(text, CAPABILITY_PATTERNS):
        return ConversationDecision(
            route="CONVERSATION",
            response=(
                "I'm the FastTracks virtual assistant, and I can help you with:\n\n"
                "• Service information and recommendations\n"
                "• Pricing and availability\n"
                "• Booking appointments\n"
                "• Studio location and details\n"
                "• Post-service support and aftercare\n\n"
                "Just let me know what you need!"
            ),
        )

    # ---------------------------------------------------------------
    # Who are you?
    # ---------------------------------------------------------------

    if _matches_any(text, IDENTITY_PATTERNS):
        return ConversationDecision(
            route="CONVERSATION",
            response=(
                "I'm the FastTracks virtual assistant. I'm here to help "
                "you with information about our car customization and "
                "detailing services, pricing, bookings, and anything "
                "else related to FastTracks."
            ),
        )

    # ---------------------------------------------------------------
    # Not basic conversation.
    #
    # Let the normal RAG pipeline decide whether this is:
    # - a FastTracks question
    # - an uncertain question
    # - an out-of-scope question
    # ---------------------------------------------------------------

    return None
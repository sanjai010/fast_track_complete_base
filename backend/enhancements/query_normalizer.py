"""
Query normalization for customer-style messages.

This runs before embedding and retrieval.

The goal is NOT to rewrite the customer's intent.
It only normalizes common chat abbreviations,
contractions, and obvious informal wording.
"""

from __future__ import annotations

import re


# Common WhatsApp/chat abbreviations.
REPLACEMENTS = {
    r"\bu\b": "you",
    r"\bur\b": "your",
    r"\burs\b": "yours",
    r"\br\b": "are",
    r"\bpls\b": "please",
    r"\bplz\b": "please",
    r"\bthx\b": "thanks",
    r"\bty\b": "thank you",
    r"\bwht\b": "what",
    r"\bwat\b": "what",
    r"\bwhats\b": "what is",
    r"\bwanna\b": "want to",
    r"\bgonna\b": "going to",
    r"\bgotta\b": "got to",
    r"\bcuz\b": "because",
    r"\bcoz\b": "because",
    r"\babt\b": "about",
    r"\binfo\b": "information",
    r"\bsvc\b": "service",
}


def normalize_query(message: str) -> str:
    """
    Normalize common informal customer language.

    This does not attempt to understand the customer's intent.
    It only makes the query more suitable for embedding search.
    """

    text = message.strip().lower()

    # Normalize repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    # Apply safe chat-style replacements.
    for pattern, replacement in REPLACEMENTS.items():
        text = re.sub(
            pattern,
            replacement,
            text,
        )

    # Normalize common punctuation spacing.
    text = re.sub(r"\s+([?.!,])", r"\1", text)

    # Remove excessive repeated punctuation.
    text = re.sub(r"([!?.,])\1+", r"\1", text)

    # Normalize whitespace again after replacements.
    text = re.sub(r"\s+", " ", text).strip()

    return text
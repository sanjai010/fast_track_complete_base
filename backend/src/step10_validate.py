"""
Step 10: Response Validation

Validates the response produced by Step 9 before it reaches
the customer.

This layer is deterministic and does not call another LLM.
"""

import re


FALLBACK_MESSAGE = (
    "I want to make sure I provide you with accurate information. "
    "Let me connect you with our team who can assist you further. "
    "You can reach us directly, or I can have someone follow up with you shortly."
)

# ---------------------------------------------------------
# Overclaim detection.
#
# Catches confident/unverifiable promises that the LLM should
# never make on behalf of the business. Each pattern is verified
# NOT to appear in any approved answer, so a hit is a real
# hallucinated overclaim - not a legitimately approved statement.
# ---------------------------------------------------------

OVERCLAIM_PATTERNS = [
    r"\bguaranteed\b",
    r"\b100\s*%\b",
    r"\bwe\s+guarantee\b",
    r"\bnever\s+(?:fade|fail|dull|peel|scratch|break)\b",
    r"\b(?:best|no\.1|number\s*one)\s+in\b",
    r"\bfade[-\s]?proof\b",
    r"\bscratch[-\s]?proof\b",
]

# Very short responses are usually broken/robotic output.
MIN_RESPONSE_LENGTH = 15

# Very long responses overwhelm the customer and drift off-course.
MAX_RESPONSE_LENGTH = 600


def _contains_overclaim(text: str) -> bool:
    if not text:
        return False
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in OVERCLAIM_PATTERNS
    )


def extract_price_ranges(text: str) -> list[str]:
    """
    Extract simple Indian-currency price/range expressions.

    Examples:
    ₹1,00,000
    ₹1,00,000–₹2,00,000
    """
    if not text:
        return []

    pattern = r"₹\s*[\d,]+(?:\s*[–-]\s*₹?\s*[\d,]+)?"
    return re.findall(pattern, text)


def validate_response(
    generated_response: str,
    business_decision,
) -> tuple[bool, str, str]:
    """
    Validate a Step 9 response.

    Returns:
        (is_valid, final_response, reason)
    """

    approved_answer = business_decision.approved_answer or ""
    response = (generated_response or "").strip()

    # ---------------------------------------------------------
    # 1. Empty response
    # ---------------------------------------------------------
    if not response:
        if approved_answer:
            return (
                False,
                approved_answer,
                "Gemini returned an empty response; used approved answer.",
            )

        return (
            False,
            FALLBACK_MESSAGE,
            "Gemini returned an empty response and no approved answer exists.",
        )

    # ---------------------------------------------------------
    # 2. Non-LLM decisions
    # ---------------------------------------------------------
    if not business_decision.use_llm:
        if approved_answer:
            return (
                True,
                approved_answer,
                "Step 8 required the approved answer directly.",
            )

        return (
            True,
            response,
            "No LLM validation required.",
        )

    # ---------------------------------------------------------
    # 3. Price protection
    # ---------------------------------------------------------
    approved_prices = extract_price_ranges(approved_answer)

    if approved_prices:
        for price in approved_prices:
            if price not in response:
                return (
                    False,
                    approved_answer,
                    f"Required approved price '{price}' was not preserved.",
                )

    # ---------------------------------------------------------
    # 4. Basic unsupported-price protection
    # ---------------------------------------------------------
    generated_prices = extract_price_ranges(response)

    if approved_prices:
        for generated_price in generated_prices:
            if generated_price not in approved_prices:
                return (
                    False,
                    approved_answer,
                    f"Generated response introduced an unapproved price: "
                    f"{generated_price}",
                )

    # ---------------------------------------------------------
    # 5. Length checks
    #
    # Extremely short responses are almost always broken output;
    # extremely long ones overload the customer. Use the approved
    # answer instead when either happens.
    # ---------------------------------------------------------
    response_len = len(response)

    if response_len < MIN_RESPONSE_LENGTH:
        return (
            False,
            approved_answer or FALLBACK_MESSAGE,
            (
                f"Generated response too short "
                f"({response_len} chars); used approved answer."
            ),
        )

    if response_len > MAX_RESPONSE_LENGTH:
        return (
            False,
            approved_answer or FALLBACK_MESSAGE,
            (
                f"Generated response too long "
                f"({response_len} chars); used approved answer."
            ),
        )

    # ---------------------------------------------------------
    # 6. Overclaim guard
    # ---------------------------------------------------------
    if _contains_overclaim(response):
        return (
            False,
            approved_answer or FALLBACK_MESSAGE,
            "Generated response contained an unapproved overclaim; "
            "used approved answer.",
        )

    # ---------------------------------------------------------
    # 7. Final successful validation
    # ---------------------------------------------------------
    return (
        True,
        response,
        "Response passed validation.",
    )


def print_validation(
    is_valid: bool,
    final_response: str,
    reason: str,
) -> None:
    print("\n" + "=" * 70)
    print("STEP 10 RESPONSE VALIDATION")
    print("=" * 70)
    print(f"valid    : {is_valid}")
    print(f"reason   : {reason}")
    print("-" * 70)
    print("FINAL RESPONSE")
    print("-" * 70)
    print(final_response)
    print("=" * 70)
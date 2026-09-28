"""End-to-end user-input battery against the running chat API.

Run from the backend directory, with the server live:

    python -m enhancements.test_user_queries

Each case is a real customer phrasing mapped to the knowledge record it
must resolve to. The suite fails any response that:
  - deflects with the old generic fallback on a knowledge-backed question
  - leaks internal terms (Qdrant, OpenRouter, retrieval, NOT CONFIRMED...)
  - misses the approved facts the case asserts (prices, options, address)
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import uuid

BASE_URL = "http://127.0.0.1:8001/chat"
TIMEOUT_SECONDS = 90

OLD_FALLBACK = "i want to make sure i give you accurate information"

INTERNAL_TERMS = [
    "qdrant",
    "openrouter",
    "retrieval",
    "canonical_id",
    "not confirmed",
    "knowledge base",
    "embedding",
    "step 8",
    "business rules",
    "approved answer",
]

# decision, canonical_id substring, [must contain], [must not contain]
CASES: list[dict] = [
    # -----------------------------------------------------
    # PRICE (the original complaint)
    # -----------------------------------------------------
    {
        "name": "PPF price with vehicle (original complaint)",
        "message": "I have a BMW X5, how much is full body PPF?",
        "decision": ["PRICE_GUARDED"],
        "canonical": "SVC-02_PRICE",
        "contains": ["1,00,000", "2,00,000"],
    },
    {
        "name": "PPF price question first",
        "message": "how much is full body PPF for BMW X5",
        "decision": ["PRICE_GUARDED"],
        "canonical": "SVC-02_PRICE",
        "contains": ["1,00,000", "2,00,000"],
    },
    {
        "name": "Short typo price question",
        "message": "ppf price??",
        "decision": ["PRICE_GUARDED"],
        "canonical": "SVC-02_PRICE",
        "contains": ["1,00,000"],
    },
    {
        "name": "Window tinting price",
        "message": "whats the price of window tinting",
        "decision": ["PRICE_GUARDED"],
        "canonical": "SVC-06_PRICE",
        "contains": ["15,000"],
    },
    {
        "name": "Ceramic coating cost (suggested question)",
        "message": "How much does ceramic coating cost?",
        "decision": ["PRICE_GUARDED"],
        "canonical": "EXT-01_PRICE",
        "contains": ["quote"],
    },
    {
        "name": "Vinyl wrapping price",
        "message": "how much does vinyl wrapping cost",
        "decision": ["PRICE_GUARDED"],
        "canonical": "SVC-07_PRICE",
    },
    {
        "name": "Alloy wheel price",
        "message": "price of alloy wheel upgrades",
        "decision": ["PRICE_GUARDED"],
        "canonical": "SVC-08_PRICE",
    },
    {
        "name": "Deep interior cleaning price",
        "message": "how much for deep interior cleaning",
        "decision": ["PRICE_GUARDED"],
        "canonical": "SVC-11_PRICE",
        "contains": ["5,000"],
    },

    # -----------------------------------------------------
    # DURATION / PROCESS / OPTIONS / FEATURES
    # -----------------------------------------------------
    {
        "name": "PPF duration",
        "message": "how long does full body PPF take",
        "decision": ["ALLOW_LLM", "PRICE_GUARDED"],
        "canonical": "_DURATION",
        "not_contains": ["guaranteed"],
    },
    {
        "name": "Ceramic coating process",
        "message": "how is ceramic coating applied step by step",
        "decision": ["ALLOW_LLM"],
        "canonical": "_PROCESS",
    },
    {
        "name": "PPF options",
        "message": "what PPF options do you have",
        "decision": ["ALLOW_LLM"],
        "canonical": "_OPTIONS",
        "contains": ["Full Body PPF"],
    },
    {
        "name": "Ceramic coating features",
        "message": "what do I get with ceramic coating",
        "decision": ["ALLOW_LLM", "PRICE_GUARDED", "COLLECT_REQUIRED_DATA"],
        "not_contains": ["not confirmed"],
    },

    # -----------------------------------------------------
    # DISCOVERY / STUDIO
    # -----------------------------------------------------
    {
        "name": "What is PPF",
        "message": "what is PPF",
        "decision": ["ALLOW_LLM"],
        "canonical": "SVC-02_DISCOVERY",
        "contains": ["protection"],
    },
    {
        "name": "Service list (broad discovery)",
        "message": "What services do you offer?",
        "decision": ["DISCOVERY"],
        "contains": ["Ceramic Coating", "PPF"],
    },
    {
        "name": "Studio location",
        "message": "where is your studio located",
        "decision": ["ALLOW_LLM"],
        "canonical": "STUDIO_LOCATION",
        "contains": ["Jubilee Hills"],
    },

    # -----------------------------------------------------
    # BOOKING (must route to the appointment flow)
    # -----------------------------------------------------
    {
        "name": "Book an appointment",
        "message": "book an appointment",
        "decision": ["BOOKING_REQUEST"],
        "contains": ["book"],
    },
    {
        "name": "Book a slot tomorrow",
        "message": "I want to book a slot tomorrow",
        "decision": ["BOOKING_REQUEST"],
        "canonical": "_BOOKING",
    },
    {
        "name": "Schedule PPF installation",
        "message": "can I schedule PPF installation this week",
        "decision": ["BOOKING_REQUEST", "VERIFY_AVAILABILITY"],
    },

    # -----------------------------------------------------
    # AVAILABILITY
    # -----------------------------------------------------
    {
        "name": "Weekend slots",
        "message": "do you have any slots this weekend",
        "decision": ["VERIFY_AVAILABILITY"],
        "contains": ["date"],
    },
    {
        "name": "Open today",
        "message": "are you open today",
        "decision": ["VERIFY_AVAILABILITY", "BOOKING_REQUEST"],
    },

    # -----------------------------------------------------
    # COMPATIBILITY (collect vehicle details)
    # -----------------------------------------------------
    {
        "name": "PPF fitment for BMW X5",
        "message": "will PPF fit my BMW X5",
        "decision": ["COLLECT_REQUIRED_DATA"],
        "canonical": "SVC-02_COMPATIBILITY",
        "contains": ["model"],
    },
    {
        "name": "Ambient lighting on Thar",
        "message": "do you do ambient lighting on a Thar",
        "decision": ["COLLECT_REQUIRED_DATA"],
        "contains": ["team"],
    },

    # -----------------------------------------------------
    # LEGAL / SAFETY / WARRANTY / AFTERCARE (team escalation)
    # -----------------------------------------------------
    {
        "name": "Window tinting legality",
        "message": "is window tinting legal in india",
        "decision": ["TEAM_ESCALATION"],
        "canonical": "SVC-06_LEGAL",
        "contains": ["legal"],
    },
    {
        "name": "PPF safety",
        "message": "is PPF safe for my car paint",
        "decision": ["TEAM_ESCALATION"],
        "canonical": "SVC-02_SAFETY",
    },
    {
        "name": "PPF warranty",
        "message": "what warranty does PPF come with",
        "decision": ["TEAM_ESCALATION"],
        "canonical": "SVC-02_WARRANTY",
        "contains": ["warranty"],
    },
    {
        "name": "Ceramic coating warranty",
        "message": "warranty on ceramic coating",
        "decision": ["TEAM_ESCALATION"],
        "canonical": "EXT-01_WARRANTY",
    },
    {
        "name": "PPF aftercare / maintenance",
        "message": "how do I maintain my PPF after installation",
        "decision": ["TEAM_ESCALATION", "COLLECT_REQUIRED_DATA"],
        "canonical": "_AFTERCARE",
    },

    # -----------------------------------------------------
    # PAYMENT
    # -----------------------------------------------------
    {
        "name": "Payment methods",
        "message": "what payment methods do you accept",
        "decision": ["VERIFY_DETAILS"],
        "contains": ["Visa"],
    },
    {
        "name": "UPI acceptance",
        "message": "do you accept UPI",
        "decision": ["VERIFY_DETAILS"],
        "contains": ["UPI"],
    },

    # -----------------------------------------------------
    # DISCOUNT
    # -----------------------------------------------------
    {
        "name": "Ceramic coating discount",
        "message": "do you offer discounts on ceramic coating",
        "decision": ["TEAM_ESCALATION"],
        "canonical": "_DISCOUNT",
        "contains": ["discount"],
    },
    {
        "name": "PPF offers",
        "message": "any offers or discounts on PPF",
        "decision": ["TEAM_ESCALATION"],
        "canonical": "SVC-02_DISCOUNT",
    },

    # -----------------------------------------------------
    # CUSTOM QUOTE
    # -----------------------------------------------------
    {
        "name": "Exact quote for BMW X5 PPF",
        "message": "I need an exact quote for full body PPF on my BMW X5",
        "decision": ["COLLECT_REQUIRED_DATA"],
        "canonical": "SVC-02_CUSTOM_QUOTE",
        "contains": ["quote"],
    },

    # -----------------------------------------------------
    # PREPARATION / REQUEST
    # -----------------------------------------------------
    {
        "name": "Preparation before PPF",
        "message": "what should I do before bringing my car for PPF",
        "decision": ["COLLECT_REQUIRED_DATA"],
        "canonical": "_PREPARATION",
    },
    {
        "name": "Install request",
        "message": "I want to get PPF installed on my car",
        "decision": ["COLLECT_REQUIRED_DATA", "BOOKING_REQUEST"],
    },

    # -----------------------------------------------------
    # COMPLAINTS (must never be answered by the LLM)
    # -----------------------------------------------------
    {
        "name": "Ceramic coating peeling",
        "message": "my ceramic coating is peeling after a week",
        "decision": ["ESCALATE_COMPLAINT"],
        "contains": ["photos"],
    },
    {
        "name": "Generic post-service issue",
        "message": "there is an issue after my service",
        "decision": ["COLLECT_COMPLAINT_DETAILS"],
    },

    # -----------------------------------------------------
    # MULTI-INTENT
    # -----------------------------------------------------
    {
        "name": "Price + duration together",
        "message": "how much and how long for full body PPF",
        "decision": ["MULTI_INTENT", "PRICE_GUARDED"],
        "contains": ["1,00,000"],
    },
    {
        "name": "Discovery + price together",
        "message": "what is PPF and how much does it cost",
        "decision": ["MULTI_INTENT", "PRICE_GUARDED"],
        "contains": ["1,00,000"],
    },

    # -----------------------------------------------------
    # BASIC CONVERSATION
    # -----------------------------------------------------
    {
        "name": "Greeting",
        "message": "hi",
        "decision": ["CONVERSATION"],
    },
    {
        "name": "Thanks",
        "message": "thanks a lot",
        "decision": ["CONVERSATION"],
    },

    # -----------------------------------------------------
    # VEHICLE STATEMENT / UNSUPPORTED (short fallback allowed)
    # -----------------------------------------------------
    {
        "name": "Bare vehicle statement",
        "message": "I have a BMW model car",
        "decision": ["NOT_CONFIRMED", "COLLECT_REQUIRED_DATA", "ALLOW_LLM"],
        "allow_old_fallback": False,
        "contains": ["80190"],
    },
    {
        "name": "Out-of-scope weather question",
        "message": "what is the weather in hyderabad today",
        "allow_fallback": True,
        "not_contains": ["guaranteed"],
    },
]


def call_chat(message: str) -> dict:
    payload = json.dumps(
        {
            "message": message,
            "history": [],
            "session_id": str(uuid.uuid4()),
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        BASE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def check_case(case: dict, result: dict) -> list[str]:
    response = str(result.get("response") or "")
    decision = str(result.get("decision") or "")
    canonical = str(result.get("canonical_id") or "")
    lowered = response.lower()

    errors: list[str] = []

    expected_decisions = case.get("decision")
    allow_fallback = case.get("allow_fallback", False)

    if expected_decisions and decision not in expected_decisions:
        if not (
            allow_fallback and decision in {"NOT_CONFIRMED", "HUMAN_HANDOFF"}
        ):
            errors.append(
                f"decision={decision!r} expected {expected_decisions}"
            )

    if not allow_fallback and not response.strip():
        errors.append("empty response")

    if not case.get("allow_old_fallback", allow_fallback):
        if OLD_FALLBACK in lowered:
            errors.append("old wavery fallback returned")

    expected_canonical = case.get("canonical")
    if expected_canonical and expected_canonical.lower() not in canonical.lower():
        if not (allow_fallback and decision == "NOT_CONFIRMED"):
            errors.append(
                f"canonical={canonical!r} expected *{expected_canonical}*"
            )

    for needle in case.get("contains", []):
        if needle.lower() not in lowered:
            errors.append(f"missing {needle!r}")

    for needle in case.get("not_contains", []):
        if needle.lower() in lowered:
            errors.append(f"must not contain {needle!r}")

    if not case.get("allow_fallback", False):
        for term in INTERNAL_TERMS:
            if term in lowered:
                errors.append(f"internal term leaked: {term!r}")

    return errors


def main() -> int:
    failures = 0

    print("=" * 78)
    print(f"USER INPUT BATTERY - {len(CASES)} cases against {BASE_URL}")
    print("=" * 78)

    for index, case in enumerate(CASES, start=1):
        try:
            result = call_chat(case["message"])
            errors = check_case(case, result)
        except (urllib.error.URLError, OSError) as exc:
            errors = [f"request failed: {exc}"]
            result = {"response": "", "decision": "ERROR"}

        status = "PASS" if not errors else "FAIL"
        if errors:
            failures += 1

        print(
            f"\n[{index:02d}] {status} - {case['name']}"
            f"\n     ask    : {case['message']}"
            f"\n     decision: {result.get('decision')}"
            f" | canonical: {result.get('canonical_id')}"
        )

        if errors:
            for error in errors:
                print(f"     ERROR  : {error}")

        response = str(result.get("response") or "").replace("\n", " ")
        if len(response) > 220:
            response = response[:220] + "..."
        print(f"     reply  : {response}")

    print("\n" + "=" * 78)
    total = len(CASES)
    print(f"RESULT: {total - failures}/{total} passed")
    print("=" * 78)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

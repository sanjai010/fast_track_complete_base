"""
Step 8: Business Rules / Guardrails

Takes the best result from Step 7 retrieval and decides what the
system should do BEFORE any LLM is called.

Step 7 is not modified.

Step 8 does not generate text.

Step 8 only makes a controlled decision.
"""

from dataclasses import dataclass
from typing import Optional


# Provisional value.
# This must be calibrated later using a validation dataset.
CONFIDENCE_THRESHOLD = 0.60


@dataclass
class BusinessDecision:
    decision: str
    final_action: str
    use_llm: bool
    approved_answer: Optional[str]
    approved_answer_variants: list[str]
    reason: str
    score: float
    canonical_id: Optional[str]
    service: Optional[str]
    intent: Optional[str]
    expected_action: Optional[str]


def apply_business_rules(result: Optional[dict]) -> BusinessDecision:
    """
    Apply Step 8 rules to ONE Step 7 retrieval result.

    No LLM is called here.
    """

    # ---------------------------------------------------------
    # Rule 0: No retrieval result
    # ---------------------------------------------------------
    if not result:
        return BusinessDecision(
            decision="NOT_CONFIRMED",
            final_action="HUMAN_HANDOFF",
            use_llm=False,
            approved_answer=None,
            approved_answer_variants=[],
            reason="No retrieval result was found.",
            score=0.0,
            canonical_id=None,
            service=None,
            intent=None,
            expected_action=None,
        )

    score = float(result.get("score", 0.0))
    canonical_id = result.get("canonical_id")
    service = result.get("service")
    intent = str(result.get("intent") or "").upper()
    expected_action = str(result.get("expected_action") or "").upper()
    approved_answer = result.get("approved_answer")
    approved_answer_variants = result.get("approved_answer_variants", [])

    # ---------------------------------------------------------
    # Rule 1: Confidence / unsupported query
    # ---------------------------------------------------------
    if score < CONFIDENCE_THRESHOLD:
        return BusinessDecision(
            decision="NOT_CONFIRMED",
            final_action="HUMAN_HANDOFF",
            use_llm=False,
            approved_answer=None,
            approved_answer_variants=[],
            reason=(
                f"Retrieval score {score:.4f} is below the "
                f"provisional threshold {CONFIDENCE_THRESHOLD:.2f}."
            ),
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 2: Complaint / aftercare
    # ---------------------------------------------------------
    if (
        "COMPLAINT" in intent
        or "COMPLAINT" in expected_action
        or expected_action == "ESCALATE_COMPLAINT"
    ):
        return BusinessDecision(
            decision="ESCALATE_COMPLAINT",
            final_action="ESCALATE_COMPLAINT",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason="Complaint/aftercare case must be escalated.",
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 3: Studio facts
    # ---------------------------------------------------------
    if canonical_id == "STUDIO_LOCATION":
        return BusinessDecision(
            decision="DIRECT_APPROVED_ANSWER",
            final_action="ANSWER",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason="Confirmed studio fact is returned without LLM rewriting.",
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 4: Price
    #
    # Keyed on the intent / action only. The guardrail *text* is
    # deliberately not consulted here because DISCOUNT and other
    # records also carry a "PRICE GUARDRAIL" note while their
    # approved answer is about something else entirely.
    # ---------------------------------------------------------
    if (
        intent == "PRICE"
        or "PRICE" in expected_action
    ):
        return BusinessDecision(
            decision="PRICE_GUARDED",
            final_action="ANSWER_WITH_PRICE_GUARDRAIL",
            use_llm=True,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason=(
                "Price answer may be naturally phrased, but the approved "
                "price/range and price guardrail must be preserved."
            ),
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 4b: Non-complaint escalations (legal, safety,
    # warranty, aftercare, team review).
    #
    # The approved answer is complete and already states that
    # the team confirms the detail, so it is returned directly
    # without letting an LLM add outside knowledge.
    # ---------------------------------------------------------
    if expected_action.startswith("ESCALATE"):
        return BusinessDecision(
            decision="TEAM_ESCALATION",
            final_action="TEAM_ESCALATION",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason=(
                "Escalation topics (legal/safety/warranty/aftercare) "
                "must use the approved answer verbatim."
            ),
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 5: Availability
    # ---------------------------------------------------------
    if (
        intent == "AVAILABILITY"
        or expected_action == "VERIFY_AVAILABILITY"
    ):
        return BusinessDecision(
            decision="VERIFY_AVAILABILITY",
            final_action="VERIFY_AVAILABILITY",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason=(
                "Live availability cannot be assumed. "
                "Use the approved availability response and require "
                "team verification."
            ),
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 6: Booking
    # ---------------------------------------------------------
    if (
        intent == "BOOKING"
        or expected_action == "BOOKING_REQUEST"
    ):
        return BusinessDecision(
            decision="BOOKING_REQUEST",
            final_action="BOOKING_REQUEST",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason="Booking request follows the approved booking flow.",
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 7: Required data collection / enquiry verification
    #
    # Covers composite actions such as
    # "COLLECT_VEHICLE + VERIFY_COMPATIBILITY",
    # "COLLECT_VEHICLE + COLLECT_SCOPE + REQUEST_TEAM_QUOTE"
    # and "ENQUIRY_VERIFY".
    # ---------------------------------------------------------
    if (
        "COLLECT" in expected_action
        or "ENQUIRY" in expected_action
        or "COLLECT" in intent
    ):
        return BusinessDecision(
            decision="COLLECT_REQUIRED_DATA",
            final_action="COLLECT_REQUIRED_DATA",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason="Required customer information must be collected.",
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 7b: Payment verification
    #
    # The approved answer lists exactly which payment methods
    # are confirmed, so it is returned verbatim.
    # ---------------------------------------------------------
    if expected_action.startswith("VERIFY"):
        return BusinessDecision(
            decision="VERIFY_DETAILS",
            final_action="VERIFY_DETAILS",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason=(
                "Payment/verification answers must use the approved "
                "wording so confirmed and unconfirmed terms are not mixed."
            ),
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 7c: Scope split / team review (combination requests)
    # ---------------------------------------------------------
    if "TEAM_REVIEW" in expected_action or "SPLIT_SCOPE" in expected_action:
        return BusinessDecision(
            decision="TEAM_REVIEW",
            final_action="TEAM_REVIEW",
            use_llm=False,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason="Combined-scope requests go through team review.",
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Rule 8: Normal approved answer
    # ---------------------------------------------------------
    if expected_action == "" or "ANSWER" in expected_action:
        return BusinessDecision(
            decision="ALLOW_LLM",
            final_action="GENERATE_RESPONSE",
            use_llm=True,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason="Approved knowledge can be naturally phrased by the LLM.",
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    # ---------------------------------------------------------
    # Safety fallback
    #
    # If retrieval passed the confidence threshold and an approved
    # answer exists, the LLM may rephrase that approved answer.
    # Only a missing approved answer blocks the response.
    # ---------------------------------------------------------
    if approved_answer:
        return BusinessDecision(
            decision="ALLOW_LLM",
            final_action="GENERATE_RESPONSE",
            use_llm=True,
            approved_answer=approved_answer,
            approved_answer_variants=approved_answer_variants,
            reason=(
                f"Unrecognized expected_action {expected_action!r} but an "
                "approved answer exists; LLM may only rephrase it."
            ),
            score=score,
            canonical_id=canonical_id,
            service=service,
            intent=intent,
            expected_action=expected_action,
        )

    return BusinessDecision(
        decision="NOT_CONFIRMED",
        final_action="HUMAN_HANDOFF",
        use_llm=False,
        approved_answer=None,
        approved_answer_variants=[],
        reason=(
            f"No approved answer for expected_action {expected_action!r}. "
            "System will not guess."
        ),
        score=score,
        canonical_id=canonical_id,
        service=service,
        intent=intent,
        expected_action=expected_action,
    )


def print_decision(decision: BusinessDecision) -> None:
    """Display a Step 8 decision clearly."""

    print("\n" + "=" * 70)
    print("STEP 8 BUSINESS DECISION")
    print("=" * 70)

    print(f"retrieval_score : {decision.score:.4f}")
    print(f"canonical_id    : {decision.canonical_id}")
    print(f"service         : {decision.service}")
    print(f"intent          : {decision.intent}")
    print(f"expected_action : {decision.expected_action}")

    print("-" * 70)

    print(f"decision        : {decision.decision}")
    print(f"final_action    : {decision.final_action}")
    print(f"use_llm         : {decision.use_llm}")
    print(f"reason          : {decision.reason}")

    if decision.approved_answer:
        print(f"approved_answer : {decision.approved_answer}")

    if decision.approved_answer_variants:
        print(f"variants count  : {len(decision.approved_answer_variants)}")

    print("=" * 70)
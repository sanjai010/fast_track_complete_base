from src.step8_business_rules import apply_business_rules


def build_multi_intent_decision(
    supported_intents: list[dict],
) -> dict:
    """
    Apply the existing Step 8 business rules independently
    to every supported intent.

    This function does not generate an answer.
    It only collects the business decisions for each intent.
    """

    decisions = []

    for item in supported_intents:
        result = item["result"]

        decision = apply_business_rules(result)

        decisions.append(
            {
                "intent": item["intent"],
                "service": item["service"],
                "score": item["score"],
                "canonical_id": item["canonical_id"],
                "decision": decision,
            }
        )

    return {
        "intent_count": len(decisions),
        "decisions": decisions,
    }


def build_combined_knowledge(
    multi_decision: dict,
) -> list[dict]:
    """
    Collect approved knowledge from every supported intent.

    No new knowledge is generated here.
    """

    knowledge = []

    for item in multi_decision["decisions"]:
        decision = item["decision"]

        if decision.approved_answer:
            knowledge.append(
                {
                    "intent": item["intent"],
                    "service": item["service"],
                    "canonical_id": item["canonical_id"],
                    "approved_answer": decision.approved_answer,
                    "decision": decision.decision,
                    "final_action": decision.final_action,
                    "use_llm": decision.use_llm,
                    "guardrail": getattr(
                        item["decision"],
                        "guardrail",
                        None,
                    ),
                }
            )

    return knowledge
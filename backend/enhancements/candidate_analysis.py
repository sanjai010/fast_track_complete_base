from collections import defaultdict


def analyze_candidates(results: list[dict]) -> dict:
    """
    Analyze Step 7 retrieval candidates.

    This function does not make the final business decision.
    It groups candidates by intent and keeps the strongest
    candidate for each intent.
    """

    grouped = defaultdict(list)

    for result in results:
        intent = str(result.get("intent") or "UNKNOWN").upper()
        grouped[intent].append(result)

    intents = {}

    for intent, candidates in grouped.items():
        candidates.sort(
            key=lambda item: float(item.get("score", 0.0)),
            reverse=True,
        )

        strongest = candidates[0]

        intents[intent] = {
            "score": float(strongest.get("score", 0.0)),
            "canonical_id": strongest.get("canonical_id"),
            "service": strongest.get("service"),
            "expected_action": strongest.get("expected_action"),
            "approved_answer": strongest.get("approved_answer"),
            "result": strongest,
            "candidate_count": len(candidates),
        }

    return {
        "intents": intents,
    }


def inspect_candidates(results: list[dict]) -> None:
    """
    Diagnostic display for Step 7 candidates.
    """

    analysis = analyze_candidates(results)

    print("\n" + "=" * 70)
    print("CANDIDATE ANALYSIS")
    print("=" * 70)

    for intent, data in analysis["intents"].items():
        print(f"\nINTENT: {intent}")
        print(f"  candidates      : {data['candidate_count']}")
        print(f"  strongest score : {data['score']:.4f}")
        print(f"  canonical_id    : {data['canonical_id']}")
        print(f"  service         : {data['service']}")
        print(f"  expected_action : {data['expected_action']}")


def combine_intent_evidence(
    results: list[dict],
    explicit_intents: list[str],
) -> dict:
    """
    Combine explicit wording signals with retrieval evidence.

    An intent is considered supported when it is explicitly
    expressed by the customer AND appears in retrieval results.

    The strongest retrieved candidate is retained with its
    service, score, canonical ID, and expected action.
    """
    analysis = analyze_candidates(results)
    retrieved_intents = analysis["intents"]

    supported_intents = []

    for intent in explicit_intents:
        if intent in retrieved_intents:
            data = retrieved_intents[intent]

            supported_intents.append(
                {
                    "intent": intent,
                    "service": data["service"],
                    "score": data["score"],
                    "canonical_id": data["canonical_id"],
                    "expected_action": data["expected_action"],
                    "result": data["result"],
                }
            )

    return {
        "explicit_intents": explicit_intents,
        "retrieved_intents": retrieved_intents,
        "supported_intents": supported_intents,
    }
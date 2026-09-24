from .intent_signals import detect_intent_signals
from .candidate_analysis import combine_intent_evidence
from .multi_intent_decision import (
    build_multi_intent_decision,
    build_combined_knowledge,
)
from src.step7_retrieve import retrieve


messages = [
    "How much does ceramic coating cost?",
    "How long does ceramic coating take?",
    "How much does ceramic coating cost and how long will it take?",
]


for message in messages:
    print("\n" + "=" * 70)
    print(f"MESSAGE: {message}")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Detect explicit customer intents
    # ---------------------------------------------------------

    signals = detect_intent_signals(message)
    explicit_intents = list(signals.keys())

    print("\nEXPLICIT INTENTS:")
    print(explicit_intents)

    # ---------------------------------------------------------
    # 2. Retrieve candidates
    # ---------------------------------------------------------

    results = retrieve(
        message,
        top_k=10,
    )

    # ---------------------------------------------------------
    # 3. Combine explicit intent + retrieval evidence
    # ---------------------------------------------------------

    combined = combine_intent_evidence(
        results,
        explicit_intents,
    )

    print("\nSUPPORTED INTENTS:")

    for item in combined["supported_intents"]:
        print(
            f"  {item['intent']}: "
            f"service={item['service']}, "
            f"score={item['score']:.4f}, "
            f"canonical_id={item['canonical_id']}, "
            f"expected_action={item['expected_action']}"
        )

    # ---------------------------------------------------------
    # 4. Apply existing Step 8 rules independently
    # ---------------------------------------------------------

    multi_decision = build_multi_intent_decision(
        combined["supported_intents"]
    )

    print("\nBUSINESS DECISIONS:")

    for item in multi_decision["decisions"]:
        decision = item["decision"]

        print(
            f"  {item['intent']}: "
            f"decision={decision.decision}, "
            f"final_action={decision.final_action}, "
            f"use_llm={decision.use_llm}, "
            f"canonical_id={decision.canonical_id}"
        )

    # ---------------------------------------------------------
    # 5. Collect approved knowledge from all intents
    # ---------------------------------------------------------

    combined_knowledge = build_combined_knowledge(
        multi_decision
    )

    print("\nCOMBINED APPROVED KNOWLEDGE:")

    for item in combined_knowledge:
        print(
            f"\n  INTENT: {item['intent']}"
            f"\n  SERVICE: {item['service']}"
            f"\n  CANONICAL ID: {item['canonical_id']}"
            f"\n  DECISION: {item['decision']}"
            f"\n  FINAL ACTION: {item['final_action']}"
            f"\n  APPROVED ANSWER: {item['approved_answer']}"
        )
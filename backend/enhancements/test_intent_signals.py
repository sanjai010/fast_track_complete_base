from .intent_signals import detect_intent_signals
from .candidate_analysis import combine_intent_evidence
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
    # 1. Detect explicit intent signals
    # ---------------------------------------------------------
    signals = detect_intent_signals(message)
    explicit_intents = list(signals.keys())

    print("\nEXPLICIT INTENTS:")
    print(explicit_intents)

    # ---------------------------------------------------------
    # 2. Retrieve real candidates from Qdrant
    # ---------------------------------------------------------
    results = retrieve(
        message,
        top_k=10,
    )

    # ---------------------------------------------------------
    # 3. Combine explicit + retrieval evidence
    # ---------------------------------------------------------
    combined = combine_intent_evidence(
        results,
        explicit_intents,
    )

    print("\nRETRIEVED INTENTS:")

    for intent, data in combined["retrieved_intents"].items():
        print(
            f"  {intent}: "
            f"score={data['score']:.4f}, "
            f"canonical_id={data['canonical_id']}"
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
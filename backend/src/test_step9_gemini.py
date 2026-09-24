from .step7_retrieve import retrieve
from .step8_business_rules import apply_business_rules
from .step9_gemini import generate_response


def main():
    query = "Do you provide PPF?"

    print("=" * 80)
    print("STEP 9 — GEMINI LIVE TEST")
    print("=" * 80)

    print(f"\nCustomer: {query}")

    results = retrieve(query, top_k=3)

    if not results:
        print("\nNo retrieval result.")
        return

    best = results[0]

    decision = apply_business_rules(best)

    print(f"\nStep 7 score: {best.get('score'):.4f}")
    print(f"Canonical ID: {best.get('canonical_id')}")
    print(f"Decision: {decision.decision}")
    print(f"Use Gemini: {decision.use_llm}")

    response = generate_response(query, decision)

    print("\n" + "-" * 80)
    print("FINAL CUSTOMER RESPONSE")
    print("-" * 80)
    print(response)
    print("=" * 80)


if __name__ == "__main__":
    main()
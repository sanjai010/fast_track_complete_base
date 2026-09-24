"""
Step 8 live test.

Uses the REAL Step 7 retrieval system and the existing Qdrant
collection. It does not rebuild or modify Qdrant.
"""

from .step7_retrieve import retrieve
from .step8_business_rules import (
    apply_business_rules,
    print_decision,
)


TEST_QUERIES = [
    "Do you provide PPF?",
    "What is the price of PPF?",
    "Where is your studio?",
    "I have a problem after my service",
    "Can I book a service?",
    "asdfghjkl random unknown question 928374",
]


def run_test(query: str):
    print("\n")
    print("#" * 80)
    print(f"TEST QUERY: {query}")
    print("#" * 80)

    results = retrieve(query, top_k=3)

    if not results:
        print("No retrieval results.")
        return

    best = results[0]

    print("\nSTEP 7 TOP RESULT")
    print("-" * 70)

    print(f"score          : {best.get('score'):.4f}")
    print(f"canonical_id   : {best.get('canonical_id')}")
    print(f"service        : {best.get('service')}")
    print(f"intent         : {best.get('intent')}")
    print(f"expected_action: {best.get('expected_action')}")

    decision = apply_business_rules(best)

    print_decision(decision)


def main():
    print("=" * 80)
    print("STEP 8 — BUSINESS RULES TEST")
    print("=" * 80)

    print(
        "\nIMPORTANT: The confidence threshold is currently "
        "PROVISIONAL = 0.60."
    )

    for query in TEST_QUERIES:
        run_test(query)

    print("\n")
    print("=" * 80)
    print("STEP 8 TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
    
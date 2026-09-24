from .step7_retrieve import retrieve
from .step8_business_rules import apply_business_rules
from .step9_gemini import generate_response
from .step10_validate import validate_response, print_validation


def main():
    queries = [
        "Do you provide PPF?",
        "What is the price of PPF?",
        "I have a problem after my service",
        "Can I book a service?",
        "asdfghjkl random unknown question 928374",
    ]

    print("=" * 80)
    print("STEP 10 — RESPONSE VALIDATION TEST")
    print("=" * 80)

    for query in queries:
        print("\n")
        print("#" * 80)
        print(f"QUERY: {query}")
        print("#" * 80)

        results = retrieve(query, top_k=3)

        if not results:
            print("No retrieval result.")
            continue

        best = results[0]
        decision = apply_business_rules(best)

        generated = generate_response(query, decision)

        is_valid, final_response, reason = validate_response(
            generated,
            decision,
        )

        print_validation(
            is_valid,
            final_response,
            reason,
        )

    print("\nSTEP 10 TEST COMPLETE")


if __name__ == "__main__":
    main()
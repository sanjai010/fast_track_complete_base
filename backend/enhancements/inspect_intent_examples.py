import json
from collections import defaultdict


DATASET_PATH = "data/processed/step4_enriched_chunks.jsonl"


def main():
    grouped = defaultdict(list)

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)

            intent = str(record.get("intent") or "").upper()
            text = record.get("text", "").strip()

            if intent and text:
                grouped[intent].append(text)

    for intent in sorted(grouped):
        print("\n" + "=" * 70)
        print(f"INTENT: {intent}")
        print(f"TOTAL EXAMPLES: {len(grouped[intent])}")
        print("=" * 70)

        # Show only the first 20 examples for inspection.
        for example in grouped[intent][:20]:
            print(f"- {example}")


if __name__ == "__main__":
    main()
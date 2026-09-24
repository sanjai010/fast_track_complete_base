"""
test_step7_retrieval.py
----------------------------
Standalone test for Step 7. Does NOT touch Steps 1-6, does NOT rebuild
the Qdrant collection — it only opens your existing "fasttracks_knowledge"
collection and runs searches against it.

Run from the project root (see the exact command below).
"""

from .step7_retrieve import retrieve, print_results
from .step6_ingest_qdrant import get_client


SAMPLE_QUERIES = [
    "how much does ceramic coating cost",
    "whats luxury recliners",
    "where is the studio located",
    "who do i contact if something went wrong after my service",
    "can i book a slot this week",
]


def run_sample_queries(client):
    print("=" * 70)
    print("Running 5 sample queries against your existing Qdrant collection")
    print("=" * 70)
    for q in SAMPLE_QUERIES:
        results = retrieve(q, top_k=3, client=client)
        print_results(q, results)


def run_interactive(client):
    print("=" * 70)
    print("Type your own queries to test retrieval (empty line to quit)")
    print("=" * 70)
    while True:
        q = input("\nYour query: ").strip()
        if not q:
            print("Done.")
            break
        results = retrieve(q, top_k=3, client=client)
        print_results(q, results)


if __name__ == "__main__":
    client = get_client()  # opens the EXISTING local collection, read-only use here

    count = client.count(collection_name="fasttracks_knowledge")
    print(f"Connected. Collection currently has {count.count} points.\n")

    run_sample_queries(client)
    run_interactive(client)

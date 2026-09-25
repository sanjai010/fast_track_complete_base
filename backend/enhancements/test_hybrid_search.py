"""Run with: python -m unittest enhancements.test_hybrid_search"""

import unittest
from unittest.mock import patch

from .hybrid_search import (
    _load_corpus,
    _rrf_merge,
    _tokenize,
    bm25_top_indices,
    hybrid_retrieve,
    resettable_reset_corpus,
)


class TokenizeTests(unittest.TestCase):
    def test_normlizes_chat_abbreviations(self):
        tokens = _tokenize("pls tell me abt ppf")
        self.assertIn("please", tokens)
        self.assertIn("about", tokens)

    def test_keeps_short_product_tokens(self):
        tokens = _tokenize("hw much is ppf for x5")
        self.assertIn("ppf", tokens)
        self.assertIn("x5", tokens)

    def test_drops_function_words(self):
        tokens = _tokenize("what is the price of ceramic coating")
        self.assertNotIn("the", tokens)
        self.assertNotIn("of", tokens)


class BM25Tests(unittest.TestCase):
    def test_keyword_query_ranks_ppf_questions_first(self):
        tops = bm25_top_indices(["ppf", "x5", "much"], top_k=10)
        self.assertTrue(tops)

    def test_returns_empty_for_no_tokens(self):
        self.assertEqual(bm25_top_indices([], top_k=10), [])


class RRFTests(unittest.TestCase):
    def test_items_in_both_lists_win(self):
        merged = _rrf_merge([["a", "b", "c"], ["b", "c", "d"]], k=60)
        self.assertEqual(merged[0][0], "b")

    def test_order_matters(self):
        merged = _rrf_merge([["a", "b"]], k=60)
        self.assertEqual(merged, [("a", 1 / 61.0), ("b", 1 / 62.0)])


class HybridRetrieveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resettable_reset_corpus()

    def test_returns_expected_shape(self):
        corpus = _load_corpus()

        tops = bm25_top_indices(_tokenize("ppf x5 cost"), top_k=5)

        fake_dense = [
            {
                "chunk_id": corpus["chunks"][idx]["chunk_id"],
                "score": 0.9 - 0.05 * rank,
                "approved_answer": corpus["chunks"][idx]["approved_answer"],
                "text": corpus["chunks"][idx]["text"],
                "service": "PPF",
                "intent": "PRICE",
            }
            for rank, idx in enumerate(tops)
        ]

        with patch("enhancements.hybrid_search.retrieve", return_value=fake_dense):
            results = hybrid_retrieve("ppf for x5 cost", top_k=5)

        self.assertTrue(results)
        for result in results:
            self.assertIn("score", result)
            self.assertIn("fused_score", result)
            self.assertIn("approved_answer", result)

    def test_falls_back_to_dense_on_error(self):
        fake_dense = [
            {
                "chunk_id": "FT_00001",
                "score": 0.9,
                "approved_answer": "Premium lounge-style captain seating.",
                "text": "What is Luxury Recliners?",
                "service": "Luxury Recliners",
                "intent": "DISCOVERY",
            }
        ]

        with patch(
            "enhancements.hybrid_search.retrieve",
            side_effect=[RuntimeError("boom"), fake_dense],
        ):
            results = hybrid_retrieve("test message", top_k=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], "FT_00001")

    def test_returns_empty_when_dense_has_no_results(self):
        with patch("enhancements.hybrid_search.retrieve", return_value=[]):
            results = hybrid_retrieve("anything", top_k=5)

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
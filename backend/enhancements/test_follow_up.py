"""Run with: python -m unittest enhancements.test_follow_up"""

import unittest
from unittest.mock import patch

from .conversation_memory import (
    clear_session,
    get_thread_type,
    record_turn,
    reset_memory,
    set_thread_type,
)

from .follow_up import (
    build_conversation_state,
    inject_antecedent,
    is_follow_up,
    resolve_follow_up,
)


SESSION = "test-session-1"


class FollowUpDetectionTests(unittest.TestCase):
    def setUp(self):
        reset_memory()

    def test_no_referent_never_follow_up(self):
        self.assertFalse(is_follow_up("and the warranty?", None))
        self.assertFalse(is_follow_up("what about the other one?", None))

    def test_starter_connectors_detected(self):
        referent = {"service": "PPF"}
        self.assertTrue(is_follow_up("and the warranty?", referent))
        self.assertTrue(is_follow_up("also how much?", referent))
        self.assertTrue(is_follow_up("what about ppf?", referent))
        self.assertTrue(is_follow_up("so is it safe?", referent))

    def test_mention_of_referent_detected(self):
        referent = {"service": "Ceramic Coating"}
        self.assertTrue(is_follow_up("what about the other one?", referent))
        self.assertTrue(is_follow_up("can I book that too?", referent))
        self.assertTrue(is_follow_up("is it waterproof?", referent))

    def test_long_fresh_question_not_follow_up(self):
        referent = {"service": "PPF"}
        fresh = "what is the best way to take care of my car paint at home myself"
        self.assertFalse(is_follow_up(fresh, referent))

    def test_missing_api_key_falls_back_to_deterministic(self):
        record_turn(
            SESSION,
            service="Ceramic Coating",
            intent="PRICE",
            canonical_id="EXT-01_PRICE",
            approved_answer="Ceramic coating starts from a set price.",
            score=0.9,
            decision="PRICE_GUARDED",
            message="how much for ceramic",
        )

        with patch("enhancements.follow_up.rewrite_follow_up", return_value=None):
            result = resolve_follow_up(
                "and what about ppf?",
                SESSION,
                [],
            )

        self.assertIsNotNone(result)
        self.assertEqual(result["rewrite_source"], "deterministic")
        self.assertIn("Ceramic Coating", result["resolved_query"])
        self.assertIn("ppf", result["resolved_query"])
        self.assertEqual(result["referent"]["service"], "Ceramic Coating")


class AntecedentInjectionTests(unittest.TestCase):
    def test_injects_service(self):
        referent = {"service": "Luxury Recliners", "intent": "DISCOVERY"}
        query = inject_antecedent("what about the other one?", referent)
        self.assertIn("Luxury Recliners", query)
        self.assertIn("what about the other one", query)

    def test_no_service_keeps_message(self):
        query = inject_antecedent("and the warranty?", {"service": None})
        self.assertEqual(query, "and the warranty?")


class MemoryAndThreadTests(unittest.TestCase):
    def setUp(self):
        reset_memory()
        clear_session(SESSION)

    def test_record_and_retrieve_turn(self):
        record_turn(
            SESSION,
            service="PPF",
            intent="WARRANTY",
            canonical_id="EXT-01_WARRANTY",
            approved_answer="Warranty is as approved.",
            score=0.85,
        )

        with patch("enhancements.follow_up.rewrite_follow_up", return_value=None):
            result = resolve_follow_up(
                "and the warranty?",
                SESSION,
                [],
            )

        self.assertIsNotNone(result)
        self.assertEqual(result["referent"]["service"], "PPF")
        self.assertEqual(result["referent"]["intent"], "WARRANTY")

    def test_complaint_thread_persists(self):
        set_thread_type(SESSION, "COMPLAINT")
        self.assertEqual(get_thread_type(SESSION), "COMPLAINT")

        record_turn(
            SESSION,
            service="Ceramic Coating",
            intent="WARRANTY",
            canonical_id="EXT-01_WARRANTY",
            approved_answer="Warranty answer.",
            score=0.8,
            decision=None,
        )
        self.assertEqual(get_thread_type(SESSION), "COMPLAINT")

    def test_booking_decision_switches_thread(self):
        record_turn(
            SESSION,
            service="Ceramic Coating",
            intent="BOOKING",
            canonical_id="EXT-01_BOOKING",
            approved_answer="Booking flow.",
            score=0.9,
            decision="BOOKING_REQUEST",
        )
        self.assertEqual(get_thread_type(SESSION), "BOOKING")

    def test_conversation_state_note(self):
        note = build_conversation_state(
            {
                "service": "PPF",
                "intent": "PRICE",
                "approved_answer": "PPF pricing depends on the vehicle.",
            }
        )
        self.assertIn("PPF", note)
        self.assertIn("previously shared", note.lower())


if __name__ == "__main__":
    unittest.main()
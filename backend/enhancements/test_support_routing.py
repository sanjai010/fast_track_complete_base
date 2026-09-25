"""Run with: python -m unittest enhancements.test_support_routing"""

import unittest

from .support_routing import helpful_unknown_response, route_post_service_issue


class SupportRoutingTests(unittest.TestCase):
    def test_ceramic_complaint_uses_existing_approved_record(self):
        route = route_post_service_issue(
            "I got ceramic coating two days ago and I have an issue. Please check it again."
        )
        self.assertIsNotNone(route)
        self.assertEqual(route.name, "SERVICE_COMPLAINT")
        self.assertEqual(route.decision, "ESCALATE_COMPLAINT")
        self.assertEqual(route.canonical_id, "EXT-01_COMPLAINT")

    def test_generic_post_service_issue_collects_service_details(self):
        route = route_post_service_issue(
            "My BMW has a problem after my service. Please check it again."
        )
        self.assertIsNotNone(route)
        self.assertEqual(route.name, "GENERAL_POST_SERVICE_ISSUE")
        self.assertEqual(route.decision, "COLLECT_COMPLAINT_DETAILS")

    def test_ordinary_question_is_not_forced_into_complaint_flow(self):
        self.assertIsNone(route_post_service_issue("What is the price of ceramic coating?"))

    def test_peeling_complaint_escalates(self):
        route = route_post_service_issue(
            "My ceramic coating is peeling after a week"
        )
        self.assertIsNotNone(route)
        self.assertEqual(route.decision, "ESCALATE_COMPLAINT")

    def test_discovery_language_does_not_spill_into_complaints(self):
        self.assertIsNone(route_post_service_issue("Is ceramic coating scratch proof?"))
        self.assertIsNone(route_post_service_issue("Is PPF fade resistant?"))

    def test_unknown_reply_is_constructive(self):
        self.assertIn("I can best assist", helpful_unknown_response())


if __name__ == "__main__":
    unittest.main()

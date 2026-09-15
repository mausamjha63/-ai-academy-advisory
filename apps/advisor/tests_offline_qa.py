from django.test import TestCase
from apps.advisor.services.advisor_service import AdvisorService
from apps.advisor.services.offline_qa_service import OfflineQAService

class OfflineQAServiceTest(TestCase):
    def setUp(self):
        self.advisor_service = AdvisorService()

    def test_preset_questions_exist(self):
        self.assertEqual(len(OfflineQAService.PRESET_QUESTIONS), 25)

    def test_offline_matching(self):
        question_1 = "What are the prerequisites for COMP201?"
        match_1 = OfflineQAService.match_preset_question(question_1)
        self.assertIsNotNone(match_1)
        self.assertEqual(match_1['id'], 1)

        question_3 = "What is the minimum attendance required for final exams?"
        match_3 = OfflineQAService.match_preset_question(question_3)
        self.assertIsNotNone(match_3)
        self.assertEqual(match_3['id'], 3)

    def test_advisor_service_fallback_execution(self):
        # Force client to None to test offline fallback
        original_client = self.advisor_service.client
        self.advisor_service.client = None

        response = self.advisor_service.process_query("What are the prerequisites for COMP201 (Data Structures)?")
        self.assertEqual(response["state"], "ANSWERED")
        self.assertIn("COMP101", response["answer"])
        self.assertTrue(len(response["evidence"]) > 0)

        # Restore client
        self.advisor_service.client = original_client

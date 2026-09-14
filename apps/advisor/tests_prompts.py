from django.test import TestCase
from advisor.prompts import get_prompt_builder
from advisor.services.advisor_service import AdvisorService
from advisor.services.decision_engine import DecisionEngine
import os
import json
from unittest.mock import patch, MagicMock

class PromptTests(TestCase):
    def test_v1_prompt_construction(self):
        builder = get_prompt_builder('v1')
        prompt = builder.build_prompt("How many credits for minor?", [], "ANSWERED", "")
        self.assertIn("You are an academic advisor.", prompt)
        
    def test_v2_prompt_construction(self):
        builder = get_prompt_builder('v2')
        prompt = builder.build_prompt("How many credits for minor?", [], "ANSWERED", "")
        self.assertIn("ROLE: You are an official Academic Advisor", prompt)
        
    def test_v3_prompt_construction(self):
        builder = get_prompt_builder('v3')
        prompt = builder.build_prompt("Rules?", [], "ANSWERED", "")
        self.assertIn("GROUNDING RULES:", prompt)
        
    def test_v4_prompt_construction(self):
        builder = get_prompt_builder('v4')
        prompt = builder.build_prompt("Can I take DATA101?", [], "NOT_ELIGIBLE", "Missing prereq")
        self.assertIn("DECISION ENGINE STATE", prompt)
        self.assertIn("NOT_ELIGIBLE", prompt)

    @patch('advisor.services.advisor_service.genai.Client')
    def test_advisor_service_json_parsing_and_state_override(self, MockClient):
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        # Mock LLM returns ELIGIBLE
        mock_response.text = '```json\n{"state": "ELIGIBLE", "answer": "Yes, you can take it.", "reason": "You passed MKTG."}\n```'
        mock_client_instance.models.generate_content.return_value = mock_response
        
        service = AdvisorService()
        service.client = mock_client_instance
        os.environ['PROMPT_VERSION'] = 'v4'
        
        # Call with an authoritative NOT_ELIGIBLE state
        # The LLM says ELIGIBLE, but it should be overridden back to NOT_ELIGIBLE by the service.
        
        # Let's mock the internal retrieve_evidence and decision engine via patches to isolate
        mock_course = MagicMock()
        mock_course.course_code = "DATA101"
        mock_course.title = "Data Science"
        mock_course.credits = 3
        mock_course.source_metadata = {}
        
        with patch('advisor.services.advisor_service.RetrievalService.retrieve_evidence', return_value=[]), \
             patch('advisor.services.advisor_service.DecisionEngine.check_prerequisite_eligibility', return_value=(DecisionEngine.STATES['NOT_ELIGIBLE'], 'Missing Prereq')), \
             patch('advisor.services.advisor_service.AcademicDataService.get_course_info', return_value=mock_course), \
             patch('advisor.services.advisor_service.AcademicDataService.get_prerequisites', return_value=[]), \
             patch('advisor.services.advisor_service.AcademicDataService.get_course_offerings', return_value=[]):
                 
             resp = service.process_query("Can I take DATA101?", "DEMO-007")
             
             self.assertEqual(resp['state'], DecisionEngine.STATES['NOT_ELIGIBLE'])
             self.assertEqual(resp['answer'], "Yes, you can take it.")
             
    @patch('advisor.services.advisor_service.genai.Client')
    def test_malformed_json_fallback(self, MockClient):
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        # Mock LLM returns garbage
        mock_response.text = 'This is not json at all'
        mock_client_instance.models.generate_content.return_value = mock_response
        
        service = AdvisorService()
        service.client = mock_client_instance
        os.environ['PROMPT_VERSION'] = 'v4'
        
        with patch('advisor.services.advisor_service.RetrievalService.retrieve_evidence', return_value=[]):
            resp = service.process_query("What is university?", None)
            self.assertEqual(resp['state'], "INFORMATION_UNAVAILABLE") # Because there's no evidence, it shouldn't even call LLM!
            
            # Now let's give it evidence so it calls LLM
            with patch('advisor.services.advisor_service.RetrievalService.retrieve_evidence', return_value=[{"content": "Blah", "source": "X", "page": "Y"}]):
                resp = service.process_query("What is university?", None)
                self.assertIn("The AI service is temporarily unavailable", resp['answer'])

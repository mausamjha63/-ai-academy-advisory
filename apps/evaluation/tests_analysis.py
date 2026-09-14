import json
import os
import tempfile
from django.test import TestCase
from django.core.management import call_command
from django.conf import settings

class Phase5AnalysisTests(TestCase):
    def test_phase5_analysis_generates_correct_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_input = os.path.join(temp_dir, 'mock_phase4.json')
            temp_output = os.path.join(temp_dir, 'mock_phase5.json')
            
            mock_data = {
                "results": [
                    {"approach": "V1 Basic LLM", "classification": "INCORRECT", "response_time_ms": 100},
                    {"approach": "V1 Basic LLM", "classification": "CORRECT", "response_time_ms": 200},
                    {"approach": "V4 Full Academic", "classification": "CORRECT", "response_time_ms": 300},
                    {"approach": "V4 Full Academic", "classification": "UNSUPPORTED_OR_HALLUCINATED", "response_time_ms": 400},
                ]
            }
            
            with open(temp_input, 'w') as f:
                json.dump(mock_data, f)
                
            # Run the command with isolated temporary paths
            call_command('run_phase5_analysis', input=temp_input, output=temp_output)
            
            # Verify the output
            self.assertTrue(os.path.exists(temp_output))
            with open(temp_output, 'r') as f:
                analysis = json.load(f)
                
            self.assertIn('V1 Basic LLM', analysis)
            self.assertEqual(analysis['V1 Basic LLM']['total_cases'], 2)
            self.assertEqual(analysis['V1 Basic LLM']['correct'], 1)
            self.assertEqual(analysis['V1 Basic LLM']['avg_response_time_ms'], 150.0)
            
            self.assertIn('V4 Full Academic', analysis)
            self.assertEqual(analysis['V4 Full Academic']['unsupported_hallucinated'], 1)

    def test_phase5_regression_isolation(self):
        real_phase5 = os.path.join(settings.BASE_DIR, 'evaluation', 'results', 'phase5_comparison.json')
        
        # Read state of real file if it exists
        original_content = None
        if os.path.exists(real_phase5):
            with open(real_phase5, 'r') as f:
                original_content = f.read()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_input = os.path.join(temp_dir, 'mock_phase4.json')
            temp_output = os.path.join(temp_dir, 'mock_phase5.json')
            with open(temp_input, 'w') as f:
                json.dump({"results": []}, f)
                
            call_command('run_phase5_analysis', input=temp_input, output=temp_output)
            
        # Verify the real file remains untouched
        if original_content is not None:
            with open(real_phase5, 'r') as f:
                current_content = f.read()
            self.assertEqual(original_content, current_content)

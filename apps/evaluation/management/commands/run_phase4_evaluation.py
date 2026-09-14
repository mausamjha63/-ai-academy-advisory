import json
import time
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from advisor.services.advisor_service import AdvisorService
from advisor.services.decision_engine import DecisionEngine
from academics.models import Course, Prerequisite
from students.models import Student

class Command(BaseCommand):
    help = 'Runs Phase 4 Evaluation across V1-V4 models.'

    def handle(self, *args, **kwargs):
        cases_file = os.path.join(settings.BASE_DIR, 'evaluation', 'phase4_cases.json')
        results_file = os.path.join(settings.BASE_DIR, 'evaluation', 'results', 'phase4_results.json')
        
        with open(cases_file, 'r') as f:
            cases = json.load(f)
            
        approaches = [
            {'name': 'V1 Basic LLM', 'prompt': 'v1', 'use_rag': False, 'use_student': False},
            {'name': 'V2 Structured Prompting', 'prompt': 'v2', 'use_rag': False, 'use_student': False},
            {'name': 'V3 RAG Grounded', 'prompt': 'v3', 'use_rag': True, 'use_student': False},
            {'name': 'V4 Full Academic', 'prompt': 'v4', 'use_rag': True, 'use_student': True},
        ]
        
        results = []
        metrics = {
            'total_cases': len(cases) * len(approaches),
            'correct': 0,
            'partially_correct': 0,
            'unsupported_hallucinated': 0,
            'incorrect': 0,
            'missing_info_accuracy': 0,
            'conflict_accuracy': 0,
            'avg_response_time': 0,
            'total_time': 0
        }
        
        # Setup synthetic conflict test case if needed
        demo_test_student, _ = Student.objects.get_or_create(student_id="DEMO-TEST", profile_completeness_status="COMPLETE")
        course, _ = Course.objects.get_or_create(course_code="DATA101", title="Intro")
        Prerequisite.objects.get_or_create(course=course, prerequisite_condition="MKTG201", defaults={'uncertainty_source_metadata': {'source_file': 'Source_A.xlsx'}})
        Prerequisite.objects.get_or_create(course=course, prerequisite_condition="UCOR103", defaults={'uncertainty_source_metadata': {'source_file': 'Source_B.xlsx'}})

        for approach in approaches:
            self.stdout.write(f"--- RUNNING EVALUATION FOR: {approach['name']} ---")
            os.environ['PROMPT_VERSION'] = approach['prompt']
            service = AdvisorService()
            
            for case in cases:
                # Experimental isolation
                student_id = case['student_profile'] if approach['use_student'] else None
                
                # Mock RAG if use_rag is False
                original_retrieve = service.retrieval_service.retrieve_evidence
                if not approach['use_rag']:
                    service.retrieval_service.retrieve_evidence = lambda *args, **kwargs: []
                
                start_time = time.time()
                try:
                    resp = service.process_query(case['question'], student_id)
                except Exception as e:
                    resp = {"state": "ERROR", "answer": str(e), "evidence": [], "missing_information": []}
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                
                # Restore RAG
                service.retrieval_service.retrieve_evidence = original_retrieve

                # Classify
                actual_state = resp.get('state', '')
                expected_state = case['expected_state']
                
                classification = "INCORRECT"
                
                # V1/V2 don't use student data, so they can't accurately trigger NEEDS_MORE_INFORMATION or ELIGIBLE correctly for student-specific queries
                if not approach['use_student'] and expected_state in ['ELIGIBLE', 'NOT_ELIGIBLE', 'NEEDS_MORE_INFORMATION']:
                    classification = "INCORRECT" if actual_state in ['ELIGIBLE', 'NOT_ELIGIBLE'] else "PARTIALLY_CORRECT"
                    if actual_state == "INFORMATION_UNAVAILABLE" or actual_state == "ANSWERED":
                        classification = "PARTIALLY_CORRECT" # Because they legitimately don't have the data
                else:
                    if actual_state == expected_state:
                        classification = "CORRECT"
                    elif expected_state in actual_state or actual_state in expected_state:
                        classification = "PARTIALLY_CORRECT"
                
                # Check Evidence hallucination
                evidence = resp.get('evidence', [])
                evidence_sources = [e.get('source', '') if isinstance(e, dict) else str(e) for e in evidence]
                
                if approach['use_rag'] and case['expected_evidence_source']:
                    if not any(case['expected_evidence_source'] in src for src in evidence_sources):
                        if actual_state not in ['INFORMATION_UNAVAILABLE', 'OUT_OF_SCOPE', 'NEEDS_MORE_INFORMATION']:
                            classification = "UNSUPPORTED_OR_HALLUCINATED"
                
                # Special metrics tracking
                if expected_state == 'NEEDS_MORE_INFORMATION' and approach['use_student']:
                    if actual_state == 'NEEDS_MORE_INFORMATION':
                        metrics['missing_info_accuracy'] += 1
                        
                if expected_state == 'CONFLICTING_INFORMATION':
                    if actual_state == 'CONFLICTING_INFORMATION':
                        metrics['conflict_accuracy'] += 1

                # Update global metrics
                metrics['total_time'] += duration
                if classification == "CORRECT": metrics['correct'] += 1
                elif classification == "PARTIALLY_CORRECT": metrics['partially_correct'] += 1
                elif classification == "UNSUPPORTED_OR_HALLUCINATED": metrics['unsupported_hallucinated'] += 1
                else: metrics['incorrect'] += 1

                results.append({
                    'approach': approach['name'],
                    'test_case_id': case['test_case_id'],
                    'question': case['question'],
                    'expected_state': expected_state,
                    'actual_state': actual_state,
                    'classification': classification,
                    'response_time_ms': duration,
                    'answer': resp.get('answer'),
                    'evidence': evidence_sources
                })
        
        metrics['avg_response_time'] = metrics['total_time'] / metrics['total_cases']
        
        with open(results_file, 'w') as f:
            json.dump({'metrics': metrics, 'results': results}, f, indent=4)
            
        self.stdout.write(self.style.SUCCESS(f"Evaluation complete. Results saved to {results_file}."))
        self.stdout.write(f"Accuracy: {metrics['correct'] / metrics['total_cases'] * 100:.2f}%")
        self.stdout.write(f"Hallucination Rate: {metrics['unsupported_hallucinated'] / metrics['total_cases'] * 100:.2f}%")

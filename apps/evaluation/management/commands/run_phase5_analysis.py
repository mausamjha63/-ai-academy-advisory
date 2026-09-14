import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Runs Phase 5 Analysis on Phase 4 results.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            default=os.path.join(settings.BASE_DIR, 'evaluation', 'results', 'phase4_results.json'),
            help='Path to the input phase4_results.json file'
        )
        parser.add_argument(
            '--output',
            default=os.path.join(settings.BASE_DIR, 'evaluation', 'results', 'phase5_comparison.json'),
            help='Path to the output phase5_comparison.json file'
        )

    def handle(self, *args, **options):
        phase4_file = options['input']
        phase5_file = options['output']
        
        with open(phase4_file, 'r') as f:
            data = json.load(f)
            
        results = data.get('results', [])
        
        approaches = ['V1 Basic LLM', 'V2 Structured Prompting', 'V3 RAG Grounded', 'V4 Full Academic']
        
        analysis = {}
        for approach in approaches:
            app_results = [r for r in results if r['approach'] == approach]
            total = len(app_results)
            correct = len([r for r in app_results if r['classification'] == 'CORRECT'])
            partial = len([r for r in app_results if r['classification'] == 'PARTIALLY_CORRECT'])
            hallucinated = len([r for r in app_results if r['classification'] == 'UNSUPPORTED_OR_HALLUCINATED'])
            incorrect = len([r for r in app_results if r['classification'] == 'INCORRECT'])
            
            avg_time = sum(r.get('response_time_ms', 0) for r in app_results) / total if total > 0 else 0
            
            analysis[approach] = {
                'total_cases': total,
                'correct': correct,
                'partially_correct': partial,
                'unsupported_hallucinated': hallucinated,
                'incorrect': incorrect,
                'avg_response_time_ms': avg_time
            }
            
        os.makedirs(os.path.dirname(phase5_file), exist_ok=True)
        with open(phase5_file, 'w') as f:
            json.dump(analysis, f, indent=4)
            
        self.stdout.write(self.style.SUCCESS(f"Analysis complete. Results saved to {phase5_file}."))


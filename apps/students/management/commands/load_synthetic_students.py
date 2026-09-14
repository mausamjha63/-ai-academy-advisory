import json
from django.core.management.base import BaseCommand
from students.models import Student, StudentCourseHistory
from academics.models import Course

class Command(BaseCommand):
    help = 'Load synthetic student profiles into the database idempotently'

    def handle(self, *args, **kwargs):
        students_data = [
            # 1. Complete academic profile (eligible for something)
            {
                "student_id": "DEMO-001", "programme": "BTech Data Science", "batch": "2024",
                "current_semester": 5, "cgpa": 8.5, "credits_earned": 90,
                "minor_opted": None, "profile_completeness_status": "COMPLETE",
                "history": [("UCOR103", "COMPLETED"), ("UCOR203", "COMPLETED")]
            },
            # 2. Missing programme
            {
                "student_id": "DEMO-002", "programme": None, "batch": "2025",
                "current_semester": 3, "cgpa": 6.2, "credits_earned": 45,
                "minor_opted": "AI", "profile_completeness_status": "MISSING_ACADEMIC_INFO",
                "history": []
            },
            # 3. Missing batch
            {
                "student_id": "DEMO-003", "programme": "BTech Computer Science", "batch": None,
                "current_semester": 5, "cgpa": 7.0, "credits_earned": 85,
                "minor_opted": None, "profile_completeness_status": "MISSING_ACADEMIC_INFO",
                "history": []
            },
            # 4. Missing current semester
            {
                "student_id": "DEMO-004", "programme": "BTech Data Science", "batch": "2026",
                "current_semester": None, "cgpa": 8.0, "credits_earned": 20,
                "minor_opted": None, "profile_completeness_status": "MISSING_ACADEMIC_INFO",
                "history": []
            },
            # 5. Missing course history
            {
                "student_id": "DEMO-005", "programme": "BTech Computer Science", "batch": "2024",
                "current_semester": 5, "cgpa": 7.5, "credits_earned": 80,
                "minor_opted": None, "profile_completeness_status": "COMPLETE",
                "history": []
            },
            # 6. Completed prerequisite (e.g. for MKTG201 -> MGMT302)
            {
                "student_id": "DEMO-006", "programme": "BTech Computer Science", "batch": "2022",
                "current_semester": 4, "cgpa": 8.2, "credits_earned": 60,
                "minor_opted": "Marketing", "profile_completeness_status": "COMPLETE",
                "history": [("MKTG201", "COMPLETED")]
            },
            # 7. Prerequisite not completed
            {
                "student_id": "DEMO-007", "programme": "BTech Computer Science", "batch": "2022",
                "current_semester": 4, "cgpa": 7.1, "credits_earned": 60,
                "minor_opted": "Marketing", "profile_completeness_status": "COMPLETE",
                "history": [("UCOR103", "COMPLETED")] # Missing MKTG201
            },
            # 8. Failed prerequisite/course
            {
                "student_id": "DEMO-008", "programme": "BTech Computer Science", "batch": "2022",
                "current_semester": 4, "cgpa": 7.1, "credits_earned": 60,
                "minor_opted": "Marketing", "profile_completeness_status": "COMPLETE",
                "history": [("MKTG201", "FAILED")]
            },
            # 9. Low CGPA / progression-related case
            {
                "student_id": "DEMO-009", "programme": "BTech Data Science", "batch": "2025",
                "current_semester": 3, "cgpa": 3.5, "credits_earned": 30,
                "minor_opted": None, "profile_completeness_status": "COMPLETE",
                "history": []
            },
            # 10. Completely INCOMPLETE
            {
                "student_id": "DEMO-010", "programme": None, "batch": None,
                "current_semester": None, "cgpa": None, "credits_earned": None,
                "minor_opted": None, "profile_completeness_status": "INCOMPLETE",
                "history": []
            }
        ]

        count = 0
        history_count = 0
        for s_data in students_data:
            obj, created = Student.objects.update_or_create(
                student_id=s_data['student_id'],
                defaults={
                    'programme': s_data['programme'],
                    'batch': s_data['batch'],
                    'current_semester': s_data['current_semester'],
                    'cgpa': s_data['cgpa'],
                    'credits_earned': s_data['credits_earned'],
                    'minor_opted': s_data['minor_opted'],
                    'profile_completeness_status': s_data['profile_completeness_status']
                }
            )
            if created:
                count += 1
                
            # Create synthetic history
            for course_code, status in s_data['history']:
                course = Course.objects.filter(course_code=course_code).first()
                if not course:
                    # Create a dummy course just for testing if it doesn't exist in actual imports
                    course, _ = Course.objects.get_or_create(course_code=course_code, defaults={"title": f"Synthetic {course_code}"})
                
                h_obj, h_created = StudentCourseHistory.objects.update_or_create(
                    student=obj,
                    course=course,
                    defaults={'status': status}
                )
                if h_created:
                    history_count += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(students_data)} synthetic students. Added {history_count} course history records."))

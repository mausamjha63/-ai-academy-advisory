from academics.models import Course, Prerequisite
from students.models import Student, StudentCourseHistory
from .academic_data_service import AcademicDataService

class DecisionEngine:
    STATES = {
        'ELIGIBLE': 'ELIGIBLE',
        'NOT_ELIGIBLE': 'NOT_ELIGIBLE',
        'NEEDS_MORE_INFORMATION': 'NEEDS_MORE_INFORMATION',
        'INFORMATION_UNAVAILABLE': 'INFORMATION_UNAVAILABLE',
        'CONFLICTING_INFORMATION': 'CONFLICTING_INFORMATION',
        'OUT_OF_SCOPE': 'OUT_OF_SCOPE'
    }

    @staticmethod
    def check_prerequisite_eligibility(student_id, course_code):
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return DecisionEngine.STATES['NEEDS_MORE_INFORMATION'], "Student profile not found."
            
        course = AcademicDataService.get_course_info(course_code)
        if not course:
            return DecisionEngine.STATES['INFORMATION_UNAVAILABLE'], "Course information not found in authoritative sources."
            
        prereqs = AcademicDataService.get_prerequisites(course_code)
        if not prereqs:
            return DecisionEngine.STATES['ELIGIBLE'], f"No prerequisites explicitly established for {course_code}."
            
        valid_prereqs = []
        for p in prereqs:
            cond = p.prerequisite_condition
            if not cond:
                continue
            cond_upper = cond.upper().strip()
            if cond_upper in ['NIL', 'NONE', 'TBA', 'TBD', 'UNKNOWN', 'MISSING', 'BLANK', '-']:
                continue
            valid_prereqs.append(p)
            
        if not valid_prereqs:
            return DecisionEngine.STATES['ELIGIBLE'], f"No specific prerequisites established for {course_code}."
            
        # CONFLICT CHECK:
        distinct_conditions = set(p.prerequisite_condition.upper().strip() for p in valid_prereqs)
        if len(distinct_conditions) > 1:
            sources = [p.uncertainty_source_metadata.get('source_file') for p in valid_prereqs if p.uncertainty_source_metadata]
            return DecisionEngine.STATES['CONFLICTING_INFORMATION'], f"Conflicting prerequisites found from sources: {sources}"

        # If we have valid prerequisites, we need the student's history
        history = StudentCourseHistory.objects.filter(student=student)
        if not history.exists() and student.profile_completeness_status != "COMPLETE":
            return DecisionEngine.STATES['NEEDS_MORE_INFORMATION'], "Student course history is required to determine prerequisite eligibility but is missing."
            
        completed = history.filter(status='COMPLETED')
        completed_course_codes = [h.course.course_code.upper() for h in completed]
        
        # Simple prerequisite logic
        for prereq in valid_prereqs:
            cond = prereq.prerequisite_condition.upper().strip()
            if cond not in completed_course_codes:
                return DecisionEngine.STATES['NOT_ELIGIBLE'], f"Missing prerequisite: {cond}"
                
        return DecisionEngine.STATES['ELIGIBLE'], "All prerequisites are satisfied."

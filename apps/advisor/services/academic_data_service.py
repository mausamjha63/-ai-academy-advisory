from academics.models import Course, CourseOffering, Prerequisite
from django.db.models import Q

class AcademicDataService:
    @staticmethod
    def get_course_info(course_code):
        try:
            return Course.objects.get(course_code__iexact=course_code)
        except Course.DoesNotExist:
            return None
            
    @staticmethod
    def get_prerequisites(course_code):
        course = AcademicDataService.get_course_info(course_code)
        if not course:
            return None
        return list(Prerequisite.objects.filter(course=course))
        
    @staticmethod
    def get_course_offerings(course_code, semester=None, batch=None):
        course = AcademicDataService.get_course_info(course_code)
        if not course:
            return None
            
        offerings = CourseOffering.objects.filter(course=course)
        if semester:
            offerings = offerings.filter(semester=semester)
        if batch:
            offerings = offerings.filter(batch_context__icontains=batch)
            
        return list(offerings)

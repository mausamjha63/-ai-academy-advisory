from django.db import models
from academics.models import Course

class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True, help_text="e.g. 'Student A'")
    programme = models.CharField(max_length=100, null=True, blank=True)
    batch = models.CharField(max_length=50, null=True, blank=True)
    current_semester = models.IntegerField(null=True, blank=True)
    cgpa = models.FloatField(null=True, blank=True)
    credits_earned = models.FloatField(null=True, blank=True)
    minor_opted = models.CharField(max_length=100, null=True, blank=True)
    profile_completeness_status = models.CharField(max_length=50, default='COMPLETE')

    def __str__(self):
        return self.student_id

class StudentCourseHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_history')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=50) # e.g. 'COMPLETED', 'FAILED', 'FA', 'ONGOING'
    grade = models.CharField(max_length=10, null=True, blank=True)
    semester = models.CharField(max_length=50, null=True, blank=True)
    source_profile_metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.course.course_code} ({self.status})"

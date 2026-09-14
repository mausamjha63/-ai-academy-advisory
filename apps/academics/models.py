from django.db import models

class Course(models.Model):
    course_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    credits = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    bucket = models.CharField(max_length=100, null=True, blank=True)
    programme_applicability = models.CharField(max_length=255, null=True, blank=True)
    source_metadata = models.JSONField(null=True, blank=True, help_text="Metadata about source provenance")

    def save(self, *args, **kwargs):
        if self.course_code:
            self.course_code = self.course_code.replace('/', '-').replace('\n', ' ').strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_code} - {self.title}"

class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    semester = models.CharField(max_length=50, null=True, blank=True) # Could be TBA/NIL
    academic_year = models.CharField(max_length=50, null=True, blank=True)
    batch_context = models.CharField(max_length=100, null=True, blank=True)
    programme_context = models.CharField(max_length=100, null=True, blank=True)
    availability_status = models.CharField(max_length=100, null=True, blank=True)
    source_reference = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.course.course_code} - Sem {self.semester}"

class Prerequisite(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite_condition = models.CharField(max_length=255)
    condition_type = models.CharField(max_length=50, null=True, blank=True)
    uncertainty_source_metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.course.course_code} requires {self.prerequisite_condition}"

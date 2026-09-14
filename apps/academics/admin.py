from django.contrib import admin
from .models import Course, CourseOffering, Prerequisite

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'credits', 'bucket')
    search_fields = ('course_code', 'title')
    list_filter = ('bucket',)

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'academic_year', 'availability_status')
    search_fields = ('course__course_code', 'course__title')
    list_filter = ('semester', 'academic_year')

@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'prerequisite_condition')
    search_fields = ('course__course_code',)

from django.contrib import admin
from .models import Student, StudentCourseHistory

class StudentCourseHistoryInline(admin.TabularInline):
    model = StudentCourseHistory
    extra = 1

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'programme', 'batch', 'cgpa', 'profile_completeness_status')
    search_fields = ('student_id',)
    list_filter = ('programme', 'batch', 'profile_completeness_status')
    inlines = [StudentCourseHistoryInline]

@admin.register(StudentCourseHistory)
class StudentCourseHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'grade', 'semester')
    search_fields = ('student__student_id', 'course__course_code')
    list_filter = ('status', 'semester')

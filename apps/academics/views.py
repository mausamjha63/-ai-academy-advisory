from django.shortcuts import render
from .models import Course
from students.models import Student

def courses_explore(request):
    synthetic_students = Student.objects.all()
    courses = Course.objects.all().prefetch_related('prerequisites')
    
    query = request.GET.get('q', '')
    if query:
        courses = courses.filter(title__icontains=query) | courses.filter(course_code__icontains=query)
        
    context = {
        'courses': courses,
        'synthetic_students': synthetic_students,
        'search_query': query,
    }
    return render(request, 'academics/courses.html', context)

from django.shortcuts import get_object_or_404

def course_detail(request, course_code):
    synthetic_students = Student.objects.all()
    course = get_object_or_404(Course, course_code=course_code)
    
    # Pre-fetch the related prerequisites and offerings
    prerequisites = course.prerequisites.all()
    offerings = course.offerings.all()
    
    context = {
        'course': course,
        'prerequisites': prerequisites,
        'offerings': offerings,
        'synthetic_students': synthetic_students,
    }
    return render(request, 'academics/course_detail.html', context)

from django.shortcuts import render
from django.http import JsonResponse
from .services.advisor_service import AdvisorService
from students.models import Student

def advisor_chat(request):
    if request.method == "POST":
        query = request.POST.get('query')
        student_id = request.POST.get('student_id')
        
        service = AdvisorService()
        response = service.process_query(query, student_id)
        
        return JsonResponse(response)
        
    synthetic_students = Student.objects.all()
    return render(request, 'advisor/chat.html', {'synthetic_students': synthetic_students})

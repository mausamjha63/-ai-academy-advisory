from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from .services.advisor_service import AdvisorService
from .models import ChatSession, ChatMessage
from students.models import Student

def advisor_chat(request):
    student_id = request.GET.get('student_id') or request.POST.get('student_id')
    active_student = None
    if student_id:
        active_student = Student.objects.filter(student_id=student_id).first()

    session_id = request.GET.get('session_id') or request.POST.get('session_id')

    # AJAX POST request (sending question)
    if request.method == "POST":
        query = request.POST.get('query', '').strip()
        if not query:
            return JsonResponse({'error': 'Query empty'}, status=400)

        # Get or create active session
        chat_session = None
        if session_id:
            chat_session = ChatSession.objects.filter(id=session_id).first()
        
        if not chat_session:
            chat_session = ChatSession.objects.create(
                student=active_student,
                title=query[:40] + ("..." if len(query) > 40 else "")
            )
        elif chat_session.title in ["New Conversation", "New Chat"]:
            chat_session.title = query[:40] + ("..." if len(query) > 40 else "")
            if active_student:
                chat_session.student = active_student
            chat_session.save()

        # Save user message
        ChatMessage.objects.create(
            session=chat_session,
            sender='USER',
            content=query
        )

        # Execute Advisor Service
        service = AdvisorService()
        response = service.process_query(query, student_id)

        # Save bot response
        ChatMessage.objects.create(
            session=chat_session,
            sender='BOT',
            content=response.get('answer', ''),
            state=response.get('state', ''),
            reason=response.get('reason'),
            recommendation=response.get('recommendation'),
            missing_information=response.get('missing_information', []),
            evidence=response.get('evidence', [])
        )

        chat_session.save() # touch updated_at
        request.session['active_chat_session_id'] = str(chat_session.id)

        return JsonResponse({
            **response,
            'session_id': str(chat_session.id),
            'session_title': chat_session.title
        })

    # GET Request (page load)
    chat_session = None
    if session_id:
        chat_session = ChatSession.objects.filter(id=session_id).first()

    if not chat_session and 'active_chat_session_id' in request.session:
        saved_id = request.session['active_chat_session_id']
        chat_session = ChatSession.objects.filter(id=saved_id).first()

    if not chat_session:
        if active_student:
            chat_session = ChatSession.objects.filter(student=active_student).first()
        else:
            chat_session = ChatSession.objects.first()

    if not chat_session:
        chat_session = ChatSession.objects.create(
            student=active_student,
            title="New Conversation"
        )

    request.session['active_chat_session_id'] = str(chat_session.id)

    recent_sessions = list(ChatSession.objects.all()[:30])
    messages = list(chat_session.messages.all())
    synthetic_students = Student.objects.all()

    context = {
        'active_session': chat_session,
        'recent_sessions': recent_sessions,
        'messages': messages,
        'synthetic_students': synthetic_students,
        'active_student': active_student,
    }
    return render(request, 'advisor/chat.html', context)

def new_chat(request):
    student_id = request.GET.get('student_id')
    active_student = Student.objects.filter(student_id=student_id).first() if student_id else None

    session = ChatSession.objects.create(
        student=active_student,
        title="New Conversation"
    )
    request.session['active_chat_session_id'] = str(session.id)
    
    url = reverse('advisor_chat') + f"?session_id={session.id}"
    if student_id:
        url += f"&student_id={student_id}"
    return redirect(url)

def delete_chat(request, session_id):
    student_id = request.GET.get('student_id')
    ChatSession.objects.filter(id=session_id).delete()
    if request.session.get('active_chat_session_id') == str(session_id):
        request.session.pop('active_chat_session_id', None)
        
    url = reverse('advisor_chat')
    if student_id:
        url += f"?student_id={student_id}"
    return redirect(url)

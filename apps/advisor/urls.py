from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.advisor_chat, name='advisor_chat'),
    path('chat/new/', views.new_chat, name='new_chat'),
    path('chat/delete/<uuid:session_id>/', views.delete_chat, name='delete_chat'),
]

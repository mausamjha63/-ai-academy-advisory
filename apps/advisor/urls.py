from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.advisor_chat, name='advisor_chat'),
]

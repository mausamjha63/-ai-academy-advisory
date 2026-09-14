from django.urls import path
from . import views

urlpatterns = [
    path('', views.courses_explore, name='courses_explore'),
    path('<str:course_code>/', views.course_detail, name='course_detail'),
]

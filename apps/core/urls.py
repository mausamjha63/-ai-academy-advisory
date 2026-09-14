from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('signin/', views.signin_page, name='signin'),
    path('signup/', views.signup_page, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('system-status/', views.system_status, name='system_status'),
    path('students/', views.students_list, name='students_list'),
    path('academic-structure/', views.academic_structure, name='academic_structure'),
    path('documents/', views.documents_sources, name='documents_sources'),
    path('administration/', views.administration, name='administration'),
    path('search/', views.global_search, name='global_search'),
]

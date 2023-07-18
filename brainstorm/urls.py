from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('questions_list/', views.questions_list, name='questions_list'),
    path('question_detail/<int:question_id>/', views.question_detail, name='question_detail'),
    path('ask_question/', views.ask_question, name='ask_question'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('set-language/<str:lang_code>/', views.set_language, name='set_language'),
]

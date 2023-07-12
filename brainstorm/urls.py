from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('qa_portal/', views.index, name='qa_portal'),
    path('contact/', views.index, name='contact'),
    path('set-language/<str:lang_code>/',
         views.set_language, name='set_language'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Homepage and Portal URLs
    path('', views.index, name='index'),
    path('portal/', views.portal, name='portal'),

    # Question URLs
    path('question_detail/<int:question_id>/', views.question_detail, name='question_detail'),  # View question details
    path('ask_question/', views.ask_question, name='ask_question'),  # Ask a new question

    # Contact and Authentication URLs
    path('contact/', views.contact, name='contact'),  # Contact page
    path('login/', views.login, name='login'),  # User login
    path('register/', views.register, name='register'),  # User registration
    path('logout/', views.logout, name='logout'),  # User logout
    path('set-language/<str:lang_code>/', views.set_language, name='set_language'),  # Set user language

    # Admin Panel URLs
    path('panel/', views.panel, name='panel'),  # Admin panel
    path('add_question/', views.add_question, name='add_question'),  # Add a new question
    path('edit_question/<int:question_id>/', views.edit_question, name='edit_question'),  # Edit a question
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),  # Delete a question
    path('admin_register/', views.admin_register, name='admin_register'),  # Admin registration page

    # Like URLs
    path('like_question/<int:question_id>/', views.like_question, name='like_question'),  # Like a question
    path('like_comment/<int:comment_id>/', views.like_comment, name='like_comment'),  # Like a comment

    # Comment URLs
    path('question_detail/<int:question_id>/add_comment/', views.add_comment, name='add_comment'),  # Add a comment
    path('question_detail/<int:question_id>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),  # Edit a comment
    path('question_detail/<int:question_id>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),  # Delete a comment
]

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import activate
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def index(request):
    return render(request, 'brainstorm/index.html')


def qa_portal(request):
    return render(request, 'brainstorm/index.html')


def contact(request):
    if request.method == 'POST':
        return render(request, 'brainstorm/index.html')
    return render(request, 'brainstorm/contact.html')


@login_required
def set_language(request, lang_code):
    if lang_code:
        activate(lang_code)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    else:
        return HttpResponseRedirect(reverse('index'))


@login_required
def questions_list(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT question_id, question_title, question_description, creation_date FROM Question")
        question_list = cursor.fetchall()

    context = {
        'question_list': question_list,
    }
    return render(request, 'brainstorm/questions_list.html', context)


@login_required
def question_detail(request, question_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM Question WHERE question_id = %s", [question_id])
        question_row = cursor.fetchone()

    question = {
        'question_id': question_row[0],
        'user_id': question_row[1],
        'question_title': question_row[2],
        'question_description': question_row[3],
        'creation_date': question_row[4],
    }

    with connection.cursor() as cursor:
        cursor.execute("SELECT username FROM auth_user WHERE id = %s", [
                       question['user_id']])
        user_row = cursor.fetchone()
        if user_row:
            question['username'] = user_row[0]
        else:
            question['username'] = 'Unknown User'
    context = {
        'question': question,
    }
    return render(request, 'brainstorm/question_detail.html', context)


@login_required
def ask_question(request):
    if request.method == 'POST':
        question_title = request.POST.get('questionInput')
        question_description = request.POST.get('detailsInput')

        if not question_title:
            messages.error(request, "Question title is required.")
        if not question_description:
            messages.error(request, "Question description is required.")
        if not question_title or not question_description:
            return render(request, 'brainstorm/ask_question.html', {'questionInput': question_title, 'detailsInput': question_description})

        creation_date = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Question (user_id, question_title, question_description, creation_date) "
                "VALUES (%s, %s, %s, %s)",
                [user_id, question_title, question_description, creation_date]
            )

        return redirect('questions_list')

    return render(request, 'brainstorm/ask_question.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        if not (username and password):
            messages.error(request, "All fields are required")
            return render(request, 'brainstorm/login.html', {'username': username, 'password': password})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'brainstorm/login.html', {'username': username, 'password': password})

    return render(request, 'brainstorm/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        term = request.POST.get('agreement')
        error_messages = []
        if not (username and email and password and confirm_password and term):
            error_messages.append("All fields are required")
        elif password != confirm_password:
            error_messages.append("Passwords do not match")
        elif not term:
            error_messages.append("You must agree to the Terms of Service")
        else:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                error_messages.append("Username or email already exists")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)

                messages.success(
                    request, "Registration successful. You can now login.")
                return redirect('login')
        context = {
            'username': username,
            'email': email,
            'error_messages': error_messages,
        }
        return render(request, 'brainstorm/register.html', context)

    return render(request, 'brainstorm/register.html')


def logout(request):
    auth_logout(request)
    return redirect('login')

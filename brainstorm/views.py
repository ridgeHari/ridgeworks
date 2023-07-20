from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import activate, gettext as _
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings


@user_passes_test(lambda u: u.is_superuser)
def panel(request):
    # Execute a SELECT query to fetch all questions from the database
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT question_id, question_title, question_description FROM question ORDER BY question_id DESC")
        question_list = cursor.fetchall()

    context = {
        'question_list': question_list
    }
    return render(request, 'brainstorm/admin/panel.html', context)


def add_question(request):
    if request.method == 'POST':
        question_title = request.POST.get('questionInput')
        question_description = request.POST.get('detailsInput')

        if not question_title:
            messages.error(request, _("Question title is required."))
        if not question_description:
            messages.error(request, _("Question description is required."))
        if not question_title or not question_description:
            return render(request, 'brainstorm/admin/add_question.html', {'questionInput': question_title, 'detailsInput': question_description})

        creation_date = timezone.localtime(
            timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Question (user_id, question_title, question_description, creation_date) "
                "VALUES (%s, %s, %s, %s)",
                [user_id, question_title, question_description, creation_date]
            )

        return redirect('panel')
    return redirect('panel')


def edit_question(request, question_id):
    # Execute a SELECT query to fetch the specific question from the database
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT question_id, question_title, question_description FROM question WHERE question_id = %s",
            [question_id]
        )
        question_row = cursor.fetchone()

    if question_row:
        question = {
            'id': question_row[0],
            'title': question_row[1],
            'description': question_row[2]
        }

        if request.method == 'POST':
            question_title = request.POST.get('question_title')
            question_description = request.POST.get('question_description')

            # Execute an UPDATE query to modify the question in the database
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE question SET question_title = %s, question_description = %s WHERE question_id = %s",
                    [question_title, question_description, question_id]
                )

            return redirect('panel')

        context = {
            'question': question
        }
        return render(request, 'brainstorm/admin/edit_question.html', context)
    else:
        return redirect('panel')


def delete_question(request, question_id):
    # Execute a DELETE query to remove the question from the database
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM question WHERE question_id = %s", [question_id])

    return redirect('panel')


def index(request):
    return render(request, 'brainstorm/index.html')


def contact(request):
    if request.method == 'POST':
        return render(request, 'brainstorm/index.html')
    return render(request, 'brainstorm/contact.html')


def set_language(request, lang_code):
    if lang_code:
        activate(lang_code)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    else:
        return HttpResponseRedirect(reverse('index'))


@login_required
def portal(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT question_id, question_title, question_description, creation_date, likes FROM Question ORDER BY likes DESC")
        question_list = cursor.fetchall()

    context = {
        'question_list': question_list,
    }
    return render(request, 'brainstorm/portal.html', context)


@login_required
def ask_question(request):
    if request.method == 'POST':
        question_title = request.POST.get('questionInput')
        question_description = request.POST.get('detailsInput')

        if not question_title:
            messages.error(request, _("Question title is required."))
        if not question_description:
            messages.error(request, _("Question description is required."))
        if not question_title or not question_description:
            return render(request, 'brainstorm/ask_question.html', {'questionInput': question_title, 'detailsInput': question_description})

        creation_date = timezone.localtime(
            timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Question (user_id, question_title, question_description, creation_date) "
                "VALUES (%s, %s, %s, %s)",
                [user_id, question_title, question_description, creation_date]
            )

        return redirect('portal')

    return render(request, 'brainstorm/ask_question.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        if not (username and password):
            messages.error(request, _("All fields are required"))
            return render(request, 'brainstorm/login.html', {'username': username, 'password': password})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if not remember:
                request.session.set_expiry(0)  # Session will expire when the user closes the browser
            else:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Session will expire after the specified duration in settings
            return redirect('portal')
        else:
            messages.error(request, _("Invalid username or password"))
            return render(request, 'brainstorm/login.html', {'username': username, 'password': password})

    return render(request, 'brainstorm/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        term = request.POST.get('agreement')
        is_admin = request.POST.get('is_admin') == 'on'
        error_messages = []
        if not (username and email and password and confirm_password and term):
            error_messages.append(_("All fields are required"))
        elif password != confirm_password:
            error_messages.append(_("Passwords do not match"))
        elif not term:
            error_messages.append(_("You must agree to the Terms of Service"))
        else:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                error_messages.append(_("Username or email already exists"))
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)

                if is_admin:
                    user.is_superuser = True
                    user.save()

                messages.success(
                    request, _("Registration successful. You can now login."))
                return redirect('login')
        context = {
            'username': username,
            'email': email,
            'error_messages': error_messages,
        }
        return render(request, 'brainstorm/register.html', context)

    return render(request, 'brainstorm/register.html')


@login_required
def admin_register(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        term = request.POST.get('agreement')
        is_admin = request.POST.get('is_admin') == 'on'
        error_messages = []
        if not (username and email and password and confirm_password and term):
            error_messages.append(_("All fields are required"))
        elif password != confirm_password:
            error_messages.append(_("Passwords do not match"))
        elif not term:
            error_messages.append(_("You must agree to the Terms of Service"))
        else:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                error_messages.append(_("Username or email already exists"))
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)

                if is_admin:
                    user.is_superuser = True
                    user.save()
                success_message = f"{user.username}'s Registration successful."
                return render(request, 'brainstorm/admin/register.html', {'success_message': success_message})
        context = {
            'username': username,
            'email': email,
            'error_messages': error_messages,
        }
        return render(request, 'brainstorm/admin/register.html', context)
    return render(request, 'brainstorm/admin/register.html')


def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required
def question_detail(request, question_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM Question WHERE question_id = %s", [question_id]
        )
        question_row = cursor.fetchone()

        if question_row:
            question = {
                'question_id': question_row[0],
                'user_id': question_row[1],
                'question_title': question_row[2],
                'question_description': question_row[3],
                'creation_date': question_row[4],
            }

            # Fetch question likes count
            cursor.execute(
                "SELECT likes FROM Question WHERE question_id = %s",
                [question_id]
            )
            question_likes_count = cursor.fetchone()[0]
            question['likes'] = question_likes_count

            # Check if the user has liked the question
            user_has_liked_question = False
            if request.user.is_authenticated:
                cursor.execute(
                    "SELECT id FROM UserLike WHERE user_id = %s AND question_id = %s AND like_type = 'question'",
                    [request.user.id, question_id]
                )
                if cursor.fetchone():
                    user_has_liked_question = True

            cursor.execute(
                "SELECT username FROM auth_user WHERE id = %s",
                [question['user_id']]
            )
            user_row = cursor.fetchone()
            if user_row:
                question['username'] = user_row[0]
            else:
                question['username'] = 'Unknown User'

            cursor.execute(
                "SELECT * FROM Comment WHERE question_id = %s", [question_id]
            )
            # Fetch comments and check if the user has liked each comment
            comments = []
            for comment_row in cursor.fetchall():
                comment = {
                    'comment_id': comment_row[0],
                    'user_id': comment_row[2],
                    'comment_text': comment_row[3],
                    'creation_date': comment_row[4],
                }

                # Fetch comment likes count
                cursor.execute(
                    "SELECT likes FROM Comment WHERE comment_id = %s",
                    [comment['comment_id']]
                )

                comment_likes_count = cursor.fetchone()[0]
                comment['likes'] = comment_likes_count

                # Check if the user has liked the comment
                user_has_liked_comment = False
                if request.user.is_authenticated:
                    cursor.execute(
                        "SELECT id FROM UserLike WHERE user_id = %s AND comment_id = %s AND like_type = 'comment'",
                        [request.user.id, comment['comment_id']]
                    )
                    if cursor.fetchone():
                        user_has_liked_comment = True

                cursor.execute(
                    "SELECT username FROM auth_user WHERE id = %s",
                    [comment['user_id']]
                )
                user_row = cursor.fetchone()
                if user_row:
                    comment['username'] = user_row[0]
                else:
                    comment['username'] = 'Unknown User'

                # Add this information to the comment dictionary
                comment['user_has_liked_comment'] = user_has_liked_comment
                comments.append(comment)

            context = {
                'question': question,
                'comments': comments,
                'user_has_liked_question': user_has_liked_question,
            }
            return render(request, 'brainstorm/question_detail.html', context)
        else:
            return redirect('portal')


@login_required
def add_comment(request, question_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        user_id = request.user.id
        creation_date = timezone.localtime(
            timezone.now()).strftime('%Y-%m-%d %H:%M:%S')

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Comment (question_id, user_id, comment_text, creation_date) "
                "VALUES (%s, %s, %s, %s)",
                [question_id, user_id, comment_text, creation_date]
            )

        return redirect('question_detail', question_id=question_id)


@login_required
def edit_comment(request, question_id, comment_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Comment SET comment_text = %s WHERE comment_id = %s",
                [comment_text, comment_id]
            )

        return redirect('question_detail', question_id=question_id)


@login_required
def delete_comment(request, question_id, comment_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM Comment WHERE comment_id = %s",
            [comment_id]
        )

    return redirect('question_detail', question_id=question_id)


@login_required
def like_question(request, question_id):
    user_id = request.user.id

    # Check if the user has already liked this question
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM UserLike WHERE user_id = %s AND question_id = %s AND like_type = 'question'",
            [user_id, question_id]
        )
        if cursor.fetchone():
            # The user has already liked this question, handle accordingly (e.g., display a message)
            pass
        else:
            # Get the current like count for the question
            cursor.execute(
                "SELECT likes FROM Question WHERE question_id = %s", [question_id])
            current_likes = cursor.fetchone()[0]

            # Increment the like count
            updated_likes = current_likes + 1

            # Perform the logic to increase the likes count for the question using raw SQL
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE Question SET likes = %s WHERE question_id = %s", [updated_likes, question_id])

                # Add the user's like to the UserLike table
                cursor.execute(
                    "INSERT INTO UserLike (user_id, question_id, like_type) VALUES (%s, %s, 'question')",
                    [user_id, question_id]
                )

    # Redirect back to the question detail page
    return redirect('question_detail', question_id=question_id)


@login_required
def like_comment(request, comment_id):
    user_id = request.user.id
    question_id = None

    # Check if the user has already liked this comment
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM UserLike WHERE user_id = %s AND comment_id = %s AND like_type = 'comment'",
            [user_id, comment_id]
        )
        if cursor.fetchone():
            # The user has already liked this comment, handle accordingly (e.g., display a message)
            cursor.execute(
                "SELECT question_id FROM Comment WHERE comment_id = %s", [comment_id])
            question_id = cursor.fetchone()[0]
            return redirect('question_detail', question_id=question_id)
        else:
            # Perform the logic to increase the likes count for the comment using raw SQL
            cursor.execute(
                "UPDATE Comment SET likes = likes + 1 WHERE comment_id = %s", [comment_id])

            # Add the user's like to the UserLike table
            cursor.execute(
                "INSERT INTO UserLike (user_id, comment_id, like_type) VALUES (%s, %s, 'comment')",
                [user_id, comment_id]
            )

            # Get the question_id for the comment before closing the cursor
            cursor.execute(
                "SELECT question_id FROM Comment WHERE comment_id = %s", [comment_id])
            question_id = cursor.fetchone()[0]

    # Redirect back to the question detail page
    if question_id is not None:
        return redirect('question_detail', question_id=question_id)
    else:
        # Handle the case where the question_id is not found (e.g., redirect to an error page)
        messages.error(request, _(
            "An error occurred. Please try again later."))
        return redirect('portal')

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import activate
from django.conf import settings


def index(request):
    LANGUAGES = settings.LANGUAGES
    context = {
        'LANGUAGES': LANGUAGES,
    }
    return render(request, 'brainstorm/index.html', context)


def home(request):
    LANGUAGES = settings.LANGUAGES
    context = {
        'LANGUAGES': LANGUAGES,
    }
    return render(request, 'brainstorm/index.html', context)


def qa_portal(request):
    LANGUAGES = settings.LANGUAGES
    context = {
        'LANGUAGES': LANGUAGES,
    }
    return render(request, 'brainstorm/index.html', context)


def contact(request):
    LANGUAGES = settings.LANGUAGES
    context = {
        'LANGUAGES': LANGUAGES,
    }
    return render(request, 'brainstorm/index.html', context)


def set_language(request, lang_code):
    if lang_code:
        activate(lang_code)
    return HttpResponseRedirect(reverse('index'))

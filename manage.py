#!/usr/bin/env python3
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ridgeworks.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Automatically create the .po files for all languages
    if len(sys.argv) > 1 and sys.argv[1] == 'makemessages':
        from django.conf import settings
        for lang_code, lang_name in settings.LANGUAGES:
            os.environ['DJANGO_SETTINGS_MODULE'] = 'ridgeworks.settings'
            os.environ['LANG'] = lang_code
            execute_from_command_line(
                ['manage.py', 'makemessages', '-l', lang_code])
        return

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

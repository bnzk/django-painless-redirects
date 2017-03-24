"""
These settings are used by the ``manage.py`` command.

Non south, django 1.7+ version.

"""
from .test_settings import *  # NOQA


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

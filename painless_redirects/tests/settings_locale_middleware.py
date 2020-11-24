from .settings import *  # noqa


MIDDLEWARE.insert(5, 'django.middleware.locale.LocaleMiddleware')
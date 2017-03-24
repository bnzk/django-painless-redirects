"""Settings that need to be set in order to run the tests."""
# may be not needed at all anymore
from .settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

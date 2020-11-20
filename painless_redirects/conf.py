from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

max_length_default = 1200

# auto create redirect to / when a 404 is detected
INDEXED_CHARFIELD_MAX_LENGTH = getattr(
    settings, 'PAINLESS_REDIRECTS_INDEXED_CHARFIELD_MAX_LENGTH', max_length_default
)

if not INDEXED_CHARFIELD_MAX_LENGTH == max_length_default:
    modules = getattr(settings, 'MIGRATION_MODULES', [])
    if 'painless_redirects' not in modules:
        raise ImproperlyConfigured(
            'You have a non default PAINLESS_REDIRECTS_INDEXED_CHARFIELD_MAX_LENGTH value'
            ' but not added painless_redirects to settings.MIGRATION_MODULES!'
        )


# auto create redirect to / when a 404 is detected
AUTO_CREATE = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE', True
)

# auto create redirect to / when a 404 is detected
REFERER_NONE_VALUE = getattr(
    settings, 'PAINLESS_REDIRECTS_REFERER_NONE_VALUE', '(no referer)'
)

# default url for created urls
AUTO_CREATE_TO_PATH = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE_TO_PATH', '/'
)

# insert current_site when auto creating
AUTO_CREATE_SITE = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE_SITE', True
)

# auto created redirects are enabled instantly! know what you do.
AUTO_CREATE_ENABLED = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE_ENABLED', False
)

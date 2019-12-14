from django.conf import settings


# auto create redirect to / when a 404 is detected
PAINLESS_REDIRECTS_AUTO_CREATE = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE', True
)

# default url for created urls
PAINLESS_REDIRECTS_AUTO_CREATE_TO_PATH = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE_TO_PATH', '/'
)

# insert current_site when auto creating
PAINLESS_REDIRECTS_AUTO_CREATE_SITE = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE_SITE', True
)

# auto created redirects are enabled instantly! know what you do.
PAINLESS_REDIRECTS_AUTO_CREATE_ENABLED = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE_ENABLED', False
)

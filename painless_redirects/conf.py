from django.conf import settings


PAINLESS_REDIRECTS_AUTO_CREATE = getattr(
    settings, 'PAINLESS_REDIRECTS_AUTO_CREATE', True
)

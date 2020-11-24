"""URLs to run the tests."""
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin


admin.autodiscover()

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
)

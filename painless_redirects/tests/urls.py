"""URLs to run the tests."""
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

urlpatterns = urlpatterns + i18n_patterns(
    url(r'^test/', TemplateView.as_view(template_name='test.html')),
    url(r'^test/no-slash', TemplateView.as_view(template_name='test_no_slash.html')),
)

"""Tests for the models of the painless_redirects app."""
from django.test import TestCase
from django.contrib.sites.models import Site
from mock import Mock

from . import factories
from ..models import Redirect
from ..middleware import ManualRedirectMiddleware

class ManualRedirectMiddlewareTestCase(TestCase):
    """
    request.get_current_site() is always the default example.com fixture
    """
    def setUp(self):
        self.middleware = ManualRedirectMiddleware()
        self.request = Mock()
        self.response = Mock()

    def test_no_404(self):
        obj = factories.RedirectFactory()
        self.request.path = obj.old_path
        self.response.status_code = 200
        self.assertEqual(
            self.middleware.process_response(self.request, self.response),
            self.response)

    def test_simple_redirect(self):
        obj = factories.RedirectFactory()
        self.response.status_code = 404
        self.request.path = obj.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_new_site_redirect(self):
        obj = factories.RedirectFactory()
        obj.new_site = factories.SiteFactory()
        obj.save()
        self.response.status_code = 404
        self.request.path = "/the-old-path/"
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.url, "%s%s" % (obj.new_site.domain, obj.new_path))

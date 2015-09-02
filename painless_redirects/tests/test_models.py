"""Tests for the models of the painless_redirects app."""
from django.test import TestCase

from . import factories


class RedirectModelTestCase(TestCase):

    def test_model(self):
        obj = factories.RedirectFactory()
        self.assertTrue(obj.pk)

    def test_redirect_value(self):
        obj = factories.RedirectFactory()
        self.assertEqual(obj.redirect_value(), "/the-new-path/")
        obj.new_site = factories.SiteFactory()
        self.assertEqual(obj.redirect_value(), "%s/the-new-path/" % obj.new_site.domain)

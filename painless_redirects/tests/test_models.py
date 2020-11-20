"""Tests for the models of the painless_redirects app."""
from django.contrib.sites.models import Site
from django.test import TestCase

from painless_redirects.models import Redirect


class RedirectModelTestCase(TestCase):

    def setUp(self):
        self.redirect = Redirect.objects.create(
            old_path="/the-old-path/",
            new_path="/the-new-path/",
        )
        self.site = Site.objects.create(
            name="example site 1",
            domain="example1.com",
        )

    def test_model(self):
        self.assertTrue(self.redirect.pk)

    def test_redirect_value(self):
        self.assertEqual(self.redirect.redirect_value('http'), "/the-new-path/")
        self.redirect.new_site = self.site
        self.assertEqual(self.redirect.redirect_value('https'), "https://%s/the-new-path/" % self.redirect.new_site.domain)

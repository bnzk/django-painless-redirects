"""Factories for the painless_redirects app."""
import factory
from django.contrib.sites.models import Site

from .. import models


class SiteFactory(factory.DjangoModelFactory):
    class Meta:
        model = Site

    name = "example site 1"
    domain = "example1.com"


class RedirectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Redirect

    old_path = "/the-old-path/"
    new_path = "/the-new-path/"

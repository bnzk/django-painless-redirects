# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


REDIRECT_TYPE_CHOICES = (
    (301, "Moved permanently"),
    (302, "Moved temporary"),
)


@python_2_unicode_compatible
class Redirect(models.Model):
    # max length note: mysql index cannot be more than 1000bytes, so with utf-8,
    # we can have no more than max_length=333 for old_path
    # creator = models.CharField(_(u'Creator'), max_length=128, blank=True)
    old_path = models.CharField(_(u'From path'), max_length=255,
        help_text=_("This should be an absolute path, excluding the domain name. Example: '/events/search/'."))
    wildcard_match = models.BooleanField(_(u'Wildcard mode'), default=False,
        help_text=_('Add wildcard (*) to from path'))
    site = models.ForeignKey(Site, null=True, blank=True,
        related_name="redirect_old_site",
        help_text=_('Optional, limit redirect to this site.'))
    domain = models.CharField(max_length=64, blank=True,
        help_text=_('Optional, exlicitly limit to specific domain.'))
    new_path = models.CharField(_(u'To path'), max_length=255,
        help_text=_('Absolute path, or full url (with http://.../).'))
    new_site = models.ForeignKey(Site, null=True, blank=True,
        related_name="redirect_new_site",
        help_text=_('Optional, automatically insert correct domain name of this site.'))
    # redirect_type = models.SmallIntegerField(
    #    choices=REDIRECT_TYPE_CHOICES, default=301,
    #    help_text=_(u"You know what you do, right? (If not: 301)"))
    # preserve_get = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Redirect"
        verbose_name_plural = "Redirects"
        unique_together = (('site', 'domain', 'old_path', ), )
        ordering = ('old_path', )

    def redirect_value(self, scheme):
        if self.new_site:
            return "%s://%s%s" % (scheme, self.new_site.domain, self.new_path)
        else:
            return self.new_path

    def __str__(self):
        wildcard = "*" if self.wildcard_match else ""
        if self.domain:
            return "%s%s%s ---> %s%s " % (
                self.domain, self.old_path, wildcard, self.new_site, self.new_path
            )
        else:
            return "%s%s%s ---> %s" % (
                getattr(self.site, "domain", ""), self.old_path, wildcard, self.redirect_value('http')
            )

# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site


REDIRECT_TYPE_CHOICES = (
    (301, "Moved permanently"),
    (302, "Moved temporary"),
)


class Redirect(models.Model):
    # max length note: mysql index cannot be more than 1000bytes, so with utf-8,
    # we can have no more than max_length=333 for old_path
    # creator = models.CharField(_(u'Creator'), max_length=128, blank=True)
    old_path = models.CharField(_(u'From path'), max_length=255,
        help_text=_("This should be an absolute path, excluding the domain name. Example: '/events/search/'."))
    wildcard_match = models.BooleanField(_(u'Wildcard mode'), default=False,
        help_text=_(u'Add wildcard (*) to from path'))
    site = models.ForeignKey(Site, null=True, blank=True,
        related_name="redirect_old_site",
        help_text=_(u'Optional, limit redirect to this site.'))
    domain = models.CharField(max_length=64, blank=True,
        help_text=_(u'Optional, exlicitly limit to specific domain.'))
    new_path = models.CharField(_(u'To path'), max_length=255,
        help_text=_(u'Absolute path, or full url (with http://.../).'))
    new_site = models.ForeignKey(Site, null=True, blank=True,
        related_name="redirect_new_site",
        help_text=_(u'Optional, automatically insert correct domain name of this site.'))
    # redirect_type = models.SmallIntegerField(
    #    choices=REDIRECT_TYPE_CHOICES, default=301,
    #    help_text=_(u"You know what you do, right? (If not: 301)"))
    # preserve_get = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Redirect"
        verbose_name_plural = "Redirects"
        unique_together = (('site', 'domain', 'old_path', ), )
        ordering = ('old_path', )

    def redirect_value(self):
        if self.new_site:
            return u"%s%s" % (self.new_site.domain, self.new_path)
        else:
            return self.new_path

    def __unicode__(self):
        wildcard = "*" if self.wildcard_match else ""
        if self.domain:
            return u"%s%s%s ---> %s%s " % (
                self.domain, self.old_path, wildcard, self.new_site, self.new_path
            )
        else:
            return u"%s%s%s ---> %s" % (
                getattr(self.site, "domain", ""), self.old_path, wildcard, self.redirect_value()
            )

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
    permanent = models.BooleanField(
        default=True,
        verbose_name=_(u'Permanent redirect (301)'),
        help_text=_("For temporary fixes, uncheck to use a status code of 302"),
    )
    old_path = models.CharField(_(u'From path'), max_length=255,
        help_text=_("Absolute path, excluding the domain name. Example: '/events/search/'"))
    wildcard_match = models.BooleanField(
        default=False,
        verbose_name=_(u'Wildcard match'),
        help_text=_('Add wildcard (/from/path/*)'),
    )
    # too complicated to implement for now!
    # querystring_match = models.BooleanField(
    #     default=False,
    #     verbose_name=_(u'Querystring match'),
    #     help_text=_('Considers ?search=whatever when mathing)'),
    # )
    site = models.ForeignKey(
        Site,
        null=True,
        on_delete=models.CASCADE,
        blank=True,
        related_name="redirect_old_site",
        help_text=_('Optional, limit redirect to this site'),
    )
    domain = models.CharField(max_length=64, blank=True, default='',
        help_text=_('Optional, exlicitly limit to specific domain'))
    new_path = models.CharField(_(u'To path'), max_length=255,
        help_text=_('Absolute path, or full url (with http://.../)'))
    keep_tree = models.BooleanField(
        default=False,
        verbose_name=_("Keep tree"),
        help_text=_("Only applies when wildcard matching enabled"),
    )
    keep_querystring = models.BooleanField(
        default=False,
        verbose_name=_("Keep querystring"),
        help_text=_("Re-applies GET querystring, if any (?page=4&search=banana)"),
   )
    new_site = models.ForeignKey(
        Site,
        null=True,
        on_delete=models.CASCADE,
        blank=True,
        related_name="redirect_new_site",
        help_text=_('Optional, automatically insert correct domain name of this site'),
    )
    # redirect_type = models.SmallIntegerField(
    #    choices=REDIRECT_TYPE_CHOICES, default=301,
    #    help_text=_(u"You know what you do, right? (If not: 301)"))
    # preserve_get = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Redirect"
        verbose_name_plural = "Redirects"
        unique_together = (('site', 'domain', 'old_path', ), )
        ordering = ('old_path', )

    def redirect_value(self, scheme, right_path='', querystring=''):
        if self.new_site:
            url = "%s://%s%s" % (scheme, self.new_site.domain, self.new_path)
        else:
            url = self.new_path
        if right_path and self.keep_tree:
            url = '{}{}'.format(url, right_path)
        if querystring and self.keep_querystring:
            url = '{}?{}'.format(url, querystring)
        return url

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

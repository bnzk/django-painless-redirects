# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from painless_redirects import conf

try:
    from django.utils.encoding import python_2_unicode_compatible
except ImportError:
    def python_2_unicode_compatible(f):
        return f

from painless_redirects.managers import RedirectQuerySet

REDIRECT_TYPE_CHOICES = (
    (301, "Moved permanently"),
    (302, "Moved temporary"),
)


@python_2_unicode_compatible
class RedirectHit(models.Model):
    redirect = models.ForeignKey(
        'painless_redirects.Redirect',
        on_delete=models.CASCADE,
    )
    referrer = models.CharField(
        _(u'Referrer'),
        # check https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
        max_length=conf.INDEXED_CHARFIELD_MAX_LENGTH,
        help_text=_("Where the hit comes from")
    )
    hits = models.PositiveIntegerField(
        default=0,
        editable=False,
    )

    def __str__(self):
        return '{} from {}'.format(self.count, self.referrer)


@python_2_unicode_compatible
class Redirect(models.Model):
    enabled = models.BooleanField(
        default=True,
        verbose_name=_(u'Enabled'),
        help_text=_("Shall this redirect be effectivly used?"),
    )
    auto_created = models.BooleanField(
        default=False,
        verbose_name=_(u'Auto created'),
        help_text=_("Created by a 404 hit? (must be enabled via settings)"),
        editable=False,
    )
    hits = models.IntegerField(
        default=0,
        editable=False,
    )
    permanent = models.BooleanField(
        default=True,
        verbose_name=_(u'Permanent redirect (301)'),
        help_text=_("For temporary fixes, uncheck to use a status code of 302"),
    )
    # max length note: mysql index cannot be more than 307Xbytes, so with utf-8,
    # we can have no more than max_length around 800 for old_path
    old_path = models.CharField(
        _(u'From path'),
        # check https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
        max_length=conf.INDEXED_CHARFIELD_MAX_LENGTH,
        help_text=_("Absolute path, excluding the domain name. Example: '/events/search/'")
    )
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
    domain = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text=_('Optional, exlicitly limit to specific domain'),
    )
    new_path = models.CharField(
        _(u'To path'),
        max_length=255,
        help_text=_('Absolute path, or full url (with http://.../)'),
    )
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

    objects = RedirectQuerySet.as_manager()

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
            return "%s%s%s ---> %s " % (
                self.domain, self.old_path, wildcard, self.redirect_value('http')
            )
        else:
            return "%s%s%s ---> %s" % (
                getattr(self.site, "domain", ""), self.old_path, wildcard, self.redirect_value('http')
            )

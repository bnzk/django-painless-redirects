from django.db import models
from django.contrib.sites.models import Site
from django.db.models import Sum
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
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
    referer = models.CharField(
        _(u'Referer'),
        # check https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
        max_length=conf.INDEXED_CHARFIELD_MAX_LENGTH,
        help_text=_("Where the hit comes from (ie refering url")
    )
    hits = models.PositiveIntegerField(
        default=0,
        editable=False,
    )
    last_hit = models.DateTimeField(
        blank=True,
        null=True,
        auto_now=True,
        help_text='The last time the URL/Redirect was hit, from this referer.'
    )

    class Meta:
        ordering = ('-hits',)
        unique_together = ('redirect', 'referer')

    def __str__(self):
        return '{}x from {}'.format(self.hits, self.referer)


@python_2_unicode_compatible
class Redirect(models.Model):
    enabled = models.BooleanField(
        default=True,
        verbose_name=_(u'Enabled'),
        help_text=_("Shall this redirect be effectivly used?"),
    )
    ignored = models.BooleanField(
        default=False,
        verbose_name=_(u'Ignored'),
        help_text=_("Shall this redirect be ignored? (use to tighen/cleanup your redirects list)"),
    )
    auto_created = models.BooleanField(
        default=False,
        verbose_name=_(u'Auto created'),
        help_text=_("Created by a 404 hit? (must be enabled via settings)"),
        editable=False,
    )
    permanent = models.BooleanField(
        default=True,
        verbose_name=_(u'Permanent'),
        help_text=_("Use status code 301. For temporary fixes, uncheck to use a status code of 302"),
    )
    # max length note: mysql index cannot be more than 307Xbytes, so with utf-8,
    # we can have no more than max_length around 800 for old_path
    old_path = models.CharField(
        _(u'From path'),
        # check https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
        max_length=conf.INDEXED_CHARFIELD_MAX_LENGTH,
        db_index=True,
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
    # )total_hits
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

    def total_hits(self):
        qs = self.redirecthit_set.all().aggregate(total_hits=Sum('hits'))
        return qs['total_hits']
    total_hits.admin_order_field = 'total_hits'

    def old_loc_display_data(self):
        path = self.old_path
        if self.domain:
            loc = "%s%s" % (
                self.domain, path
            )
            loc_link = loc
            if not self.domain.startswith('http'):
                loc_link = 'http://{}'.format(loc)
        else:
            loc = "%s%s" % (
                getattr(self.site, "domain", ""), path
            )
            loc_link = loc
            if getattr(self.site, "domain", None):
                loc_link = 'http://{}'.format(loc)
        if self.wildcard_match:
            loc += "*"
        return truncatechars(loc, 50), loc_link

    def old_loc(self):
        loc, loc_link = self.old_loc_display_data()
        loc = format_html(
            ' <a href="{}">{}</a> (<a href="{}" target="_blank">check</a>)',
            reverse('admin:painless_redirects_redirect_change', args=(self.id, ), ),
            loc,
            loc_link,
        )
        return mark_safe(loc)
    old_loc.short_description = 'From'

    def new_loc_display_data(self):
        loc = self.redirect_value('http')
        loc_link = loc
        # redirect_value has http covered
        # if getattr(self.new_site, "domain", None):
        #     loc_link = 'http://{}'.format(loc)
        if self.keep_tree:
            loc += '/' if not loc.endswith('/') else ''
            loc += "keep-wildcard/"
        if self.keep_querystring:
            loc += "?keep=query"
        return loc, loc_link

    def new_loc(self):
        loc, loc_link = self.new_loc_display_data()
        loc = format_html(
            '<a href="{}" target="_blank">{}</a>',
            loc_link,
            loc,
        )
        return mark_safe(loc)
    new_loc.short_description = 'To'

    def __str__(self):
        old_loc, old_loc_link = self.old_loc_display_data()
        new_loc, new_loc_link = self.new_loc_display_data()
        return '{} ---> {}'.format(old_loc, new_loc)

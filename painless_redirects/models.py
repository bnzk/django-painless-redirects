# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site


class Redirect(models.Model):
    site = models.ForeignKey(Site, null=True, blank=True,
        related_name="redirect_old_site",
        help_text=_(u'Optional, limit redirect to this site.'))
    domain = models.CharField(max_length=1024, blank=True,
        help_text=_(u'Optional, exlicitly limit to specific domain.'))
    old_path = models.CharField(_(u'From'), max_length=1024, db_index=True,
        help_text=_("This should be an absolute path, excluding the domain name. Example: '/events/search/'."))
    new_path = models.CharField(_(u'To'), max_length=1024,
        help_text=_(u'Absolute path, or full url (with http://.../).'))
    new_site = models.ForeignKey(Site, null=True, blank=True,
        related_name="redirect_new_site",
        help_text=_(u'Optional, automatically insert correct domain name of this site.'))

    def redirect_value(self):
        if self.new_site:
            return u"%s%s" % (self.new_site.domain, self.new_path)
        else:
            return self.new_path

    def __unicode__(self):
        if self.domain:
            return u"%s%s ---> %s%s " % (
                self.domain, self.old_path, self.new_site, self.new_path
            )
        else:
            return u"%s%s ---> %s%s" % (
                self.site, self.old_path, self.new_site, self.new_path
            )

    class Meta:
        verbose_name = "Redirect"
        verbose_name_plural = "Redirects"

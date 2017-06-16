# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models


class RedirectAdmin(admin.ModelAdmin):
    search_fields = ['old_path', 'domain', 'new_path', ]
    list_filter = ['site', 'domain', 'new_site', 'wildcard_match', ]
    fieldsets = (
        (_('From'), {
            'fields': ('old_path', 'wildcard_match', 'site', 'domain', ),
        }),
        (_('To'), {
            'fields': ('new_path', 'new_site')
        }),
    )

admin.site.register(models.Redirect, RedirectAdmin)

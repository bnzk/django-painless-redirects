# coding: utf-8
from django.contrib import admin

from . import models


class RedirectAdmin(admin.ModelAdmin):
    search_fields = ['old_path', 'domain', 'new_path', ]
    list_filter = ['site', 'domain', 'new_site', 'wildcard_match', ]

admin.site.register(models.Redirect, RedirectAdmin)

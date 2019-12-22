# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models


@admin.register(models.Redirect)
class RedirectAdmin(admin.ModelAdmin):
    search_fields = ['old_path', 'domain', 'new_path', ]
    list_display = ('__str__', 'hits', 'enabled', )
    list_filter = [
        'enabled',
        'auto_created',
        'wildcard_match',
        'site',
        'new_site',
        'domain',
    ]
    readonly_fields = ['auto_created', 'hits', ]
    fieldsets = (
        ('', {
            'fields': (('enabled', 'auto_created', 'hits', ), ),
        }),
        (_('From'), {
            'fields': (('old_path', 'wildcard_match', ), 'site', 'domain', ),
        }),
        (_('To'), {
            'fields': ('new_path', ('keep_tree', 'keep_querystring', ), 'new_site', 'permanent', )
        }),
    )

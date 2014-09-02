# coding: utf-8
from django.contrib import admin

from . import models


class RedirectAdmin(admin.ModelAdmin):
    search_fields = ['old_path', 'domain', 'new_path', ]

admin.site.register(models.Redirect, RedirectAdmin)

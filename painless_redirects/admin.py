# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Redirect


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    search_fields = ['old_path', 'domain', 'new_path', ]
    list_display = ('__str__', 'hits', 'enabled', 'auto_created',)
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

    actions = [
        'remove_disabled_auto_created',
        'remove_all_auto_created',
    ]

    # https://stackoverflow.com/a/24799844/1029469
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] in self.actions:
            if not request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Redirect.objects.all()[:10]:
                    post.update({admin.ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super().changelist_view(request, extra_context)

    def remove_disabled_auto_created(self, request, queryset):
        Redirect.objects.filter(auto_created=True, enabled=False, ).delete()
    remove_disabled_auto_created.short_description = "Remove auto created that are disabled"

    def remove_all_auto_created(self, request, queryset):
        Redirect.objects.filter(auto_created=True, ).delete()
    remove_all_auto_created.short_description = "Remove all auto created"

from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from .models import Redirect, RedirectHit


class RedirectHitInline(admin.TabularInline):
    model = RedirectHit
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return ['referer', 'hits', 'last_hit']


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    search_fields = ['old_path', 'domain', 'new_path', ]
    list_display_links = []
    list_display = ('old_loc', 'new_path', 'total_hits', 'enabled', 'permanent', 'ignored', 'auto_created',)
    list_editable = ('enabled', 'ignored', 'new_path', 'permanent')
    list_filter = [
        'enabled',
        'auto_created',
        'wildcard_match',
        'ignored',
        'permanent',
        'site',
        'new_site',
        'domain',
    ]
    readonly_fields = ['auto_created', 'total_hits', ]
    fieldsets = (
        ('', {
            'fields': (('enabled', 'auto_created', 'ignored', ), ),
        }),
        (_('From'), {
            'fields': (('old_path', 'wildcard_match', ), 'site', 'domain', ),
        }),
        (_('To'), {
            'fields': ('new_path', ('keep_tree', 'keep_querystring', ), 'new_site', 'permanent', )
        }),
    )
    inlines = [RedirectHitInline, ]

    actions = [
        'set_ignored',
        'remove_disabled_auto_created',
        'remove_all_auto_created',
        'remove_all_ignored',
    ]

    # def get_sortable_by(self, request):
    #     by = super().get_sortable_by(request)
    #     by = list(by)
    #     by.append('hits')
    #     return by

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(total_hits=Sum('redirecthit__hits'))
        return qs

    # https://stackoverflow.com/a/24799844/1029469
    def changelist_view(self, request=None, extra_context=None):
        if 'action' in request.POST and request.POST['action'] in self.actions:
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Redirect.objects.all()[:10]:
                    post.update({ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super().changelist_view(request, extra_context)

    def set_ignored(self, request, queryset):
        queryset.update(ignored=True)
    set_ignored.short_description = "Ignore selected"

    def remove_disabled_auto_created(self, request, queryset):
        Redirect.objects.filter(auto_created=True, enabled=False, ).delete()
    remove_disabled_auto_created.short_description = "Remove auto created that are disabled"

    def remove_all_auto_created(self, request, queryset):
        Redirect.objects.filter(auto_created=True, ).delete()
    remove_all_auto_created.short_description = "Remove all auto created"

    def remove_all_ignored(self, request, queryset):
        Redirect.objects.filter(ignored=True, ).delete()
    remove_all_ignored.short_description = "Remove all ignored"

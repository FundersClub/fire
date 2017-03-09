from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import (
    format_html,
    format_html_join,
)

from fb_github.models import Repository


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'created_at',
        'status',
        'email_slug',
        'num_email_maps',
        'num_issues',
    )
    fields = (
        ('login', 'name'),
        'status',
        'email_slug',
        ('created_at', 'approved_at'),
        'admins_display',
        'uuid',
        'inviter_login',
        'num_email_maps',
        'num_issues',
    )
    readonly_fields = [f.name for f in Repository._meta.fields] + [
        'admins_display',
        'num_email_maps',
        'num_issues',
    ]

    def get_queryset(self, request):
        return (super().get_queryset(request)
            .annotate(
                num_email_maps=Count('emailmap', distinct=True),
                num_issues=Count('issue', distinct=True),
            )
            .prefetch_related('admins')
        )

    def num_email_maps(self, obj):
        return obj.num_email_maps

    def num_issues(self, obj):
        return obj.num_issues

    def admins_display(self, obj):
        return format_html(
            '<ul>{}</ul>',
            format_html_join(
                '',
                '<li><a href="{}">{}</a></li>',
                ((reverse('admin:auth_user_change', args=[u.id]), u.username) for u in obj.admins.all()),
            )
        )

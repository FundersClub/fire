from django import template
from django.utils.html import format_html


register = template.Library()


@register.filter
def github_profile(login):
    return format_html(
        '<a href="https://github.com/{0}">@{0}</a>',
        login,
    )

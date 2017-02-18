from django.contrib import admin

from fb_github.models import Repository


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    pass

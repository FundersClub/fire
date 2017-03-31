from django.core.management.base import BaseCommand

from fb_github.models import Repository


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('from_repo', type=str)
        parser.add_argument('to_repo', type=str)

    def handle(self, *args, **options):
        from_repo_login, from_repo_name = options['from_repo'].split('/')
        to_repo_login, to_repo_name = options['to_repo'].split('/')

        from_repo = Repository.objects.get(login=from_repo_login, name=from_repo_name)
        to_repo = Repository.objects.get(login=to_repo_login, name=to_repo_name)

        for entry in from_repo.emailmap_set.all():
            to_repo.emailmap_set.get_or_create(
                email=entry.email,
                defaults={
                    'login': entry.login,
                    'user': entry.user,
                },
            )

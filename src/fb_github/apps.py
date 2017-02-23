from django.apps import AppConfig


class FbGithubConfig(AppConfig):
    name = 'fb_github'

    def ready(self):
        import fb_github.signalhandlers  # noqa

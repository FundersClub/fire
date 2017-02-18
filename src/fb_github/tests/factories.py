import factory

from django.utils import timezone

from fb_github import models


class RepositoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Repository

    inviter_login = factory.Sequence(lambda n: 'inviter{}'.format(n))
    login = factory.Sequence(lambda n: 'login{}'.format(n))
    name = factory.Sequence(lambda n: 'name{}'.format(n))
    original_invitation_data = {}
    status = models.Repository.Status.Active

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if kwargs['status'] == models.Repository.Status.Active:
            kwargs.setdefault('approved_at', timezone.now())

        return super(RepositoryFactory, cls)._create(model_class, *args, **kwargs)

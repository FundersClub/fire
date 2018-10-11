import factory

from django.contrib.auth import get_user_model


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = factory.Faker('name')
    last_name = factory.Faker('name')
    email = factory.Faker('email')

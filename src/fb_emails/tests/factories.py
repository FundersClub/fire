import factory

from django.conf import settings

from fb_emails import models


class IncomingMessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.IncomingMessage

    body_html = ''
    body_text = factory.Faker('text')
    from_email = factory.Faker('email')
    from_name = factory.Faker('name')
    original_post_data = {}
    subject = factory.Faker('sentence')
    to_email = 'fake@{}'.format(settings.EMAIL_DOMAIN)

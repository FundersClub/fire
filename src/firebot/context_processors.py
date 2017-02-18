from django.conf import settings


def firebot_context_processor(request):
    return {
        'settings': settings,
    }

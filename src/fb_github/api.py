from django.conf import settings
from django.conf.urls import (
    include,
    url,
)

from rest_framework import (
    permissions,
    routers,
    serializers,
)
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from fb_github import models
from firebot.api import BaseSerializer


################################################################################
# Serializers
################################################################################

class EmailMapSerializer(BaseSerializer):
    class Meta:
        model = models.EmailMap
        fields = (
            'email',
            'login',
            'repo',
            'url',
        )


class RepositorySerializer(serializers.HyperlinkedModelSerializer):
    emailmap_set = EmailMapSerializer(many=True, read_only=True)

    class Meta:
        model = models.Repository
        fields = (
            'emailmap_set',
            'email_slug',
            'login',
            'name',
            'status',
            'url',
        )
        read_only_fields = [f for f in fields if f != 'email_slug']
        extra_kwargs = {
            'email_slug': {
                'required': True,
            },
        }

    def validate_email_slug(self, value):
        if value in settings.FIREBOT_BANNED_EMAIL_SLUGS:
            raise serializers.ValidationError('"{}" is not permitted.'.format(value))
        return value


################################################################################
# Viewsets
################################################################################

class EmailMapViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    queryset = models.EmailMap.objects.all()
    serializer_class = EmailMapSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return (super(EmailMapViewSet, self).get_queryset()
            .filter(repo__admins=self.request.user)
        )


class RepositoryViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    queryset = models.Repository.objects.all()
    serializer_class = RepositorySerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return (super(RepositoryViewSet, self).get_queryset()
            .filter(admins=self.request.user)
        )


################################################################################
# Views
################################################################################

class MeView(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated():
            resp = {
                'is_authenticated': False,
            }
        else:
            resp = {
                'repositories': RepositoryViewSet.as_view({'get': 'list'})(request).data,
                'username': request.user.username,
                'is_authenticated': True,
                'urls': {
                    'logout': reverse('account_logout', request=request),
                },
            }
        return Response(resp)


################################################################################
# Router
################################################################################

router = routers.DefaultRouter()

router.register('email-map', EmailMapViewSet)
router.register('repository', RepositoryViewSet)

urlpatterns = [
    url(r'^me/$', MeView.as_view(), name='fb-github-me'),
    url(r'^', include(router.urls)),
]

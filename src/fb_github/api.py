from django.conf import settings
from django.conf.urls import (
    include,
    url,
)

from rest_framework import (
    permissions,
    routers,
    serializers,
    status,
)
from rest_framework.decorators import detail_route
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

from fb_emails import models as fb_emails_models
from fb_github import models
from firebot.api import BaseSerializer


################################################################################
# Serializers
################################################################################

class EmailMapSerializer(BaseSerializer):
    login = serializers.SlugField()

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
    urls = serializers.SerializerMethodField()

    class Meta:
        model = models.Repository
        fields = (
            'emailmap_set',
            'email',
            'email_slug',
            'full_name',
            'gh_url',
            'login',
            'name',
            'status',
            'url',
            'urls',
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

    def get_urls(self, obj):
        return {
            'purge_attachments': reverse('repository-purge-attachments', args=[obj.pk], request=self.context['request']),
        }


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

    @detail_route(methods=['post'])
    def purge_attachments(self, request, pk=None):
        repo = self.get_object()

        qs = fb_emails_models.Attachment.objects.filter(
            msg__issue__repo=repo
        )
        for attachment in qs.iterator():
            attachment.file.delete()
            attachment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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

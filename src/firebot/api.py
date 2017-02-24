from rest_framework import serializers

from fb_github.models import Repository


class BaseHyperlinkRelatedField(serializers.HyperlinkedRelatedField):
    """Override HyperlinkedRelatedField to only let the user access objects
    they can access.

    Currently the filters map is hardcoded here, but in the future we might change it
    so that every app can contribute it's models here, or implement a `for_user`
    filter on it's queryset.
    """

    def get_queryset(self):
        user = self.context['request'].user
        qs = super(BaseHyperlinkRelatedField, self).get_queryset()
        filters = {
            Repository: {
                'admins': user,
            },
        }.get(qs.model)
        assert filters is not None, 'No filters set for related model {}'.format(qs.model)
        return qs.filter(**filters)


class BaseSerializer(serializers.HyperlinkedModelSerializer):
    serializer_related_field = BaseHyperlinkRelatedField

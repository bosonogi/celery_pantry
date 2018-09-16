from rest_framework import serializers
from rest_framework.settings import api_settings

from celery_pantry import models


class TaskSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Task
        fields = (
            api_settings.URL_FIELD_NAME,
            'id',
            'first_saved',
            'data',
        )
        extra_kwargs = {
            api_settings.URL_FIELD_NAME: {'lookup_field': 'id'}
        }

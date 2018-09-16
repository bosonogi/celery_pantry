from rest_framework import viewsets

from celery_pantry import models, serializers


class TaskViewSet(viewsets.ReadOnlyModelViewSet):

    """Celery Tasks"""

    queryset = models.Task.objects.all().order_by('-first_saved')
    serializer_class = serializers.TaskSerializer
    lookup_field = 'id'

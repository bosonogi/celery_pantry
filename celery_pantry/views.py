import os
import json

import coreapi
import coreschema
from django.template import loader
from rest_framework import viewsets, filters
from rest_framework.filters import OrderingFilter

from celery_pantry import models, serializers


class TasksFilter(filters.BaseFilterBackend):

    """Return tasks that satisfy given constraints"""

    template = os.path.join('celery_pantry', 'tasks_filter.html')
    schema = [
        coreapi.Field(
            name='with_data',
            required=False,
            location='query',
            schema=coreschema.Object(
                description='Data users must have',
                min_properties=1
            )
        ),
        coreapi.Field(
            name='without_data',
            required=False,
            location='query',
            schema=coreschema.Object(
                description='Data users must not have',
                min_properties=1
            )
        ),
    ]

    @staticmethod
    def _filter__with_data(queryset, value):
        return queryset.filter(data__contains=json.loads(value))

    @staticmethod
    def _filter__without_data(queryset, value):
        return queryset.exclude(data__contains=json.loads(value))

    def filter_queryset(self, request, queryset, view):
        if view.action == 'list':
            for key, value in request.query_params.items():
                if value:
                    try:
                        filter_func = getattr(self, f'_filter__{key}')
                        queryset = filter_func(queryset, value)
                    except AttributeError:
                        continue
        return queryset

    def to_html(self, request, queryset, view) -> str:
        template = loader.get_template(self.template)
        context = self.get_template_context(request)
        return template.render(context)

    def get_template_context(self, request):
        return dict(conditions={
            field.name: request.query_params.get(field.name, '')
            for field in self.schema
        })


class TaskViewSet(viewsets.ReadOnlyModelViewSet):

    """Celery Tasks"""

    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    lookup_field = 'id'
    lookup_value_regex = '[a-z0-9._-]+'
    filter_backends = (OrderingFilter, TasksFilter)
    ordering_fields = ('first_saved',)
    ordering = ('-first_saved',)

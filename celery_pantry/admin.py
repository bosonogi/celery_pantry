from django.contrib import admin
from django.contrib.admin import ModelAdmin

from celery_pantry import models


class TaskAdmin(ModelAdmin):

    """Read-only access to Task objects from admin panel"""

    readonly_fields = ('id', 'data')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.Task, TaskAdmin)

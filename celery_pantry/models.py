from django.db import models
from django.contrib.postgres import fields, indexes


class Task(models.Model):

    """Celery task information"""

    class Meta:
        indexes = [
            indexes.GinIndex(fields=['data']),
        ]

    id = models.CharField(max_length=512, primary_key=True,
                          help_text='Task ID')
    first_saved = models.DateTimeField(auto_now_add=True, db_index=True)
    data = fields.JSONField(blank=True, help_text='Task data')

    def __str__(self):
        return 'Task {}'.format(self.id)

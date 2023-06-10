from django.db import models


class DynamicModel(models.Model):
    title = models.CharField(max_length=255)
    fields = models.JSONField()

    def __str__(self):
        return self.title

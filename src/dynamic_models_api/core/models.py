from django.db import models


class DynamicModel(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    fields = models.JSONField(default=list)

    def __str__(self):
        return self.name

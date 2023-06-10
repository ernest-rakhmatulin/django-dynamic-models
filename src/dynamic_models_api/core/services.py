from django.db import models, migrations


class DynamicModelService:

    fields_map = {
        'string': {
            'class': models.TextField,
        },
        'number': {
            'class': models.FloatField,
        },
        'boolean': {
            'class': models.BooleanField,
        },
    }

    @staticmethod
    def get_choices():
        return list(DynamicModelService.fields_map.keys())

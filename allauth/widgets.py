import json
from django.core.serializers import serialize, deserialize, json as jsonserializer
from django.db.models.query import QuerySet
from django.db import models
from django.forms.widgets import Textarea


class DjangoJSONEncoder(jsonserializer.DjangoJSONEncoder):
    """
        Version of DjangoJSONEncoder that knows how to encode embedded QuerySets or Models.
    """
    def default(self, obj):
        if isinstance(obj, QuerySet):
            return serialize('python', obj)
        if isinstance(obj, models.Model):
            return serialize('python', [obj])[0]
        return super(DjangoJSONEncoder, self).default(obj)


def deserialize_model(obj):
    if 'model' in obj and 'pk' in obj:
        obj = list(deserialize('python', [obj]))[0].object
    return obj


class SerializedObjectWidget(Textarea):
    def render(self, name, value, attrs=None):
        value = json.dumps(value, indent=2, cls=DjangoJSONEncoder)
        return super(SerializedObjectWidget, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        val = data.get(name, None)
        if not val:
            return None
        return json.loads(val, object_hook=deserialize_model)

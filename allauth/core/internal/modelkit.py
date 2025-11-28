import base64
import json

from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import FileField
from django.db.models.fields import BinaryField, DateField, DateTimeField, TimeField
from django.utils import dateparse
from django.utils.encoding import force_bytes, force_str


SERIALIZED_DB_FIELD_PREFIX = "_db_"


def serialize_instance(instance):
    """
    Since Django 1.6 items added to the session are no longer pickled,
    but JSON encoded by default. We are storing partially complete models
    in the session (user, account, token, ...). We cannot use standard
    Django serialization, as these are models are not "complete" yet.
    Serialization will start complaining about missing relations et al.
    """
    data = {}
    for k, v in instance.__dict__.items():
        if k.startswith("_") or callable(v):
            continue
        try:
            field = instance._meta.get_field(k)
            if isinstance(field, BinaryField):
                if v is not None:
                    v = force_str(base64.b64encode(v))
            elif isinstance(field, FileField):
                if v and not isinstance(v, str):
                    v = {
                        "name": v.name,
                        "content": base64.b64encode(v.read()).decode("ascii"),
                    }
            # Check if the field is serializable. If not, we'll fall back
            # to serializing the DB values which should cover most use cases.
            try:
                json.dumps(v, cls=DjangoJSONEncoder)
            except TypeError:
                v = field.get_prep_value(v)
                k = SERIALIZED_DB_FIELD_PREFIX + k
        except FieldDoesNotExist:
            pass
        data[k] = v
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def deserialize_instance(model, data):
    if not isinstance(data, dict):
        raise ValueError()
    ret = model()
    for k, v in data.items():
        is_db_value = False
        if k.startswith(SERIALIZED_DB_FIELD_PREFIX):
            k = k[len(SERIALIZED_DB_FIELD_PREFIX) :]
            is_db_value = True
        if v is not None:
            try:
                f = model._meta.get_field(k)
                if isinstance(f, DateTimeField):
                    v = dateparse.parse_datetime(v)
                elif isinstance(f, TimeField):
                    v = dateparse.parse_time(v)
                elif isinstance(f, DateField):
                    v = dateparse.parse_date(v)
                elif isinstance(f, BinaryField):
                    v = force_bytes(base64.b64decode(force_bytes(v)))
                elif isinstance(f, FileField):
                    if isinstance(v, dict):
                        v = ContentFile(base64.b64decode(v["content"]), name=v["name"])
                elif is_db_value:
                    try:
                        # This is quite an ugly hack, but will cover most
                        # use cases...
                        # The signature of `from_db_value` changed in Django 3
                        # https://docs.djangoproject.com/en/3.0/releases/3.0/#features-removed-in-3-0
                        v = f.from_db_value(v, None, None)
                    except Exception:
                        raise ImproperlyConfigured(
                            f"Unable to auto serialize field '{k}', custom serialization override required"
                        )
            except FieldDoesNotExist:
                pass
        setattr(ret, k, v)
    return ret

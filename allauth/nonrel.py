
try:
    from django.forms import Field
    from djangotoolbox.fields import ListField, DictField, AbstractIterableField
    from .widgets import SerializedObjectWidget

    class ListFieldWithForm(ListField):
        def formfield(self, **kwargs):
            defaults = {'form_class': Field, 'widget': SerializedObjectWidget}
            defaults.update(kwargs)
            return super(AbstractIterableField, self).formfield(**defaults)

    class DictFieldWithForm(DictField, Field):
        def formfield(self, **kwargs):
            defaults = {'form_class': Field, 'widget': SerializedObjectWidget}
            defaults.update(kwargs)
            return super(AbstractIterableField, self).formfield(**defaults)
except ImportError:
    pass

from django.conf import settings
db_engine = settings.DATABASES['default']['ENGINE']

non_rel = (db_engine == 'django_mongodb_engine')

try:
    from django.forms import Field
    from djangotoolbox.fields import EmbeddedModelField, ListField, DictField, AbstractIterableField
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

    non_rel = True
except ImportError:
    non_rel = False

import importlib
from collections import OrderedDict

from django.apps import apps
from django.conf import settings

from allauth.utils import import_attribute


class ProviderRegistry:
    def __init__(self):
        self.provider_map = OrderedDict()
        self.loaded = False

    def get_class_list(self):
        self.load()
        return list(self.provider_map.values())

    def register(self, cls):
        self.provider_map[cls.id] = cls

    def get_class(self, id):
        return self.provider_map.get(id)

    def as_choices(self):
        self.load()
        for provider_cls in self.provider_map.values():
            yield (provider_cls.id, provider_cls.name)

    def load(self):
        # TODO: Providers register with the provider registry when
        # loaded. Here, we build the URLs for all registered providers. So, we
        # really need to be sure all providers did register, which is why we're
        # forcefully importing the `provider` modules here. The overall
        # mechanism is way to magical and depends on the import order et al, so
        # all of this really needs to be revisited.
        if not self.loaded:
            for app_config in apps.get_app_configs():
                try:
                    module_name = app_config.name + ".provider"
                    provider_module = importlib.import_module(module_name)
                except ImportError as e:
                    if e.name != module_name:
                        raise
                else:
                    provider_settings = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
                    for cls in getattr(provider_module, "provider_classes", []):
                        provider_class = provider_settings.get(cls.id, {}).get(
                            "provider_class"
                        )
                        if provider_class:
                            cls = import_attribute(provider_class)
                        self.register(cls)
            self.loaded = True


registry = ProviderRegistry()

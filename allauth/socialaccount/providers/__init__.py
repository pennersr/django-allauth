from django.conf import settings
from django.utils import importlib

class ProviderRegistry(object):
    def __init__(self):
        self.provider_map = {}
        self.loaded = False

    def get_list(self):
        self.load()
        return self.provider_map.values()

    def register(self, cls):
        self.provider_map[cls.id] = cls()

    def by_id(self, id):
        self.load()
        return self.provider_map[id]

    def as_choices(self):
        self.load()
        for provider in self.get_list():
            yield (provider.id, provider.name)

    def load(self):
        if not self.loaded:
            for app in settings.INSTALLED_APPS:
                provider_module = app + '.provider'
                try:
                    importlib.import_module(provider_module)
                except ImportError:
                    pass
            self.loaded = True

registry = ProviderRegistry()

import importlib
import warnings

from collections import OrderedDict

from django.conf import settings


class ProviderRegistry(object):
    def __init__(self):
        self.provider_map = OrderedDict()
        self.loaded = False

    def get_list(self, request=None):
        self.load()
        from ..models import SocialApp
        providers = []
        for provider_cls in self.provider_map.values():
            try:
                SocialApp.objects.get_current(provider_cls.id, request)
                providers.append(provider_cls(request))
            except SocialApp.DoesNotExist:
                warnings.warn("No {} app configured: please"
                              " add a SocialApp using the Django"
                              " admin".format(provider_cls.name))
        return providers

    def register(self, cls):
        self.provider_map[cls.id] = cls

    def by_id(self, id, request=None):
        self.load()
        return self.provider_map[id](request=request)

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
            for app in settings.INSTALLED_APPS:
                try:
                    provider_module = importlib.import_module(
                        app + '.provider'
                    )
                except ImportError:
                    pass
                else:
                    for cls in getattr(
                        provider_module, 'provider_classes', []
                    ):
                        self.register(cls)
            self.loaded = True


registry = ProviderRegistry()

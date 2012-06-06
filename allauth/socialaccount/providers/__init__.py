class ProviderRegistry(object):
    def __init__(self):
        self.provider_map = {}

    def get_providers(self):
        return self.provider_map.values()

    def register_provider(self, cls):
        self.provider_map[cls.id] = cls()

    def provider_by_id(self, id):
        return self.provider_map[id]

registry = ProviderRegistry()


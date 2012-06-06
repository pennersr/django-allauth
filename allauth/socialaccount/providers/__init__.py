class ProviderRegistry(object):
    def __init__(self):
        self.provider_map = {}

    def get_list(self):
        return self.provider_map.values()

    def register(self, cls):
        self.provider_map[cls.id] = cls()

    def by_id(self, id):
        return self.provider_map[id]

    def as_choices(self):
        for provider in self.get_list():
            yield (provider.id, provider.name)

registry = ProviderRegistry()


_providers = { }

def register_provider(cls):
    _providers[cls.id] = cls()
    
def get_providers():
    return _providers.values()

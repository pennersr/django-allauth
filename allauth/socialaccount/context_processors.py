from . import providers

def socialaccount(request):
    ctx = { 'providers': providers.registry.get_list() }
    return dict(socialaccount=ctx)

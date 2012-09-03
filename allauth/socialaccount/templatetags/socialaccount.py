from django.template.defaulttags import token_kwargs
from django import template

from allauth.socialaccount import providers

register = template.Library()

class ProviderLoginURLNode(template.Node):
    def __init__(self, provider_id, params):
        self.provider_id_var = template.Variable(provider_id)
        self.params = params

    def render(self, context):
        provider_id = self.provider_id_var.resolve(context)
        provider = providers.registry.by_id(provider_id)
        query = dict([(str(name), var.resolve(context)) for name, var
                      in self.params.iteritems()])
        request = context['request']
        if not query.has_key('next'):
            next = request.REQUEST.get('next')
            if next:
                query['next'] = next
        else:
            if not query['next']:
                del query['next']
        return provider.get_login_url(request, **query)

@register.tag
def provider_login_url(parser, token):
    """
    {% provider_login_url "facebook" next=bla %}
    {% provider_login_url "openid" openid="http://me.yahoo.com" next=bla %}
    """
    bits = token.split_contents()
    provider_id = bits[1]
    params = token_kwargs(bits[2:], parser, support_legacy=False)
    return ProviderLoginURLNode(provider_id, params)
    
class ProvidersMediaJSNode(template.Node):
    def render(self, context):
        request = context['request']
        ret = '\n'.join([p.media_js(request) 
                         for p in providers.registry.get_list()])
        return ret


@register.tag
def providers_media_js(parser, token):
    return ProvidersMediaJSNode()

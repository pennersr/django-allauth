from django import template
from django.template.defaulttags import token_kwargs

from allauth.socialaccount import providers
from allauth.utils import get_request_param


register = template.Library()


class ProviderLoginURLNode(template.Node):
    def __init__(self, provider_id, params):
        self.provider_id_var = template.Variable(provider_id)
        self.params = params

    def render(self, context):
        provider_id = self.provider_id_var.resolve(context)
        request = context.get('request')
        provider = providers.registry.by_id(provider_id, request)
        query = dict([(str(name), var.resolve(context)) for name, var
                      in self.params.items()])
        auth_params = query.get('auth_params', None)
        scope = query.get('scope', None)
        process = query.get('process', None)
        if scope == '':
            del query['scope']
        if auth_params == '':
            del query['auth_params']
        if 'next' not in query:
            next = get_request_param(request, 'next')
            if next:
                query['next'] = next
            elif process == 'redirect':
                query['next'] = request.get_full_path()
        else:
            if not query['next']:
                del query['next']
        # get the login url and append query as url parameters
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
                         for p in providers.registry.get_list(request)])
        return ret


@register.tag
def providers_media_js(parser, token):
    return ProvidersMediaJSNode()


@register.simple_tag
def get_social_accounts(user):
    """
    {% get_social_accounts user as accounts %}

    Then:
        {{accounts.twitter}} -- a list of connected Twitter accounts
        {{accounts.twitter.0}} -- the first Twitter account
        {% if accounts %} -- if there is at least one social account
    """
    accounts = {}
    for account in user.socialaccount_set.all().iterator():
        providers = accounts.setdefault(account.provider, [])
        providers.append(account)
    return accounts


@register.simple_tag
def get_providers():
    """
    Returns a list of social authentication providers.

    Usage: `{% get_providers as socialaccount_providers %}`.

    Then within the template context, `socialaccount_providers` will hold
    a list of social providers configured for the current site.
    """
    return providers.registry.get_list()

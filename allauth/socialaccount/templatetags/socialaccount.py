from django import template
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.safestring import mark_safe

from allauth.socialaccount.adapter import get_adapter
from allauth.utils import get_request_param


register = template.Library()


@register.simple_tag(takes_context=True)
def provider_login_url(context, provider, **params):
    """
    {% provider_login_url "facebook" next=bla %}
    {% provider_login_url "openid" openid="https://me.yahoo.com" next=bla %}
    """
    request = context.get("request")
    if isinstance(provider, str):
        adapter = get_adapter()
        provider = adapter.get_provider(request, provider)
    query = dict(params)
    auth_params = query.get("auth_params", None)
    scope = query.get("scope", None)
    process = query.get("process", None)
    if scope == "":
        del query["scope"]
    if auth_params == "":
        del query["auth_params"]
    if REDIRECT_FIELD_NAME not in query:
        next = get_request_param(request, REDIRECT_FIELD_NAME)
        if next:
            query[REDIRECT_FIELD_NAME] = next
        elif process == "redirect":
            query[REDIRECT_FIELD_NAME] = request.get_full_path()
    else:
        if not query[REDIRECT_FIELD_NAME]:
            del query[REDIRECT_FIELD_NAME]
    # get the login url and append query as url parameters
    return provider.get_login_url(request, **query)


@register.simple_tag(takes_context=True)
def providers_media_js(context):
    request = context["request"]
    providers = get_adapter().list_providers(request)
    ret = "\n".join(p.media_js(request) for p in providers)
    return mark_safe(ret)  # nosec


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


@register.simple_tag(takes_context=True)
def get_providers(context):
    """
    Returns a list of social authentication providers.

    Usage: `{% get_providers as socialaccount_providers %}`.

    Then within the template context, `socialaccount_providers` will hold
    a list of social providers configured for the current site.
    """
    request = context["request"]
    adapter = get_adapter()
    providers = adapter.list_providers(request)
    providers = [
        provider
        for provider in providers
        if (not provider.uses_apps or not provider.app.settings.get("hidden"))
    ]
    return sorted(providers, key=lambda p: p.name)

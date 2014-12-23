import requests
from django.core.exceptions import ImproperlyConfigured

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount import app_settings, providers

from .provider import PersonaProvider


def persona_login(request):
    assertion = request.POST.get('assertion', '')
    settings = app_settings.PROVIDERS.get(PersonaProvider.id, {})
    audience = settings.get('AUDIENCE', None)
    if audience is None:
        raise ImproperlyConfigured("No Persona audience configured. Please "
                                   "add an AUDIENCE item to the "
                                   "SOCIALACCOUNT_PROVIDERS['persona'] setting.")

    resp = requests.post('https://verifier.login.persona.org/verify',
                         {'assertion': assertion,
                          'audience': audience})
    try:
        resp.raise_for_status()
        extra_data = resp.json()
        if extra_data['status'] != 'okay':
            return render_authentication_error(
                request,
                provider_id=PersonaProvider.id,
                extra_context={'response': extra_data})
    except (ValueError, requests.RequestException) as e:
        return render_authentication_error(
            request,
            provider_id=PersonaProvider.id,
            exception=e)
    login = providers.registry \
        .by_id(PersonaProvider.id) \
        .sociallogin_from_response(request, extra_data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)

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
    if resp.json()['status'] != 'okay':
        return render_authentication_error(request)
    extra_data = resp.json()
    login = providers.registry \
        .by_id(PersonaProvider.id) \
        .sociallogin_from_response(request, extra_data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)

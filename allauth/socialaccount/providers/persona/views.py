import requests

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount import providers

from .provider import PersonaProvider


def persona_login(request):
    assertion = request.POST.get('assertion', '')
    audience = request.build_absolute_uri('/')
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

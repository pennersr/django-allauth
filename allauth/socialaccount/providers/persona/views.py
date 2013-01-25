import requests

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.adapter import get_adapter

from provider import PersonaProvider

def persona_login(request):
    assertion = request.POST.get('assertion', '')
    audience = request.build_absolute_uri('/') 
    resp = requests.post('https://verifier.login.persona.org/verify',
                         { 'assertion': assertion,
                           'audience': audience })
    if resp.json()['status'] != 'okay':
        return render_authentication_error(request)
    email = resp.json()['email']
    user = get_adapter() \
        .populate_new_user(email=email)
    extra_data = resp.json()
    account = SocialAccount(uid=email,
                            provider=PersonaProvider.id,
                            extra_data=extra_data,
                            user=user)
    # TBD: Persona e-mail addresses are verified, so we could check if
    # a matching local user account already exists with an identical
    # verified e-mail address and short-circuit the social login. Then
    # again, this holds for all social providers that guarantee
    # verified e-mail addresses, so if at all, short-circuiting should
    # probably not be handled here...
    login = SocialLogin(account)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)



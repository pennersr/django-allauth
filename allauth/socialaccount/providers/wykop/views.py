from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialAccount, SocialLogin, SocialToken
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount import providers

from .provider import WykopProvider
from .forms import WykopConnectForm

import base64
import ast

def wykop_complete_login(app, connectData):
    import wykop
    client = wykop.WykopAPI(app.client_id, app.secret)
    extra_data = client.get_profile(connectData['login'])
    user = get_adapter() \
        .populate_new_user(email=extra_data.get('email').split(":")[0] + '@wykop.pl',
                           username=extra_data.get('login'),
                           name=extra_data.get('name'))
    account = SocialAccount(uid=extra_data['login'],
                            provider=WykopProvider.id,
                            extra_data=extra_data,
                            user=user)

    return SocialLogin(account)

def wykop_login_by_token(request):
    ret = None
    if request.method == 'GET':
        form = WykopConnectForm(request.GET)
        if form.is_valid():
            try:
                app = providers.registry.by_id(WykopProvider.id).get_app(request)
                connectData = form.cleaned_data['connectData']
                connectData = ast.literal_eval(base64.b64decode(connectData))
                token = SocialToken(app=app, token=connectData['token'])
                login = wykop_complete_login(app, connectData)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except AttributeError:
                # FIXME: Catch only what is needed
                pass
    if not ret:
        ret = render_authentication_error(request)
    return ret



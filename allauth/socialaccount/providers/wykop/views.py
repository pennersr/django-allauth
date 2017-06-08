from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount import providers

from .provider import WykopProvider
from .forms import WykopConnectForm

import base64
import ast

def wykop_complete_login(request, app, connectData):
    import wykop
    client = wykop.WykopAPI(app.client_id, app.secret)
    extra_data = client.get_profile(connectData['login'])
    login = providers.registry \
        .by_id(WykopProvider.id) \
        .sociallogin_from_response(request, extra_data)
    return login

def login_by_token(request):
    ret = None
    if request.method == 'GET':
        form = WykopConnectForm(request.GET)
        if form.is_valid():
            try:
                app = providers.registry.by_id(WykopProvider.id).get_app(request)
                connectData = form.cleaned_data['connectData']
                connectData = ast.literal_eval(base64.b64decode(connectData))
                token = SocialToken(app=app, token=connectData['token'])
                login = wykop_complete_login(request, app, connectData)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except AttributeError:
                # FIXME: Catch only what is needed
                pass
    if not ret:
        ret = render_authentication_error(request)
    return ret



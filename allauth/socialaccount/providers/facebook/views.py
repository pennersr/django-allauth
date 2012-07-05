from django.utils.cache import patch_response_headers
from django.contrib.auth.models import User
from django.shortcuts import render

from allauth.socialaccount.models import SocialAccount, SocialLogin, SocialToken
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount import requests

from forms import FacebookConnectForm
from provider import FacebookProvider

from allauth.utils import valid_email_or_none

def fb_complete_login(app, token):
    resp = requests.get('https://graph.facebook.com/me',
                        params={ 'access_token': token.token })
    extra_data = resp.json
    email = valid_email_or_none(extra_data.get('email'))
    uid = extra_data['id']
    user = User(email=email)
    # some facebook accounts don't have this data
    for k in ['username', 'first_name', 'last_name']:
        v = extra_data.get(k)
        if v:
            setattr(user, k, v)
    account = SocialAccount(uid=uid,
                            provider=FacebookProvider.id,
                            extra_data=extra_data,
                            user=user)
    return SocialLogin(account)


class FacebookOAuth2Adapter(OAuth2Adapter):
    provider_id = FacebookProvider.id

    authorize_url = 'https://www.facebook.com/dialog/oauth'
    access_token_url = 'https://graph.facebook.com/oauth/access_token'

    def complete_login(self, request, app, access_token):
        return fb_complete_login(app, access_token)


oauth2_login = OAuth2LoginView.adapter_view(FacebookOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FacebookOAuth2Adapter)


def login_by_token(request):
    ret = None
    if request.method == 'POST':
        form = FacebookConnectForm(request.POST)
        if form.is_valid():
            try:
                app = providers.registry.by_id(FacebookProvider.id) \
                    .get_app(request)
                access_token = form.cleaned_data['access_token']
                token = SocialToken(app=app,
                                    token=access_token)
                login = fb_complete_login(app, token)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except:
                # FIXME: Catch only what is needed
                pass
    if not ret:
        ret = render_authentication_error(request)
    return ret


def channel(request):
    provider = providers.registry.by_id(FacebookProvider.id)
    locale = provider.get_locale_for_request(request)
    response = render(request, 'facebook/channel.html',
                      {'facebook_jssdk_locale': locale})
    cache_expire = 60 * 60 * 24 * 365
    patch_response_headers(response, cache_expire)
    response['Pragma'] = 'Public'
    return response

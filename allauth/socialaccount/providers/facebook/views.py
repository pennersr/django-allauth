from django.utils.cache import patch_response_headers
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CompleteView)


try:
    from facebook import GraphAPI, GraphAPIError
except ImportError:
    # People often seem to overlook this dependency, so let's make it
    # a bit more explicit...
    raise ImproperlyConfigured("Dependency missing: Python Facebook SDK")

from forms import FacebookConnectForm
from models import FacebookProvider

from allauth.utils import valid_email_or_none


def fb_user_info(access_token):
    api = GraphAPI(access_token)
    extra_data = api.get_object("me")
    email = valid_email_or_none(extra_data.get('email'))
    uid = extra_data['id']
    data = dict(email=email,
                facebook_access_token=access_token,
                facebook_me=extra_data)
    # some facebook accounts don't have this data
    data.update((k, v) for (k, v) in extra_data.items()
                if k in ['username', 'first_name', 'last_name'])
    return uid, data, extra_data


class FacebookOAuth2Adapter(OAuth2Adapter):
    provider_id = FacebookProvider.id

    authorize_url = 'https://www.facebook.com/dialog/oauth'
    access_token_url = 'https://graph.facebook.com/oauth/access_token'

    def get_user_info(self, request, app, access_token):
        try:
            return fb_user_info(access_token)
        except (GraphAPIError, IOError), e:
            raise OAuth2Error(e)

oauth2_login = OAuth2LoginView.adapter_view(FacebookOAuth2Adapter)
oauth2_complete = OAuth2CompleteView.adapter_view(FacebookOAuth2Adapter)


def login_by_token(request):
    ret = None
    if request.method == 'POST':
        form = FacebookConnectForm(request.POST)
        if form.is_valid():
            try:
                token = form.cleaned_data['access_token']
                social_id, data, facebook_me = fb_user_info(token)
                # TODO: DRY, duplicates OAuth logic
                try:
                    account = SocialAccount.objects \
                        .get(uid=social_id,
                             provider=FacebookProvider.id)
                except SocialAccount.DoesNotExist:
                    account = SocialAccount(uid=social_id,
                                            provider=FacebookProvider.id)
                # Don't save partial/temporary accounts that haven't
                # gone through the full signup yet, as there is no
                # User attached yet.
                if account.pk:
                    account.sync(data)
                ret = complete_social_login(request, data, account)
            except (GraphAPIError, IOError):
                pass
    if not ret:
        ret = render_authentication_error(request)
    return ret


def channel(request):
    response = render(request, 'facebook/channel.html')
    cache_expire = 60 * 60 * 24 * 365
    patch_response_headers(response, cache_expire)
    response['Pragma'] = 'Public'
    return response

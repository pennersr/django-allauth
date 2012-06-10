from django.utils.cache import patch_response_headers
from django.shortcuts import render

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.facebook.provider_settings import JSSDK_LOCALE
from facebook import GraphAPI, GraphAPIError, get_user_from_cookie

from forms import FacebookConnectForm
from models import FacebookProvider

from allauth.utils import valid_email_or_none


def login(request):
    ret = None
    if request.method == 'POST':
        try:
            app = SocialApp.objects.get_current(FacebookProvider.id)
        except SocialApp.DoesNotExist:
            raise ImproperlyConfigured("No Facebook app configured: please"
                                     " add a SocialApp using the Django admin")
        try:
            # TODO: Split this function so it doesn't autoretrieve the token
            fbcred = get_user_from_cookie(request.COOKIES, app.key, app.secret)
            if fbcred is not None:
                social_id = fbcred['uid']
                g = GraphAPI(fbcred['access_token'])
                # TODO: Make access token extension optional (a setting)
                # TODO: Extend only when close to expiration
                ex = g.extend_access_token(app.key, app.secret)
                token = ex['access_token']
                facebook_me = g.get_object("me")
                email = valid_email_or_none(facebook_me.get('email'))
                try:
                    account = SocialAccount.objects.get(uid=social_id,
                                                        provider=FacebookProvider.id)
                except SocialAccount.DoesNotExist:
                    account = SocialAccount(uid=social_id,
                                            provider=FacebookProvider.id)
                data = dict(email=email,
                            facebook_access_token=token,
                            facebook_me=facebook_me)
                # some facebook accounts don't have this data
                data.update((k, v) for (k, v) in facebook_me.items()
                            if k in ['username', 'first_name', 'last_name'])
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
    response = render(request, 'facebook/channel.html',
                      {'facebook_jssdk_locale': JSSDK_LOCALE})
    cache_expire = 60 * 60 * 24 * 365
    patch_response_headers(response, cache_expire)
    response['Pragma'] = 'Public'
    return response

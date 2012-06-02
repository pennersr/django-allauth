# Create your views here.
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from allauth.utils import get_login_redirect_url
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.oauth import OAuthClient, OAuthError
from allauth.socialaccount.models import SocialApp, SocialAccount
from allauth.socialaccount.defs import Provider

from utils import OAuthTwitter

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'


def login_done(request):
    app = SocialApp.objects.get_current(Provider.TWITTER.id)
    client = OAuthTwitter(
        request, app.key,
        app.secret,
        REQUEST_TOKEN_URL)
    try:
        user_info = client.get_user_info()
    except OAuthError:
        return render_authentication_error(request)
    try:
        account = SocialAccount.objects.get(provider=Provider.TWITTER.id,
                                            uid=user_info['id'])
    except SocialAccount.DoesNotExist:
        account = SocialAccount(provider=Provider.TWITTER.id,
                                uid=user_info['id']) 
    account.extra_data = { 'profile_image_url': user_info['profile_image_url'],
                           'screen_name': user_info['screen_name'] }
    if account.pk:
        account.save()
    data = dict(twitter_user_info=user_info,
                username=user_info['screen_name'])
    return complete_social_login(request, data, account)


def oauth_redirect(request, consumer_key=None, secret_key=None,
    request_token_url=None, access_token_url=None, authorization_url=None,
    callback_url=None, parameters=None):
    """
    View to handle the OAuth based authentication redirect to the service provider
    """
    request.session['next'] = get_login_redirect_url(request)
    client = OAuthClient(request, consumer_key, secret_key,
        request_token_url, access_token_url, authorization_url, callback_url, parameters)
    try:
        return client.get_redirect()
    except OAuthError, e:
        return render_authentication_error(request)


def oauth_callback(request, consumer_key=None, secret_key=None,
    request_token_url=None, access_token_url=None, authorization_url=None,
    callback_url=None, 
    extra_context=dict(), parameters=None):
    """
    View to handle final steps of OAuth based authentication where the user
    gets redirected back to from the service provider
    """
    client = OAuthClient(request, consumer_key, secret_key, request_token_url,
        access_token_url, authorization_url, callback_url, parameters)

    extra_context.update(dict(oauth_client=client))

    if not client.is_valid():
        if request.GET.has_key('denied'):
            return HttpResponseRedirect \
                (reverse('socialaccount_login_cancelled'))
        return render_authentication_error(request, extra_context)

    # We're redirecting to the setup view for this oauth service
    return HttpResponseRedirect(client.callback_url)


def _oauth_kwargs(request, callback_url):
    app = SocialApp.objects.get_current(Provider.TWITTER.id)
    kwargs = dict(consumer_key=app.key,
                  secret_key=app.secret,
                  request_token_url=REQUEST_TOKEN_URL,
                  access_token_url=ACCESS_TOKEN_URL,
                  authorization_url=AUTHORIZE_URL,
                  callback_url=callback_url)
    return kwargs

def login(request):
    kwargs = _oauth_kwargs(request, reverse(callback))
    return oauth_redirect(request, **kwargs)
                           
@csrf_exempt
def callback(request):
    kwargs = _oauth_kwargs(request, reverse(login_done))
    return oauth_callback(request, **kwargs)


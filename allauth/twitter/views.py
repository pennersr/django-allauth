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

from models import TwitterApp, TwitterAccount
from utils import OAuthTwitter

def login_done(request):
    app = TwitterApp.objects.get_current()
    client = OAuthTwitter(
        request, app.consumer_key,
        app.consumer_secret,
        app.request_token_url)
    try:
        user_info = client.get_user_info()
    except OAuthError, e:
        return render_authentication_error(request)
    try:
        account = TwitterAccount.objects.get(social_id=user_info['id'])
    except TwitterAccount.DoesNotExist:
        account = TwitterAccount(social_id=user_info['id']) 
    account.profile_image_url = user_info['profile_image_url']
    account.username = user_info['screen_name']
    if account.pk:
        account.save()
    data = dict(twitter_user_info=user_info,
                username=account.username)
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
    app = TwitterApp.objects.get_current()
    kwargs = dict(consumer_key=app.consumer_key,
                  secret_key=app.consumer_secret,
                  request_token_url=app.request_token_url,
                  access_token_url=app.access_token_url,
                  authorization_url=app.authorize_url,
                  callback_url=callback_url)
    return kwargs

def login(request):
    kwargs = _oauth_kwargs(request, reverse(callback))
    return oauth_redirect(request, **kwargs)
                           
@csrf_exempt
def callback(request):
    kwargs = _oauth_kwargs(request, reverse(login_done))
    return oauth_callback(request, **kwargs)


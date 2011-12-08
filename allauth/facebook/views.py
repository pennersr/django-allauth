from datetime import datetime, timedelta

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.cache import patch_response_headers
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt

from allauth.utils import get_login_redirect_url
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.oauth import OAuthClient

from facebook import GraphAPI, GraphAPIError

from models import FacebookApp, FacebookAccount
from forms import FacebookConnectForm

from allauth.utils import valid_email_or_none

def login(request):
    ret = None
    if request.method == 'POST':
        form = FacebookConnectForm(request.POST)
        if form.is_valid():
            try:
                token = form.cleaned_data['access_token']
                g = GraphAPI(token)
                facebook_me = g.get_object("me")
                email = valid_email_or_none(facebook_me.get('email'))
                social_id = facebook_me['id']
                try:
                    account = FacebookAccount.objects.get(social_id=social_id)
                except FacebookAccount.DoesNotExist:
                    account = FacebookAccount(social_id=social_id)
                data = dict(email=email,
                            facebook_access_token=token,
                            facebook_me=facebook_me)
                # some facebook accounts don't have this data
                data.update((k,v) for (k,v) in facebook_me.items() 
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
    response = render(request, 'facebook/channel.html')
    cache_expire = 60*60*24*365
    patch_response_headers(response, cache_expire)
    response['Pragma'] = 'Public'
    return response

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
from allauth.socialaccount.oauth import OAuthClient

from facebook import GraphAPI

from models import FacebookApp, FacebookAccount
from forms import FacebookConnectForm

from allauth.utils import valid_email_or_none

def login(request):
    ret = None
    if request.method == 'POST':
        form = FacebookConnectForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['access_token']
            g = GraphAPI(token)
            data = g.get_object("me")
            email = valid_email_or_none(data.get('email'))
            social_id = data['id']
            try:
                account = FacebookAccount.objects.get(social_id=social_id)
            except FacebookAccount.DoesNotExist:
                account = FacebookAccount(social_id=social_id)
            account.link = data['link']
            account.name = data['name']
            if account.pk:
                account.save()
            data = dict(email=email,
                        facebook_me=data)
            ret = complete_social_login(request, data, account)
    if not ret:
        ret = render_authentication_error(request)
    return ret

    

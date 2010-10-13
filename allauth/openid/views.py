from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from openid.consumer.discover import DiscoveryFailure
from openid.consumer import consumer

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.helpers import complete_social_login

from models import OpenIDAccount
from utils import DBOpenIDStore
from forms import LoginForm

def _openid_consumer(request):
    store = DBOpenIDStore()
    client = consumer.Consumer(request.session, store)
    return client

def login(request):
    if request.GET.has_key('openid') or request.method=='POST':
        form = LoginForm(request.REQUEST)
        if form.is_valid():
            client = _openid_consumer(request)
            auth_request = client.begin(form.cleaned_data['openid'])
            try:
                redirect_url = auth_request.redirectURL(
                    request.build_absolute_uri('/'), 
                    request.build_absolute_uri(reverse(callback)))
                return HttpResponseRedirect(redirect_url)
            except DiscoveryFailure:
                return render_authentication_error(request)
    else:
        form = LoginForm()
    d = dict(form=form)
    return render_to_response('openid/login.html', 
                              d, context_instance=RequestContext(request))


@csrf_exempt
def callback(request):
    client = _openid_consumer(request)
    result = client.complete(
        dict(request.GET.items()),
        request.build_absolute_uri(request.path))
    if result.status == consumer.SUCCESS:
        identity = result.identity_url
        try:
            account = OpenIDAccount.objects.get(identity=identity)
        except OpenIDAccount.DoesNotExist:
            account = OpenIDAccount(identity=identity)
        ret = complete_social_login(request, None, account)
    else:
        ret = render_authentication_error(request)
    return ret



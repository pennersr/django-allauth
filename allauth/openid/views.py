from django.utils.http import urlencode
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from openid.consumer.discover import DiscoveryFailure
from openid.consumer import consumer
from openid.extensions.sreg import SRegRequest, SRegResponse
from openid.extensions.ax import FetchRequest, FetchResponse, AttrInfo

from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.helpers import complete_social_login
from allauth.utils import valid_email_or_none


from models import OpenIDAccount
from utils import DBOpenIDStore
from forms import LoginForm

class AXAttribute:
    CONTACT_EMAIL = 'http://axschema.org/contact/email'

class SRegField:
    EMAIL = 'email'

def _openid_consumer(request):
    store = DBOpenIDStore()
    client = consumer.Consumer(request.session, store)
    return client


def login(request):
    if request.GET.has_key('openid') or request.method=='POST':
        form = LoginForm(request.REQUEST)
        if form.is_valid():
            client = _openid_consumer(request)
            try:
                auth_request = client.begin(form.cleaned_data['openid'])
                if QUERY_EMAIL:
                    sreg = SRegRequest()
                    sreg.requestField(field_name=SRegField.EMAIL, required=True)
                    auth_request.addExtension(sreg)
                    ax = FetchRequest()
                    ax.add(AttrInfo(AXAttribute.CONTACT_EMAIL, 
                                    required=True))
                    auth_request.addExtension(ax)
                callback_url = reverse(callback)
                next = request.GET.get('next')
                if next:
                    callback_url = callback_url + '?' + urlencode(dict(next=next))
                redirect_url = auth_request.redirectURL(
                    request.build_absolute_uri('/'), 
                    request.build_absolute_uri(callback_url))
                return HttpResponseRedirect(redirect_url)
            except DiscoveryFailure, e:
                if request.method == 'POST':
                    form._errors["openid"] = form.error_class([e])
                else:
                    return render_authentication_error(request)
    else:
        form = LoginForm()
    d = dict(form=form)
    return render_to_response('openid/login.html', 
                              d, context_instance=RequestContext(request))


def _get_email_from_response(response):
    email = None
    sreg = SRegResponse.fromSuccessResponse(response)
    if sreg:
        email = valid_email_or_none(sreg.get(SRegField.EMAIL))
    if not email:
        ax = FetchResponse.fromSuccessResponse(response)
        if ax:
            try:
                values = ax.get(AXAttribute.CONTACT_EMAIL)
                if values:
                    email = valid_email_or_none(values[0])
            except KeyError:
                pass
    return email

@csrf_exempt
def callback(request):
    client = _openid_consumer(request)
    response = client.complete(
        dict(request.REQUEST.items()),
        request.build_absolute_uri(request.path))
    if response.status == consumer.SUCCESS:
        email = _get_email_from_response(response)
        identity = response.identity_url
        try:
            account = OpenIDAccount.objects.get(identity=identity)
        except OpenIDAccount.DoesNotExist:
            account = OpenIDAccount(identity=identity)
        data = dict(email=email)
        ret = complete_social_login(request, data, account)
    elif response.status == consumer.CANCEL:
        ret = HttpResponseRedirect(reverse('socialaccount_login_cancelled'))
    else:
        ret = render_authentication_error(request)
    return ret



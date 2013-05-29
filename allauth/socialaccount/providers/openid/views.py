from django.utils.http import urlencode
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from openid.consumer.discover import DiscoveryFailure
from openid.consumer import consumer
from openid.extensions.sreg import SRegRequest, SRegResponse
from openid.extensions.ax import FetchRequest, FetchResponse, AttrInfo

from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.adapter import get_adapter
from allauth.utils import valid_email_or_none

from .utils import DBOpenIDStore
from .forms import LoginForm
from .provider import OpenIDProvider

class AXAttribute:
    CONTACT_EMAIL = 'http://axschema.org/contact/email'


class SRegField:
    EMAIL = 'email'


def _openid_consumer(request):
    store = DBOpenIDStore()
    client = consumer.Consumer(request.session, store)
    return client


def login(request):
    if 'openid' in request.GET or request.method == 'POST':
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
                SocialLogin.stash_state(request)
                redirect_url = auth_request.redirectURL(
                    request.build_absolute_uri('/'),
                    request.build_absolute_uri(callback_url))
                return HttpResponseRedirect(redirect_url)
            # UnicodeDecodeError: see https://github.com/necaris/python3-openid/issues/1
            except (UnicodeDecodeError, DiscoveryFailure) as e:
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
        user = get_adapter() \
            .populate_new_user(email=_get_email_from_response(response))
        account = SocialAccount(uid=response.identity_url,
                                provider=OpenIDProvider.id,
                                user=user,
                                extra_data={})
        login = SocialLogin(account)
        login.state = SocialLogin.unstash_state(request)
        ret = complete_social_login(request, login)
    elif response.status == consumer.CANCEL:
        ret = HttpResponseRedirect(reverse('socialaccount_login_cancelled'))
    else:
        ret = render_authentication_error(request)
    return ret


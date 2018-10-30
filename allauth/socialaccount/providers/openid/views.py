from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure
from openid.extensions.ax import AttrInfo, FetchRequest
from openid.extensions.sreg import SRegRequest

from allauth.socialaccount import providers
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin

from ..base import AuthError
from .forms import LoginForm
from .provider import OpenIDProvider
from .utils import AXAttributes, DBOpenIDStore, JSONSafeSession, SRegFields


def _openid_consumer(request):
    store = DBOpenIDStore()
    client = consumer.Consumer(JSONSafeSession(request.session), store)
    return client


def login(request):
    if 'openid' in request.GET or request.method == 'POST':
        form = LoginForm(
            dict(list(request.GET.items()) + list(request.POST.items()))
        )
        if form.is_valid():
            client = _openid_consumer(request)
            provider = OpenIDProvider(request)
            realm = provider.get_settings().get(
                'REALM',
                request.build_absolute_uri('/'))
            try:
                auth_request = client.begin(form.cleaned_data['openid'])
                if QUERY_EMAIL:
                    sreg = SRegRequest()
                    for name in SRegFields:
                        sreg.requestField(field_name=name,
                                          required=True)
                    auth_request.addExtension(sreg)
                    ax = FetchRequest()
                    for name in AXAttributes:
                        ax.add(AttrInfo(name,
                                        required=True))
                    provider = OpenIDProvider(request)
                    server_settings = \
                        provider.get_server_settings(request.GET.get('openid'))
                    extra_attributes = \
                        server_settings.get('extra_attributes', [])
                    for _, name, required in extra_attributes:
                        ax.add(AttrInfo(name,
                                        required=required))
                    auth_request.addExtension(ax)
                callback_url = reverse(callback)
                SocialLogin.stash_state(request)
                # Fix for issues 1523 and 2072 (github django-allauth)
                if 'next' in form.cleaned_data and form.cleaned_data['next']:
                    auth_request.return_to_args['next'] = \
                        form.cleaned_data['next']
                redirect_url = auth_request.redirectURL(
                    realm,
                    request.build_absolute_uri(callback_url))
                return HttpResponseRedirect(redirect_url)
            # UnicodeDecodeError:
            # see https://github.com/necaris/python3-openid/issues/1
            except (UnicodeDecodeError, DiscoveryFailure) as e:
                if request.method == 'POST':
                    form._errors["openid"] = form.error_class([e])
                else:
                    return render_authentication_error(
                        request,
                        OpenIDProvider.id,
                        exception=e)
    else:
        form = LoginForm(initial={'next': request.GET.get('next'),
                                  'process': request.GET.get('process')})
    d = dict(form=form)
    return render(request, "openid/login.html", d)


@csrf_exempt
def callback(request):
    client = _openid_consumer(request)
    response = client.complete(
        dict(list(request.GET.items()) + list(request.POST.items())),
        request.build_absolute_uri(request.path))
    if response.status == consumer.SUCCESS:
        login = providers.registry \
            .by_id(OpenIDProvider.id, request) \
            .sociallogin_from_response(request, response)
        login.state = SocialLogin.unstash_state(request)
        ret = complete_social_login(request, login)
    else:
        if response.status == consumer.CANCEL:
            error = AuthError.CANCELLED
        else:
            error = AuthError.UNKNOWN
        ret = render_authentication_error(
            request,
            OpenIDProvider.id,
            error=error)
    return ret

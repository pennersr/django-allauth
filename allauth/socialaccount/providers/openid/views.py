from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure
from openid.extensions.ax import AttrInfo, FetchRequest
from openid.extensions.sreg import SRegRequest

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.openid.provider import OpenIDProvider

from ..base import AuthError
from .forms import LoginForm
from .utils import AXAttributes, DBOpenIDStore, JSONSafeSession, SRegFields


def _openid_consumer(request, provider, endpoint):
    server_settings = provider.get_server_settings(endpoint)
    stateless = server_settings.get("stateless", False)
    store = None if stateless else DBOpenIDStore()
    client = consumer.Consumer(JSONSafeSession(request.session), store)
    return client


@method_decorator(login_not_required, name="dispatch")
class OpenIDLoginView(View):
    template_name = "openid/login.html"
    form_class = LoginForm
    provider_class = OpenIDProvider

    def dispatch(self, request, *args, **kwargs):
        self.provider = self.provider_class(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.get_form()
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        try:
            return self.perform_openid_auth(form)
        except (UnicodeDecodeError, DiscoveryFailure) as e:
            # UnicodeDecodeError: necaris/python3-openid#1
            return render_authentication_error(request, self.provider, exception=e)

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            try:
                return self.perform_openid_auth(form)
            except (UnicodeDecodeError, DiscoveryFailure) as e:
                form._errors["openid"] = form.error_class([e])

        return render(request, self.template_name, {"form": form})

    def get_form(self):
        if self.request.method == "GET" and "openid" not in self.request.GET:
            return self.form_class(
                initial={
                    "next": self.request.GET.get(REDIRECT_FIELD_NAME),
                    "process": self.request.GET.get("process"),
                }
            )

        return self.form_class(
            dict(list(self.request.GET.items()) + list(self.request.POST.items()))
        )

    def get_client(self, provider, endpoint):
        return _openid_consumer(self.request, provider, endpoint)

    def get_realm(self, provider):
        return provider.get_settings().get(
            "REALM", self.request.build_absolute_uri("/")
        )

    def get_callback_url(self):
        return reverse(callback)

    def perform_openid_auth(self, form):
        if not form.is_valid():
            return form

        request = self.request
        provider = self.provider
        endpoint = form.cleaned_data["openid"]
        client = self.get_client(provider, endpoint)
        realm = self.get_realm(provider)

        auth_request = client.begin(endpoint)
        if QUERY_EMAIL:
            sreg = SRegRequest()
            for name in SRegFields:
                sreg.requestField(field_name=name, required=True)
            auth_request.addExtension(sreg)
            ax = FetchRequest()
            for name in AXAttributes:
                ax.add(AttrInfo(name, required=True))
            server_settings = provider.get_server_settings(request.GET.get("openid"))
            extra_attributes = server_settings.get("extra_attributes", [])
            for _, name, required in extra_attributes:
                ax.add(AttrInfo(name, required=required))
            auth_request.addExtension(ax)

        SocialLogin.stash_state(request)

        # Fix for issues 1523 and 2072 (github django-allauth)
        if "next" in form.cleaned_data and form.cleaned_data["next"]:
            auth_request.return_to_args["next"] = form.cleaned_data["next"]
        redirect_url = auth_request.redirectURL(
            realm, request.build_absolute_uri(self.get_callback_url())
        )
        return HttpResponseRedirect(redirect_url)


login = OpenIDLoginView.as_view()


@method_decorator(login_not_required, name="dispatch")
class OpenIDCallbackView(View):
    provider_class = OpenIDProvider

    def get(self, request):
        provider = self.provider = self.provider_class(request)
        endpoint = request.GET.get("openid.op_endpoint", "")
        client = self.get_client(provider, endpoint)
        response = self.get_openid_response(client)

        if response.status == consumer.SUCCESS:
            login = provider.sociallogin_from_response(request, response)
            login.state = SocialLogin.unstash_state(request)
            return self.complete_login(login)
        else:
            if response.status == consumer.CANCEL:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return self.render_error(error)

    post = get

    def complete_login(self, login):
        return complete_social_login(self.request, login)

    def render_error(self, error):
        return render_authentication_error(self.request, self.provider, error=error)

    def get_client(self, provider, endpoint):
        return _openid_consumer(self.request, provider, endpoint)

    def get_openid_response(self, client):
        return client.complete(
            dict(list(self.request.GET.items()) + list(self.request.POST.items())),
            self.request.build_absolute_uri(self.request.path),
        )


callback = csrf_exempt(OpenIDCallbackView.as_view())

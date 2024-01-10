import binascii
import logging

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Settings
from onelogin.saml2.errors import OneLogin_Saml2_Error

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import get_next_redirect_url
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base.constants import AuthError
from allauth.socialaccount.providers.base.utils import respond_to_login_on_get
from allauth.socialaccount.sessions import LoginSession

from .utils import (
    build_saml_config,
    decode_relay_state,
    encode_relay_state,
    get_app_or_404,
    prepare_django_request,
)


logger = logging.getLogger(__name__)


class SAMLViewMixin:
    def build_auth(self, provider, organization_slug):
        req = prepare_django_request(self.request)
        config = build_saml_config(
            self.request, provider.app.settings, organization_slug
        )
        auth = OneLogin_Saml2_Auth(req, config)
        return auth

    def get_app(self, organization_slug):
        app = get_app_or_404(self.request, organization_slug)
        return app

    def get_provider(self, organization_slug):
        app = self.get_app(organization_slug)
        return app.get_provider(self.request)


@method_decorator(csrf_exempt, name="dispatch")
class ACSView(SAMLViewMixin, View):
    def dispatch(self, request, organization_slug):
        provider = self.get_provider(organization_slug)
        auth = self.build_auth(provider, organization_slug)
        error_reason = None
        errors = []
        try:
            auth.process_response()
        except binascii.Error:
            errors = ["invalid_response"]
            error_reason = "Invalid response"
        except OneLogin_Saml2_Error as e:
            error_reason = str(e)
        if not errors:
            errors = auth.get_errors()
        if errors:
            # e.g. ['invalid_response']
            error_reason = auth.get_last_error_reason() or error_reason
            logger.error(
                "Error processing SAML ACS response: %s: %s"
                % (", ".join(errors), error_reason)
            )
            return render_authentication_error(
                request,
                provider,
                extra_context={
                    "saml_errors": errors,
                    "saml_last_error_reason": error_reason,
                },
            )
        if not auth.is_authenticated():
            return render_authentication_error(
                request, provider, error=AuthError.CANCELLED
            )

        relay_state = decode_relay_state(request.POST.get("RelayState"))
        login = provider.sociallogin_from_response(request, auth)
        for key in ["process", "next"]:
            value = relay_state.get(key)
            if value:
                login.state[key] = value
        acs_session = LoginSession(request, "saml_acs_session", "saml-acs-session")
        acs_session.store["login"] = login.serialize()
        url = reverse(
            "saml_finish_acs",
            kwargs={"organization_slug": organization_slug},
        )
        response = HttpResponseRedirect(url)
        acs_session.save(response)
        return response


acs = ACSView.as_view()


class FinishACSView(SAMLViewMixin, View):
    def dispatch(self, request, organization_slug):
        provider = self.get_provider(organization_slug)
        acs_session = LoginSession(request, "saml_acs_session", "saml-acs-session")
        serialized_login = acs_session.store.get("login")
        if not serialized_login:
            logger.error("Unable to finish login, SAML ACS session missing")
            return render_authentication_error(request, provider)
        acs_session.delete()
        login = SocialLogin.deserialize(serialized_login)
        return complete_social_login(request, login)


finish_acs = FinishACSView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
class SLSView(SAMLViewMixin, View):
    def dispatch(self, request, organization_slug):
        provider = self.get_provider(organization_slug)
        auth = self.build_auth(provider, organization_slug)
        should_logout = request.user.is_authenticated
        account_adapter = get_account_adapter(request)

        def force_logout():
            account_adapter.logout(request)

        redirect_to = None
        error_reason = None
        try:
            redirect_to = auth.process_slo(
                delete_session_cb=force_logout, keep_local_session=not should_logout
            )
        except OneLogin_Saml2_Error as e:
            error_reason = str(e)
        errors = auth.get_errors()
        if errors:
            error_reason = auth.get_last_error_reason() or error_reason
            logger.error(
                "Error processing SAML SLS response: %s: %s"
                % (", ".join(errors), error_reason)
            )
            resp = HttpResponse(error_reason, content_type="text/plain")
            resp.status_code = 400
            return resp
        if not redirect_to:
            redirect_to = account_adapter.get_logout_redirect_url(request)
        return HttpResponseRedirect(redirect_to)


sls = SLSView.as_view()


class MetadataView(SAMLViewMixin, View):
    def dispatch(self, request, organization_slug):
        provider = self.get_provider(organization_slug)
        config = build_saml_config(
            self.request, provider.app.settings, organization_slug
        )
        saml_settings = OneLogin_Saml2_Settings(
            settings=config, sp_validation_only=True
        )
        metadata = saml_settings.get_sp_metadata()
        errors = saml_settings.validate_metadata(metadata)

        if len(errors) > 0:
            resp = JsonResponse({"errors": errors})
            resp.status_code = 500
            return resp

        return HttpResponse(content=metadata, content_type="text/xml")


metadata = MetadataView.as_view()


class LoginView(SAMLViewMixin, View):
    def dispatch(self, request, organization_slug):
        provider = self.get_provider(organization_slug)
        resp = respond_to_login_on_get(request, provider)
        if resp:
            return resp
        auth = self.build_auth(provider, organization_slug)
        process = self.request.GET.get("process")
        next_url = get_next_redirect_url(request)
        relay_state = encode_relay_state(process=process, next_url=next_url)
        # If we pass `return_to=None` `auth.login` will use the URL of the
        # current view, which will then end up being used as a redirect URL.
        redirect = auth.login(return_to=relay_state)
        return HttpResponseRedirect(redirect)


login = LoginView.as_view()

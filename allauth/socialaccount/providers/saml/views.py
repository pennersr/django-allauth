import binascii
import logging

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Settings

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import get_next_redirect_url
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base.constants import (
    AuthError,
    AuthProcess,
)
from allauth.socialaccount.sessions import LoginSession

from .utils import build_saml_config, get_app_or_404, prepare_django_request


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
        try:
            auth.process_response()
        except binascii.Error:
            errors = ["invalid_response"]
        else:
            errors = auth.get_errors()
        if errors:
            # e.g. ['invalid_response']
            logger.error(
                "Error processing SAML response: %s: %s"
                % (", ".join(errors), auth.get_last_error_reason())
            )
            return render_authentication_error(
                request,
                provider.id,
                extra_context={
                    "saml_errors": errors,
                    "saml_last_error_reason": auth.get_last_error_reason(),
                },
            )
        if not auth.is_authenticated():
            return render_authentication_error(
                request, provider.id, error=AuthError.CANCELLED
            )

        relay_state = request.POST.get("RelayState")
        login = provider.sociallogin_from_response(request, auth)
        if relay_state == reverse("socialaccount_connections"):
            login.state["process"] = AuthProcess.CONNECT
        elif relay_state:
            login.state["next"] = relay_state

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
            return render_authentication_error(request, provider.id)
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

        redirect_to = auth.process_slo(
            delete_session_cb=force_logout, keep_local_session=not should_logout
        )
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
        auth = self.build_auth(provider, organization_slug)
        process = self.request.GET.get("process")
        return_to = get_next_redirect_url(request)
        if return_to:
            pass
        elif process == AuthProcess.CONNECT:
            return_to = reverse("socialaccount_connections")
        else:
            # If we pass `return_to=None` `auth.login` will use the URL of the
            # current view, which will then end up being used as a redirect URL.
            return_to = ""
        redirect = auth.login(return_to=return_to)
        return HttpResponseRedirect(redirect)


login = LoginView.as_view()

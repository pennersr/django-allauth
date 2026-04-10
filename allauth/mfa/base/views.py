from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from allauth.account import app_settings as account_settings
from allauth.account.internal.decorators import login_stage_required
from allauth.account.internal.templatekit import get_entrance_context_data
from allauth.account.views import BaseReauthenticateView
from allauth.core.internal.httpkit import authenticated_user
from allauth.mfa import app_settings
from allauth.mfa.base.forms import AuthenticateForm, ReauthenticateForm
from allauth.mfa.internal.flows import trust as trust_
from allauth.mfa.models import Authenticator
from allauth.mfa.stages import AuthenticateStage, TrustStage
from allauth.mfa.utils import is_mfa_enabled
from allauth.mfa.webauthn.forms import AuthenticateWebAuthnForm
from allauth.mfa.webauthn.internal.flows import auth as webauthn_auth
from allauth.utils import get_form_class


@method_decorator(
    login_stage_required(stage=AuthenticateStage.key, redirect_urlname="account_login"),
    name="dispatch",
)
class AuthenticateView(TemplateView):
    form_class = AuthenticateForm
    webauthn_form_class = AuthenticateWebAuthnForm
    template_name = f"mfa/authenticate.{account_settings.TEMPLATE_EXTENSION}"

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        self.stage = request._login_stage  # type:ignore[attr-defined]
        if not is_mfa_enabled(
            self.stage.login.user,
            [Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN],
        ):
            return HttpResponseRedirect(reverse("account_login"))
        self.form = self._build_forms()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    def _build_forms(self):
        posted_form = None
        AuthenticateFormClass = self.get_form_class()
        AuthenticateWebAuthnFormClass = self.get_webauthn_form_class()
        user = self.stage.login.user
        support_webauthn = "webauthn" in app_settings.SUPPORTED_TYPES
        if self.request.method == "POST":
            if "code" in self.request.POST:
                posted_form = self.auth_form = AuthenticateFormClass(
                    user=user, data=self.request.POST
                )
                self.webauthn_form = (
                    AuthenticateWebAuthnFormClass(user=user)
                    if support_webauthn
                    else None
                )
            else:
                self.auth_form = (
                    AuthenticateFormClass(user=user) if support_webauthn else None
                )
                posted_form = self.webauthn_form = AuthenticateWebAuthnFormClass(
                    user=user, data=self.request.POST
                )
        else:
            self.auth_form = AuthenticateFormClass(user=user)
            self.webauthn_form = (
                AuthenticateWebAuthnFormClass(user=user) if support_webauthn else None
            )
        return posted_form

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "authenticate", self.form_class)

    def get_webauthn_form_class(self):
        return get_form_class(
            app_settings.FORMS, "authenticate_webauthn", self.webauthn_form_class
        )

    def form_valid(self, form) -> HttpResponse:
        form.save()
        return self.stage.exit()

    def form_invalid(self, form) -> HttpResponse:
        return super().get(self.request)

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data()
        ret.update(get_entrance_context_data(self.request))
        ret.update(
            {
                "form": self.auth_form,
                "MFA_SUPPORTED_TYPES": app_settings.SUPPORTED_TYPES,
            }
        )
        if self.webauthn_form:
            request_options = webauthn_auth.begin_authentication(self.stage.login.user)
            ret.update(
                {
                    "webauthn_form": self.webauthn_form,
                    "js_data": {"request_options": request_options},
                }
            )
        return ret


authenticate = AuthenticateView.as_view()


@method_decorator(login_required, name="dispatch")
class ReauthenticateView(BaseReauthenticateView):
    form_class = ReauthenticateForm
    template_name = f"mfa/reauthenticate.{account_settings.TEMPLATE_EXTENSION}"

    def get_form_kwargs(self) -> dict:
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "reauthenticate", self.form_class)

    def form_valid(self, form) -> HttpResponse:
        form.save()
        return super().form_valid(form)


reauthenticate = ReauthenticateView.as_view()


@method_decorator(login_required, name="dispatch")
class IndexView(TemplateView):
    template_name = f"mfa/index.{account_settings.TEMPLATE_EXTENSION}"

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        authenticators: dict = {}
        user = authenticated_user(self.request)
        for auth in Authenticator.objects.filter(user_id=user.pk):
            if auth.type == Authenticator.Type.WEBAUTHN:
                auths = authenticators.setdefault(auth.type, [])
                auths.append(auth.wrap())
            else:
                authenticators[auth.type] = auth.wrap()
        ret["authenticators"] = authenticators
        ret["MFA_SUPPORTED_TYPES"] = app_settings.SUPPORTED_TYPES
        ret["MFA_RECOVERY_CODES_SHOW_ONCE"] = app_settings.RECOVERY_CODES_SHOW_ONCE
        ret["is_mfa_enabled"] = is_mfa_enabled(authenticated_user(self.request))
        return ret


index = IndexView.as_view()


@method_decorator(
    login_stage_required(stage=TrustStage.key, redirect_urlname="account_login"),
    name="dispatch",
)
class TrustView(FormView):
    form_class = Form
    template_name = f"mfa/trust.{account_settings.TEMPLATE_EXTENSION}"

    def form_valid(self, form) -> HttpResponse:
        do_trust = self.request.POST.get("action") == "trust"
        stage = self.request._login_stage  # type:ignore[attr-defined]
        response = stage.exit()
        if do_trust:
            trust_.trust_browser(self.request, stage.login.user, response)
        return response

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        ret.update(get_entrance_context_data(self.request))
        now = timezone.now()
        ret["trust_from"] = now
        ret["trust_until"] = now + app_settings.TRUST_COOKIE_AGE
        return ret


trust = TrustView.as_view()

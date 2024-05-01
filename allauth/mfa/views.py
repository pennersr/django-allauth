import base64

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from allauth.account import app_settings as account_settings
from allauth.account.decorators import reauthentication_required
from allauth.account.stages import LoginStageController
from allauth.account.views import BaseReauthenticateView
from allauth.mfa import app_settings, totp
from allauth.mfa.adapter import get_adapter
from allauth.mfa.forms import (
    ActivateTOTPForm,
    AuthenticateForm,
    DeactivateTOTPForm,
    GenerateRecoveryCodesForm,
    ReauthenticateForm,
)
from allauth.mfa.internal import flows
from allauth.mfa.models import Authenticator
from allauth.mfa.stages import AuthenticateStage
from allauth.mfa.utils import is_mfa_enabled
from allauth.utils import get_form_class


class AuthenticateView(FormView):
    form_class = AuthenticateForm
    template_name = "mfa/authenticate." + account_settings.TEMPLATE_EXTENSION

    def dispatch(self, request, *args, **kwargs):
        self.stage = LoginStageController.enter(request, AuthenticateStage.key)
        if not self.stage or not is_mfa_enabled(
            self.stage.login.user, [Authenticator.Type.TOTP]
        ):
            return HttpResponseRedirect(reverse("account_login"))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.stage.login.user
        return ret

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "authenticate", self.form_class)

    def form_valid(self, form):
        form.save()
        return self.stage.exit()


authenticate = AuthenticateView.as_view()


@method_decorator(login_required, name="dispatch")
class ReauthenticateView(BaseReauthenticateView):
    form_class = ReauthenticateForm
    template_name = "mfa/reauthenticate." + account_settings.TEMPLATE_EXTENSION

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "reauthenticate", self.form_class)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


reauthenticate = ReauthenticateView.as_view()


@method_decorator(login_required, name="dispatch")
class IndexView(TemplateView):
    template_name = "mfa/index." + account_settings.TEMPLATE_EXTENSION

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        authenticators = {
            auth.type: auth.wrap()
            for auth in Authenticator.objects.filter(user=self.request.user)
        }
        ret["authenticators"] = authenticators
        ret["MFA_SUPPORTED_TYPES"] = app_settings.SUPPORTED_TYPES
        ret["is_mfa_enabled"] = is_mfa_enabled(self.request.user)
        return ret


index = IndexView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class ActivateTOTPView(FormView):
    form_class = ActivateTOTPForm
    template_name = "mfa/totp/activate_form." + account_settings.TEMPLATE_EXTENSION

    def dispatch(self, request, *args, **kwargs):
        if is_mfa_enabled(request.user, [Authenticator.Type.TOTP]):
            return HttpResponseRedirect(reverse("mfa_deactivate_totp"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        adapter = get_adapter()
        totp_url = totp.build_totp_url(
            adapter.get_totp_label(self.request.user),
            adapter.get_totp_issuer(),
            ret["form"].secret,
        )
        totp_svg = totp.build_totp_svg(totp_url)
        base64_data = base64.b64encode(totp_svg.encode("utf8")).decode("utf-8")
        totp_data_uri = f"data:image/svg+xml;base64,{base64_data}"
        ret.update(
            {
                "totp_svg": totp_svg,
                "totp_svg_data_uri": totp_data_uri,
                "totp_url": totp_url,
            }
        )
        return ret

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "activate_totp", self.form_class)

    def get_success_url(self):
        if Authenticator.Type.RECOVERY_CODES in app_settings.SUPPORTED_TYPES:
            return reverse("mfa_view_recovery_codes")
        return reverse("mfa_index")

    def form_valid(self, form):
        flows.totp.activate_totp(self.request, form)
        return super().form_valid(form)


activate_totp = ActivateTOTPView.as_view()


@method_decorator(login_required, name="dispatch")
class DeactivateTOTPView(FormView):
    form_class = DeactivateTOTPForm
    template_name = "mfa/totp/deactivate_form." + account_settings.TEMPLATE_EXTENSION
    success_url = reverse_lazy("mfa_index")

    def dispatch(self, request, *args, **kwargs):
        self.authenticator = get_object_or_404(
            Authenticator,
            user=self.request.user,
            type=Authenticator.Type.TOTP,
        )
        if not is_mfa_enabled(request.user, [Authenticator.Type.TOTP]):
            return HttpResponseRedirect(reverse("mfa_activate_totp"))
        return self._dispatch(request, *args, **kwargs)

    @method_decorator(reauthentication_required)
    def _dispatch(self, request, *args, **kwargs):
        """There's no point to reauthenticate when MFA is not enabled, so the
        `is_mfa_enabled` chheck needs to go first, which is why we cannot slap a
        `reauthentication_required` decorator on the `dispatch` directly.
        """
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["authenticator"] = self.authenticator
        # The deactivation form does not require input, yet, can generate
        # validation errors in case deactivation is not allowed. We want to
        # immediately present such errors even before the user actually posts
        # the form, which is why we put an empty data payload in here.
        ret.setdefault("data", {})
        return ret

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "deactivate_totp", self.form_class)

    def form_valid(self, form):
        flows.totp.deactivate_totp(self.request, self.authenticator)
        return super().form_valid(form)


deactivate_totp = DeactivateTOTPView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class GenerateRecoveryCodesView(FormView):
    form_class = GenerateRecoveryCodesForm
    template_name = "mfa/recovery_codes/generate." + account_settings.TEMPLATE_EXTENSION
    success_url = reverse_lazy("mfa_view_recovery_codes")

    def form_valid(self, form):
        flows.recovery_codes.generate_recovery_codes(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        unused_codes = []
        authenticator = Authenticator.objects.filter(
            user=self.request.user, type=Authenticator.Type.RECOVERY_CODES
        ).first()
        if authenticator:
            unused_codes = authenticator.wrap().get_unused_codes()
        ret["unused_code_count"] = len(unused_codes)
        return ret

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret


generate_recovery_codes = GenerateRecoveryCodesView.as_view()


class DownloadRecoveryCodesView(TemplateView):
    template_name = "mfa/recovery_codes/download.txt"
    content_type = "text/plain"

    def dispatch(self, request, *args, **kwargs):
        self.authenticator = flows.recovery_codes.view_recovery_codes(self.request)
        if not self.authenticator:
            raise Http404()
        self.unused_codes = self.authenticator.wrap().get_unused_codes()
        if not self.unused_codes:
            return Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret["unused_codes"] = self.unused_codes
        return ret

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Disposition"] = 'attachment; filename="recovery-codes.txt"'
        return response


download_recovery_codes = DownloadRecoveryCodesView.as_view()


class ViewRecoveryCodesView(TemplateView):
    template_name = "mfa/recovery_codes/index." + account_settings.TEMPLATE_EXTENSION

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        authenticator = flows.recovery_codes.view_recovery_codes(self.request)
        if not authenticator:
            raise Http404()
        ret.update(
            {
                "unused_codes": authenticator.wrap().get_unused_codes(),
                "total_count": app_settings.RECOVERY_CODE_COUNT,
            }
        )
        return ret


view_recovery_codes = ViewRecoveryCodesView.as_view()

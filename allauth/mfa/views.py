from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.decorators import reauthentication_required
from allauth.account.stages import LoginStageController
from allauth.mfa import app_settings, totp
from allauth.mfa.adapter import get_adapter
from allauth.mfa.forms import ActivateTOTPForm, AuthenticateForm
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes import RecoveryCodes
from allauth.mfa.stages import AuthenticateStage
from allauth.mfa.utils import is_mfa_enabled


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

    def form_valid(self, form):
        return self.stage.exit()


authenticate = AuthenticateView.as_view()


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
        return ret


index = IndexView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class ActivateTOTPView(FormView):
    form_class = ActivateTOTPForm
    template_name = "mfa/totp/activate_form." + account_settings.TEMPLATE_EXTENSION
    success_url = reverse_lazy("mfa_view_recovery_codes")

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
        ret.update(
            {
                "totp_svg": totp_svg,
                "totp_url": totp_url,
            }
        )
        return ret

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def form_valid(self, form):
        totp.TOTP.activate(self.request.user, form.secret)
        RecoveryCodes.activate(self.request.user)
        adapter = get_account_adapter(self.request)
        adapter.add_message(
            self.request, messages.SUCCESS, "mfa/messages/totp_activated.txt"
        )
        return super().form_valid(form)


activate_totp = ActivateTOTPView.as_view()


@method_decorator(login_required, name="dispatch")
class DeactivateTOTPView(FormView):
    form_class = forms.Form
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

    def form_valid(self, form):
        self.authenticator.wrap().deactivate()
        adapter = get_account_adapter(self.request)
        adapter.add_message(
            self.request, messages.SUCCESS, "mfa/messages/totp_deactivated.txt"
        )
        return super().form_valid(form)


deactivate_totp = DeactivateTOTPView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class GenerateRecoveryCodesView(FormView):
    form_class = forms.Form
    template_name = "mfa/recovery_codes/generate." + account_settings.TEMPLATE_EXTENSION
    success_url = reverse_lazy("mfa_view_recovery_codes")

    def form_valid(self, form):
        Authenticator.objects.filter(
            user=self.request.user, type=Authenticator.Type.RECOVERY_CODES
        ).delete()
        RecoveryCodes.activate(self.request.user)
        adapter = get_account_adapter(self.request)
        adapter.add_message(
            self.request, messages.SUCCESS, "mfa/messages/recovery_codes_generated.txt"
        )
        return super().form_valid(form)


generate_recovery_codes = GenerateRecoveryCodesView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class DownloadRecoveryCodesView(TemplateView):
    template_name = "mfa/recovery_codes/download.txt"
    content_type = "text/plain"

    def dispatch(self, request, *args, **kwargs):
        self.authenticator = get_object_or_404(
            Authenticator,
            user=self.request.user,
            type=Authenticator.Type.RECOVERY_CODES,
        )
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


@method_decorator(reauthentication_required, name="dispatch")
class ViewRecoveryCodesView(TemplateView):
    template_name = "mfa/recovery_codes/index." + account_settings.TEMPLATE_EXTENSION

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        authenticator = get_object_or_404(
            Authenticator,
            user=self.request.user,
            type=Authenticator.Type.RECOVERY_CODES,
        )
        ret.update(
            {
                "unused_codes": authenticator.wrap().get_unused_codes(),
                "total_count": app_settings.RECOVERY_CODE_COUNT,
            }
        )
        return ret


view_recovery_codes = ViewRecoveryCodesView.as_view()

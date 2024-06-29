import base64

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from allauth.account import app_settings as account_settings
from allauth.account.decorators import reauthentication_required
from allauth.mfa import app_settings
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.forms import ActivateTOTPForm, DeactivateTOTPForm
from allauth.mfa.totp.internal import flows
from allauth.mfa.utils import is_mfa_enabled
from allauth.utils import get_form_class


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
        totp_url = adapter.build_totp_url(
            self.request.user,
            ret["form"].secret,
        )
        totp_svg = adapter.build_totp_svg(totp_url)
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
        if self.did_generate_recovery_codes:
            return reverse("mfa_view_recovery_codes")
        return reverse("mfa_index")

    def form_valid(self, form):
        totp_auth, rc_auth = flows.activate_totp(self.request, form)
        self.did_generate_recovery_codes = bool(rc_auth)
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
        `is_mfa_enabled` check needs to go first, which is why we cannot slap a
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
        flows.deactivate_totp(self.request, self.authenticator)
        return super().form_valid(form)


deactivate_totp = DeactivateTOTPView.as_view()

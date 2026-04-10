from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from allauth.account import app_settings as account_settings
from allauth.account.decorators import reauthentication_required
from allauth.core.internal.httpkit import authenticated_user
from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.forms import GenerateRecoveryCodesForm
from allauth.mfa.recovery_codes.internal import flows
from allauth.utils import get_form_class


@method_decorator(reauthentication_required, name="dispatch")
class GenerateRecoveryCodesView(FormView):
    form_class = GenerateRecoveryCodesForm
    template_name = f"mfa/recovery_codes/generate.{account_settings.TEMPLATE_EXTENSION}"
    success_url = reverse_lazy("mfa_view_recovery_codes")

    def form_valid(self, form) -> HttpResponse:
        flows.generate_recovery_codes(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        unused_codes = []
        authenticator = Authenticator.objects.filter(
            user_id=authenticated_user(self.request).pk,
            type=Authenticator.Type.RECOVERY_CODES,
        ).first()
        if authenticator:
            unused_codes = authenticator.wrap().get_unused_codes()
        ret["unused_code_count"] = len(unused_codes)
        return ret

    def get_form_kwargs(self) -> dict:
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def get_form_class(self):
        return get_form_class(
            app_settings.FORMS, "generate_recovery_codes", self.form_class
        )


generate_recovery_codes = GenerateRecoveryCodesView.as_view()


@method_decorator(login_required, name="dispatch")
@method_decorator(never_cache, name="dispatch")
class DownloadRecoveryCodesView(TemplateView):
    template_name = "mfa/recovery_codes/download.txt"
    content_type = "text/plain"

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        recovery_codes, can_view = flows.view_recovery_codes(self.request)
        if not recovery_codes:
            raise Http404()
        if not can_view:
            raise PermissionDenied
        self.authenticator = recovery_codes.instance
        self.unused_codes = recovery_codes.get_unused_codes()
        if not self.unused_codes:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        ret["unused_codes"] = self.unused_codes
        return ret

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Disposition"] = 'attachment; filename="recovery-codes.txt"'
        return response


download_recovery_codes = DownloadRecoveryCodesView.as_view()


@method_decorator(login_required, name="dispatch")
class ViewRecoveryCodesView(TemplateView):
    template_name = f"mfa/recovery_codes/index.{account_settings.TEMPLATE_EXTENSION}"

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        recovery_codes, can_view = flows.view_recovery_codes(self.request)
        if not recovery_codes:
            raise Http404()
        unused_codes = recovery_codes.get_unused_codes()
        if not can_view:
            # Prevent accidental leakage into templates at all costs.
            unused_codes = ["****" for _ in unused_codes]
        ret.update(
            {
                "unused_codes": unused_codes,
                "can_view_codes": can_view,
                "can_download_codes": not app_settings.RECOVERY_CODES_SHOW_ONCE
                and len(unused_codes) > 0,
                "total_count": app_settings.RECOVERY_CODE_COUNT,
                "MFA_RECOVERY_CODES_SHOW_ONCE": app_settings.RECOVERY_CODES_SHOW_ONCE,
                "can_generate_codes": not app_settings.RECOVERY_CODES_SHOW_ONCE
                or not can_view,
            }
        )
        return ret


view_recovery_codes = ViewRecoveryCodesView.as_view()

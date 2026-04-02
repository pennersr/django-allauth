from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.decorators import reauthentication_required
from allauth.account.internal.decorators import login_stage_required
from allauth.account.internal.templatekit import get_entrance_context_data
from allauth.account.mixins import NextRedirectMixin, RedirectAuthenticatedUserMixin
from allauth.account.models import Login
from allauth.account.views import BaseReauthenticateView
from allauth.mfa import app_settings
from allauth.mfa.internal.flows.add import redirect_if_add_not_allowed
from allauth.mfa.models import Authenticator
from allauth.mfa.webauthn.forms import (
    AddWebAuthnForm,
    EditWebAuthnForm,
    LoginWebAuthnForm,
    ReauthenticateWebAuthnForm,
    SignupWebAuthnForm,
)
from allauth.mfa.webauthn.internal import auth, flows
from allauth.mfa.webauthn.stages import PasskeySignupStage
from allauth.utils import get_form_class


@method_decorator(redirect_if_add_not_allowed, name="dispatch")
@method_decorator(reauthentication_required, name="dispatch")
class AddWebAuthnView(FormView):
    form_class = AddWebAuthnForm
    template_name = f"mfa/webauthn/add_form.{account_settings.TEMPLATE_EXTENSION}"

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data()
        creation_options = auth.begin_registration(self.request.user, False)
        ret["js_data"] = {"creation_options": creation_options}
        return ret

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "add_webauthn", self.form_class)

    def get_form_kwargs(self) -> dict:
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def get_success_url(self) -> str:
        if self.did_generate_recovery_codes:
            return reverse("mfa_view_recovery_codes")
        return reverse("mfa_index")

    def form_valid(self, form) -> HttpResponse:
        auth, rc_auth = flows.add_authenticator(
            self.request,
            name=form.cleaned_data["name"],
            credential=form.cleaned_data["credential"],
        )
        self.did_generate_recovery_codes = bool(rc_auth)
        return super().form_valid(form)


add_webauthn = AddWebAuthnView.as_view()


@method_decorator(login_required, name="dispatch")
class ListWebAuthnView(ListView):
    template_name = (
        f"mfa/webauthn/authenticator_list.{account_settings.TEMPLATE_EXTENSION}"
    )
    context_object_name = "authenticators"

    def get_queryset(self):
        return Authenticator.objects.filter(
            user=self.request.user, type=Authenticator.Type.WEBAUTHN
        )


list_webauthn = ListWebAuthnView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class RemoveWebAuthnView(NextRedirectMixin, DeleteView):
    object: Authenticator  # https://github.com/typeddjango/django-stubs/issues/1227
    template_name = (
        "mfa/webauthn/authenticator_confirm_delete."
        + account_settings.TEMPLATE_EXTENSION
    )
    success_url = reverse_lazy("mfa_list_webauthn")

    def get_queryset(self):
        return Authenticator.objects.filter(
            user=self.request.user, type=Authenticator.Type.WEBAUTHN
        )

    def form_valid(self, form) -> HttpResponse:
        authenticator = self.get_object()
        flows.remove_authenticator(self.request, authenticator)
        return HttpResponseRedirect(self.get_success_url())


remove_webauthn = RemoveWebAuthnView.as_view()


class LoginWebAuthnView(RedirectAuthenticatedUserMixin, FormView):
    form_class = LoginWebAuthnForm

    def get(self, request, *args, **kwargs) -> HttpResponse:
        if get_account_adapter().is_ajax(request):
            request_options = auth.begin_authentication(user=None)
            data = {"request_options": request_options}
            return JsonResponse(data)
        return HttpResponseRedirect(reverse("account_login"))

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "login_webauthn", self.form_class)

    def form_invalid(self, form) -> HttpResponse:
        for message in form.errors.get("credential", []):
            get_account_adapter().add_message(
                self.request, messages.ERROR, message=message
            )
        return HttpResponseRedirect(reverse("account_login"))

    def form_valid(self, form) -> HttpResponse:
        authenticator = form.cleaned_data["credential"]
        redirect_url = None
        login = Login(user=authenticator.user, redirect_url=redirect_url)
        return flows.perform_passwordless_login(self.request, authenticator, login)

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        ret.update(get_entrance_context_data(self.request))
        return ret


login_webauthn = LoginWebAuthnView.as_view()


@method_decorator(login_required, name="dispatch")
class ReauthenticateWebAuthnView(BaseReauthenticateView):
    form_class = ReauthenticateWebAuthnForm
    template_name = f"mfa/webauthn/reauthenticate.{account_settings.TEMPLATE_EXTENSION}"

    def get_form_class(self):
        return get_form_class(
            app_settings.FORMS, "reauthenticate_webauthn", self.form_class
        )

    def get_form_kwargs(self) -> dict:
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def form_invalid(self, form) -> HttpResponse:
        for message in form.errors.get("credential", []):
            get_account_adapter().add_message(
                self.request, messages.ERROR, message=message
            )
        return HttpResponseRedirect(reverse("account_login"))

    def form_valid(self, form) -> HttpResponse:
        authenticator = form.cleaned_data["credential"]
        flows.reauthenticate(self.request, authenticator)
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data()
        request_options = auth.begin_authentication(self.request.user)
        ret["js_data"] = {"request_options": request_options}
        return ret


reauthenticate_webauthn = ReauthenticateWebAuthnView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class EditWebAuthnView(NextRedirectMixin, UpdateView):
    form_class = EditWebAuthnForm
    template_name = f"mfa/webauthn/edit_form.{account_settings.TEMPLATE_EXTENSION}"
    success_url = reverse_lazy("mfa_list_webauthn")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "edit_webauthn", self.form_class)

    def get_queryset(self):
        return Authenticator.objects.filter(
            user=self.request.user, type=Authenticator.Type.WEBAUTHN
        )


edit_webauthn = EditWebAuthnView.as_view()


@method_decorator(
    login_stage_required(
        stage=PasskeySignupStage.key, redirect_urlname="account_signup"
    ),
    name="dispatch",
)
class SignupWebAuthnView(FormView):
    form_class = SignupWebAuthnForm
    template_name = f"mfa/webauthn/signup_form.{account_settings.TEMPLATE_EXTENSION}"

    @property
    def _login_stage(self):
        return self.request._login_stage

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data()
        ret.update(get_entrance_context_data(self.request))
        stage = self._login_stage
        creation_options = auth.begin_registration(stage.login.user, True)
        ret["js_data"] = {"creation_options": creation_options}
        return ret

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "signup_webauthn", self.form_class)

    def get_form_kwargs(self) -> dict:
        ret = super().get_form_kwargs()
        stage = self._login_stage
        ret["user"] = stage.login.user
        return ret

    def form_valid(self, form) -> HttpResponse:
        stage = self._login_stage
        flows.signup_authenticator(
            self.request,
            user=stage.login.user,
            name=form.cleaned_data["name"],
            credential=form.cleaned_data["credential"],
        )
        return stage.exit()


signup_webauthn = SignupWebAuthnView.as_view()

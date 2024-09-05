from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.decorators import reauthentication_required
from allauth.account.mixins import NextRedirectMixin
from allauth.account.models import Login
from allauth.account.views import BaseReauthenticateView
from allauth.mfa.internal.flows.add import redirect_if_add_not_allowed
from allauth.mfa.models import Authenticator
from allauth.mfa.webauthn.forms import (
    AddWebAuthnForm,
    EditWebAuthnForm,
    LoginWebAuthnForm,
    ReauthenticateWebAuthnForm,
)
from allauth.mfa.webauthn.internal import auth, flows


@method_decorator(redirect_if_add_not_allowed, name="dispatch")
@method_decorator(reauthentication_required, name="dispatch")
class AddWebAuthnView(FormView):
    form_class = AddWebAuthnForm
    template_name = "mfa/webauthn/add_form." + account_settings.TEMPLATE_EXTENSION

    def get_context_data(self, **kwargs):
        ret = super().get_context_data()
        creation_options = auth.begin_registration(self.request.user, False)
        ret["js_data"] = {"creation_options": creation_options}
        return ret

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def get_success_url(self):
        if self.did_generate_recovery_codes:
            return reverse("mfa_view_recovery_codes")
        return reverse("mfa_index")

    def form_valid(self, form):
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
        "mfa/webauthn/authenticator_list." + account_settings.TEMPLATE_EXTENSION
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

    def form_valid(self, form):
        authenticator = self.get_object()
        flows.remove_authenticator(self.request, authenticator)
        return HttpResponseRedirect(self.get_success_url())


remove_webauthn = RemoveWebAuthnView.as_view()


class LoginWebAuthnView(FormView):
    form_class = LoginWebAuthnForm

    def get(self, request, *args, **kwargs):
        if get_account_adapter().is_ajax(request):
            request_options = auth.begin_authentication(user=None)
            data = {"request_options": request_options}
            return JsonResponse(data)
        return HttpResponseRedirect(reverse("account_login"))

    def form_invalid(self, form):
        for message in form.errors.get("credential", []):
            get_account_adapter().add_message(
                self.request, messages.ERROR, message=message
            )
        return HttpResponseRedirect(reverse("account_login"))

    def form_valid(self, form):
        authenticator = form.cleaned_data["credential"]
        redirect_url = None
        login = Login(user=authenticator.user, redirect_url=redirect_url)
        return flows.perform_passwordless_login(self.request, authenticator, login)


login_webauthn = LoginWebAuthnView.as_view()


@method_decorator(login_required, name="dispatch")
class ReauthenticateWebAuthnView(BaseReauthenticateView):
    form_class = ReauthenticateWebAuthnForm
    template_name = "mfa/webauthn/reauthenticate." + account_settings.TEMPLATE_EXTENSION

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def form_invalid(self, form):
        for message in form.errors.get("credential", []):
            get_account_adapter().add_message(
                self.request, messages.ERROR, message=message
            )
        return HttpResponseRedirect(reverse("account_login"))

    def form_valid(self, form):
        authenticator = form.cleaned_data["credential"]
        flows.reauthenticate(self.request, authenticator)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data()
        request_options = auth.begin_authentication(self.request.user)
        ret["js_data"] = {"request_options": request_options}
        return ret


reauthenticate_webauthn = ReauthenticateWebAuthnView.as_view()


@method_decorator(reauthentication_required, name="dispatch")
class EditWebAuthnView(NextRedirectMixin, UpdateView):
    form_class = EditWebAuthnForm
    template_name = "mfa/webauthn/edit_form." + account_settings.TEMPLATE_EXTENSION
    success_url = reverse_lazy("mfa_list_webauthn")

    def get_queryset(self):
        return Authenticator.objects.filter(
            user=self.request.user, type=Authenticator.Type.WEBAUTHN
        )


edit_webauthn = EditWebAuthnView.as_view()

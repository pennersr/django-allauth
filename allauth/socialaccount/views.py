from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from allauth.account.internal.decorators import login_not_required
from allauth.account.internal.templatekit import get_entrance_context_data
from allauth.socialaccount.forms import DisconnectForm, SignupForm
from allauth.socialaccount.internal import flows
from allauth.socialaccount.models import SocialAccount

from ..account import app_settings as account_settings
from ..account.views import (
    AjaxCapableProcessFormViewMixin,
    CloseableSignupMixin,
    RedirectAuthenticatedUserMixin,
)
from ..utils import get_form_class
from . import app_settings
from .adapter import get_adapter


class SignupView(
    RedirectAuthenticatedUserMixin,
    CloseableSignupMixin,
    AjaxCapableProcessFormViewMixin,
    FormView,
):
    form_class = SignupForm
    template_name = f"socialaccount/signup.{account_settings.TEMPLATE_EXTENSION}"

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "signup", self.form_class)

    @method_decorator(login_not_required)
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        self.sociallogin = flows.signup.get_pending_signup(request)
        if not self.sociallogin:
            return HttpResponseRedirect(reverse("account_login"))
        return super().dispatch(request, *args, **kwargs)

    def is_open(self) -> bool:
        return get_adapter(self.request).is_open_for_signup(
            self.request, self.sociallogin
        )

    def get_form_kwargs(self) -> dict:
        ret = super().get_form_kwargs()
        ret["sociallogin"] = self.sociallogin
        return ret

    def form_valid(self, form) -> HttpResponse:
        return flows.signup.signup_by_form(self.request, self.sociallogin, form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret.update(get_entrance_context_data(self.request))
        ret.update(
            dict(
                account=self.sociallogin.account,
            )
        )
        return ret

    def get_authenticated_redirect_url(self) -> str:
        return reverse("socialaccount_connections")


signup = SignupView.as_view()


@method_decorator(login_not_required, name="dispatch")
class LoginCancelledView(TemplateView):
    template_name = (
        f"socialaccount/login_cancelled.{account_settings.TEMPLATE_EXTENSION}"
    )

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        ret.update(get_entrance_context_data(self.request))
        return ret


login_cancelled = LoginCancelledView.as_view()


class LoginErrorView(TemplateView):
    template_name = (
        f"socialaccount/authentication_error.{account_settings.TEMPLATE_EXTENSION}"
    )

    def get(self, request, *args, **kwargs) -> HttpResponse:
        return self.render_to_response(
            self.get_context_data(**kwargs),
            status=HTTPStatus.UNAUTHORIZED,
        )

    def get_context_data(self, **kwargs) -> dict:
        ret = super().get_context_data(**kwargs)
        ret.update(get_entrance_context_data(self.request))
        return ret


login_error = LoginErrorView.as_view()


@method_decorator(login_required, name="dispatch")
class ConnectionsView(AjaxCapableProcessFormViewMixin, FormView):
    template_name = f"socialaccount/connections.{account_settings.TEMPLATE_EXTENSION}"
    form_class = DisconnectForm
    success_url = reverse_lazy("socialaccount_connections")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "disconnect", self.form_class)

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        form.save()
        return super().form_valid(form)

    def get_ajax_data(self):
        account_data = []
        for account in SocialAccount.objects.filter(user=self.request.user):
            provider_account = account.get_provider_account()
            account_data.append(
                {
                    "id": account.pk,
                    "provider": account.provider,
                    "name": provider_account.to_str(),
                }
            )
        return {"socialaccounts": account_data}


connections = ConnectionsView.as_view()

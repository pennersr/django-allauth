from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.html import format_html

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal import flows
from allauth.account.utils import (
    get_login_redirect_url,
    get_next_redirect_url,
    passthrough_next_redirect_url,
)
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.utils import get_request_param


def _ajax_response(request, response, form=None, data=None):
    adapter = get_adapter()
    if adapter.is_ajax(request):
        if isinstance(response, HttpResponseRedirect) or isinstance(
            response, HttpResponsePermanentRedirect
        ):
            redirect_to = response["Location"]
        else:
            redirect_to = None
        response = adapter.ajax_response(
            request, response, form=form, data=data, redirect_to=redirect_to
        )
    return response


class RedirectAuthenticatedUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and app_settings.AUTHENTICATED_LOGIN_REDIRECTS:
            redirect_to = self.get_authenticated_redirect_url()
            response = HttpResponseRedirect(redirect_to)
            return _ajax_response(request, response)
        else:
            response = super().dispatch(request, *args, **kwargs)
        return response

    def get_authenticated_redirect_url(self):
        redirect_field_name = self.redirect_field_name
        return get_login_redirect_url(
            self.request,
            url=self.get_success_url(),
            redirect_field_name=redirect_field_name,
        )


class LogoutFunctionalityMixin:
    def logout(self):
        flows.logout.logout(self.request)


class AjaxCapableProcessFormViewMixin:
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        form = self.get_form()
        return _ajax_response(
            self.request, response, form=form, data=self._get_ajax_data_if()
        )

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            response = self.form_valid(form)
        else:
            response = self.form_invalid(form)
        return _ajax_response(
            self.request, response, form=form, data=self._get_ajax_data_if()
        )

    def get_form(self, form_class=None):
        form = getattr(self, "_cached_form", None)
        if form is None:
            form = super().get_form(form_class)
            self._cached_form = form
        return form

    def _get_ajax_data_if(self):
        return (
            self.get_ajax_data()
            if get_adapter(self.request).is_ajax(self.request)
            else None
        )

    def get_ajax_data(self):
        return None


class CloseableSignupMixin:
    template_name_signup_closed = (
        "account/signup_closed." + app_settings.TEMPLATE_EXTENSION
    )

    def dispatch(self, request, *args, **kwargs):
        try:
            if not self.is_open():
                return self.closed()
        except ImmediateHttpResponse as e:
            return e.response
        return super().dispatch(request, *args, **kwargs)

    def is_open(self):
        return get_adapter(self.request).is_open_for_signup(self.request)

    def closed(self):
        response_kwargs = {
            "request": self.request,
            "template": self.template_name_signup_closed,
        }
        return self.response_class(**response_kwargs)


class NextRedirectMixin:
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        redirect_field_value = get_request_param(self.request, self.redirect_field_name)
        ret.update(
            {
                "redirect_field_name": self.redirect_field_name,
                "redirect_field_value": redirect_field_value,
                "redirect_field": format_html(
                    '<input type="hidden" name="{}" value="{}">',
                    self.redirect_field_name,
                    redirect_field_value,
                )
                if redirect_field_value
                else "",
            }
        )
        return ret

    def get_success_url(self):
        """
        We're in a mixin, so we cannot rely on the fact that our super() has a get_success_url.
        Also, we want to check for -- in this order:
        1) The `?next=/foo`
        2) The `get_succes_url()` if available.
        3) The `.success_url` if available.
        4) A fallback default success URL: `get_default_success_url()`.
        """
        url = self.get_next_url()
        if url:
            return url

        if not url:
            if hasattr(super(), "get_success_url"):
                try:
                    url = super().get_success_url()
                except ImproperlyConfigured:
                    # Django's default get_success_url() checks self.succes_url,
                    # and throws this if that is not set. Yet, in our case, we
                    # want to fallback to the default.
                    pass
            elif hasattr(self, "success_url"):
                url = self.success_url
                if url:
                    url = str(url)  # reverse_lazy
        if not url:
            url = self.get_default_success_url()
        return url

    def get_default_success_url(self):
        return None

    def get_next_url(self):
        return get_next_redirect_url(self.request, self.redirect_field_name)

    def passthrough_next_url(self, url):
        return passthrough_next_redirect_url(
            self.request, url, self.redirect_field_name
        )

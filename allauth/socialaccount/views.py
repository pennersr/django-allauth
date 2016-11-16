from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from ..compat import reverse, reverse_lazy
from ..account import app_settings as account_settings
from ..account.views import (AjaxCapableProcessFormViewMixin,
                             CloseableSignupMixin,
                             RedirectAuthenticatedUserMixin)
from ..account.adapter import get_adapter as get_account_adapter
from ..utils import get_form_class, get_current_site

from .adapter import get_adapter
from .models import SocialLogin
from .forms import DisconnectForm, SignupForm
from . import helpers
from . import app_settings


class SignupView(RedirectAuthenticatedUserMixin, CloseableSignupMixin,
                 AjaxCapableProcessFormViewMixin, FormView):
    form_class = SignupForm
    template_name = (
        'socialaccount/signup.' + account_settings.TEMPLATE_EXTENSION)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS,
                              'signup',
                              self.form_class)

    def dispatch(self, request, *args, **kwargs):
        self.sociallogin = None
        data = request.session.get('socialaccount_sociallogin')
        if data:
            self.sociallogin = SocialLogin.deserialize(data)
        if not self.sociallogin:
            return HttpResponseRedirect(reverse('account_login'))
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def is_open(self):
        return get_adapter(self.request).is_open_for_signup(
            self.request,
            self.sociallogin)

    def get_form_kwargs(self):
        ret = super(SignupView, self).get_form_kwargs()
        ret['sociallogin'] = self.sociallogin
        return ret

    def form_valid(self, form):
        form.save(self.request)
        return helpers.complete_social_signup(self.request,
                                              self.sociallogin)

    def get_context_data(self, **kwargs):
        ret = super(SignupView, self).get_context_data(**kwargs)
        ret.update(dict(site=get_current_site(self.request),
                        account=self.sociallogin.account))
        return ret

    def get_authenticated_redirect_url(self):
        return reverse(connections)


signup = SignupView.as_view()


class LoginCancelledView(TemplateView):
    template_name = (
        "socialaccount/login_cancelled." + account_settings.TEMPLATE_EXTENSION)


login_cancelled = LoginCancelledView.as_view()


class LoginErrorView(TemplateView):
    template_name = (
        "socialaccount/authentication_error." +
        account_settings.TEMPLATE_EXTENSION)


login_error = LoginErrorView.as_view()


class ConnectionsView(AjaxCapableProcessFormViewMixin, FormView):
    template_name = (
        "socialaccount/connections." +
        account_settings.TEMPLATE_EXTENSION)
    form_class = DisconnectForm
    success_url = reverse_lazy("socialaccount_connections")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS,
                              'disconnect',
                              self.form_class)

    def get_form_kwargs(self):
        kwargs = super(ConnectionsView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        get_account_adapter().add_message(self.request,
                                          messages.INFO,
                                          'socialaccount/messages/'
                                          'account_disconnected.txt')
        form.save()
        return super(ConnectionsView, self).form_valid(form)


connections = login_required(ConnectionsView.as_view())

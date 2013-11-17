from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.http import base36_to_int
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect

from ..exceptions import ImmediateHttpResponse
from ..utils import get_user_model

from .utils import (get_next_redirect_url, complete_signup,
                    get_login_redirect_url,
                    passthrough_next_redirect_url)
from .forms import AddEmailForm, ChangePasswordForm
from .forms import LoginForm, ResetPasswordKeyForm
from .forms import ResetPasswordForm, SetPasswordForm, SignupForm
from .utils import sync_user_email_addresses
from .models import EmailAddress, EmailConfirmation

from . import signals
from . import app_settings

from .adapter import get_adapter

User = get_user_model()


class RedirectAuthenticatedUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        # WORKAROUND: https://code.djangoproject.com/ticket/19316
        self.request = request
        # (end WORKAROUND)
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_authenticated_redirect_url())
        return super(RedirectAuthenticatedUserMixin, self).dispatch(request,
                                                                    *args,
                                                                    **kwargs)

    def get_authenticated_redirect_url(self):
        redirect_field_name = self.redirect_field_name
        return get_login_redirect_url(self.request,
                                      url=self.get_success_url(),
                                      redirect_field_name=redirect_field_name)


class LoginView(RedirectAuthenticatedUserMixin, FormView):
    form_class = LoginForm
    template_name = "account/login.html"
    success_url = None
    redirect_field_name = "next"

    def form_valid(self, form):
        success_url = self.get_success_url()
        return form.login(self.request, redirect_url=success_url)

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (get_next_redirect_url(self.request,
                                     self.redirect_field_name)
               or self.success_url)
        return ret

    def get_context_data(self, **kwargs):
        ret = super(LoginView, self).get_context_data(**kwargs)
        signup_url = passthrough_next_redirect_url(self.request,
                                                   reverse("account_signup"),
                                                   self.redirect_field_name)
        redirect_field_value = self.request.REQUEST \
            .get(self.redirect_field_name)
        ret.update({"signup_url": signup_url,
                    "site": Site.objects.get_current(),
                    "redirect_field_name": self.redirect_field_name,
                    "redirect_field_value": redirect_field_value})
        return ret

login = LoginView.as_view()


class CloseableSignupMixin(object):
    template_name_signup_closed = "account/signup_closed.html"

    def dispatch(self, request, *args, **kwargs):
        # WORKAROUND: https://code.djangoproject.com/ticket/19316
        self.request = request
        # (end WORKAROUND)
        try:
            if not self.is_open():
                return self.closed()
        except ImmediateHttpResponse as e:
            return e.response
        return super(CloseableSignupMixin, self).dispatch(request,
                                                          *args,
                                                          **kwargs)

    def is_open(self):
        return get_adapter().is_open_for_signup(self.request)

    def closed(self):
        response_kwargs = {
            "request": self.request,
            "template": self.template_name_signup_closed,
        }
        return self.response_class(**response_kwargs)


class SignupView(RedirectAuthenticatedUserMixin, CloseableSignupMixin,
                 FormView):
    template_name = "account/signup.html"
    form_class = SignupForm
    redirect_field_name = "next"
    success_url = None

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (get_next_redirect_url(self.request,
                                     self.redirect_field_name)
               or self.success_url)
        return ret

    def form_valid(self, form):
        user = form.save(self.request)
        return complete_signup(self.request, user,
                               app_settings.EMAIL_VERIFICATION,
                               self.get_success_url())

    def get_context_data(self, **kwargs):
        form = kwargs['form']
        form.fields["email"].initial = self.request.session \
            .get('account_verified_email', None)
        ret = super(SignupView, self).get_context_data(**kwargs)
        login_url = passthrough_next_redirect_url(self.request,
                                                  reverse("account_login"),
                                                  self.redirect_field_name)
        redirect_field_name = self.redirect_field_name
        redirect_field_value = self.request.REQUEST.get(redirect_field_name)
        ret.update({"login_url": login_url,
                    "redirect_field_name": redirect_field_name,
                    "redirect_field_value": redirect_field_value})
        return ret

signup = SignupView.as_view()


class ConfirmEmailView(TemplateResponseMixin, View):

    def get_template_names(self):
        if self.request.method == 'POST':
            return ["account/email_confirmed.html"]
        else:
            return ["account/email_confirm.html"]

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            if app_settings.CONFIRM_EMAIL_ON_GET:
                return self.post(*args, **kwargs)
        except Http404:
            self.object = None
        ctx = self.get_context_data()
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        # Don't -- allauth doesn't tocuh is_active so that sys admin can
        # use it to block users et al
        #
        # user = confirmation.email_address.user
        # user.is_active = True
        # user.save()
        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'account/messages/email_confirmed.txt',
                                  {'email': confirmation.email_address.email})
        return redirect(redirect_url)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs["key"].lower())
        except EmailConfirmation.DoesNotExist:
            raise Http404()

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx["confirmation"] = self.object
        return ctx

    def get_redirect_url(self):
        return get_adapter().get_email_confirmation_redirect_url(self.request)

confirm_email = ConfirmEmailView.as_view()


class EmailView(FormView):
    template_name = "account/email.html"
    form_class = AddEmailForm
    success_url = reverse_lazy('account_email')

    def dispatch(self, request, *args, **kwargs):
        sync_user_email_addresses(request.user)
        return super(EmailView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(EmailView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        email_address = form.save(self.request)
        get_adapter().add_message(self.request,
                                  messages.INFO,
                                  'account/messages/'
                                  'email_confirmation_sent.txt',
                                  {'email': form.cleaned_data["email"]})
        signals.email_added.send(sender=self.request.user.__class__,
                                 request=self.request,
                                 user=self.request.user,
                                 email_address=email_address)
        return super(EmailView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        res = None
        if "action_add" in request.POST:
            res = super(EmailView, self).post(request, *args, **kwargs)
        elif request.POST.get("email"):
            if "action_send" in request.POST:
                res = self._action_send(request)
            elif "action_remove" in request.POST:
                res = self._action_remove(request)
            elif "action_primary" in request.POST:
                res = self._action_primary(request)
            # TODO: Ugly. But if we .get() here the email is used as
            # initial for the add form, whereas the user was not
            # interacting with that form..
            res = res or HttpResponseRedirect(reverse('account_email'))
        return res or self.get(request, *args, **kwargs)

    def _action_send(self, request, *args, **kwargs):
        email = request.POST["email"]
        try:
            email_address = EmailAddress.objects.get(
                user=request.user,
                email=email,
            )
            get_adapter().add_message(request,
                                      messages.INFO,
                                      'account/messages/'
                                      'email_confirmation_sent.txt',
                                      {'email': email})
            email_address.send_confirmation(request)
            return HttpResponseRedirect(self.get_success_url())
        except EmailAddress.DoesNotExist:
            pass

    def _action_remove(self, request, *args, **kwargs):
        email = request.POST["email"]
        try:
            email_address = EmailAddress.objects.get(
                user=request.user,
                email=email
            )
            if email_address.primary:
                get_adapter().add_message(request,
                                          messages.ERROR,
                                          'account/messages/'
                                          'cannot_delete_primary_email.txt',
                                          {"email": email})
            else:
                email_address.delete()
                signals.email_removed.send(sender=request.user.__class__,
                                           request=request,
                                           user=request.user,
                                           email_address=email_address)
                get_adapter().add_message(request,
                                          messages.SUCCESS,
                                          'account/messages/email_deleted.txt',
                                          {"email": email})
                return HttpResponseRedirect(self.get_success_url())
        except EmailAddress.DoesNotExist:
            pass

    def _action_primary(self, request, *args, **kwargs):
        email = request.POST["email"]
        try:
            email_address = EmailAddress.objects.get(
                user=request.user,
                email=email,
            )
            # Not primary=True -- Slightly different variation, don't
            # require verified unless moving from a verified
            # address. Ignore constraint if previous primary email
            # address is not verified.
            if not email_address.verified and \
                    EmailAddress.objects.filter(user=request.user,
                                                verified=True).exists():
                get_adapter().add_message(request,
                                          messages.ERROR,
                                          'account/messages/'
                                          'unverified_primary_email.txt')
            else:
                # Sending the old primary address to the signal
                # adds a db query.
                try:
                    from_email_address = EmailAddress.objects \
                        .get(user=request.user, primary=True)
                except EmailAddress.DoesNotExist:
                    from_email_address = None
                email_address.set_as_primary()
                get_adapter() \
                    .add_message(request,
                                 messages.SUCCESS,
                                 'account/messages/primary_email_set.txt')
                signals.email_changed \
                    .send(sender=request.user.__class__,
                          request=request,
                          user=request.user,
                          from_email_address=from_email_address,
                          to_email_address=email_address)
                return HttpResponseRedirect(self.get_success_url())
        except EmailAddress.DoesNotExist:
            pass

    def get_context_data(self, **kwargs):
        ret = super(EmailView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['add_email_form'] = ret.get('form')
        # (end NOTE)
        return ret

email = login_required(EmailView.as_view())


class PasswordChangeView(FormView):
    template_name = "account/password_change.html"
    form_class = ChangePasswordForm
    success_url = reverse_lazy("account_change_password")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_usable_password():
            return HttpResponseRedirect(reverse('account_set_password'))
        return super(PasswordChangeView, self).dispatch(request, *args,
                                                        **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'account/messages/password_changed.txt')
        signals.password_changed.send(sender=self.request.user.__class__,
                                      request=self.request,
                                      user=self.request.user)
        return super(PasswordChangeView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordChangeView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['password_change_form'] = ret.get('form')
        # (end NOTE)
        return ret

password_change = login_required(PasswordChangeView.as_view())


class PasswordSetView(FormView):
    template_name = "account/password_set.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("account_set_password")

    def dispatch(self, request, *args, **kwargs):
        if request.user.has_usable_password():
            return HttpResponseRedirect(reverse('account_change_password'))
        return super(PasswordSetView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordSetView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'account/messages/password_set.txt')
        signals.password_set.send(sender=self.request.user.__class__,
                                  request=self.request, user=self.request.user)
        return super(PasswordSetView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordSetView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['password_set_form'] = ret.get('form')
        # (end NOTE)
        return ret

password_set = login_required(PasswordSetView.as_view())


class PasswordResetView(FormView):
    template_name = "account/password_reset.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("account_reset_password_done")

    def form_valid(self, form):
        form.save()
        return super(PasswordResetView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordResetView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['password_reset_form'] = ret.get('form')
        # (end NOTE)
        return ret

password_reset = PasswordResetView.as_view()


class PasswordResetDoneView(TemplateView):
    template_name = "account/password_reset_done.html"

password_reset_done = PasswordResetDoneView.as_view()


class PasswordResetFromKeyView(FormView):
    template_name = "account/password_reset_from_key.html"
    form_class = ResetPasswordKeyForm
    token_generator = default_token_generator
    success_url = reverse_lazy("account_reset_password_from_key_done")

    def _get_user(self, uidb36):
        # pull out user
        try:
            uid_int = base36_to_int(uidb36)
        except ValueError:
            raise Http404
        return get_object_or_404(User, id=uid_int)

    def dispatch(self, request, uidb36, key, **kwargs):
        self.request = request
        self.uidb36 = uidb36
        self.key = key
        self.reset_user = self._get_user(uidb36)
        if not self.token_generator.check_token(self.reset_user, key):
            return self._response_bad_token(request, uidb36, key, **kwargs)
        else:
            return super(PasswordResetFromKeyView, self).dispatch(request,
                                                                  uidb36,
                                                                  key,
                                                                  **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordResetFromKeyView, self).get_form_kwargs()
        kwargs["user"] = self.reset_user
        kwargs["temp_key"] = self.key
        return kwargs

    def form_valid(self, form):
        form.save()
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'account/messages/password_changed.txt')
        signals.password_reset.send(sender=self.reset_user.__class__,
                                    request=self.request,
                                    user=self.reset_user)
        return super(PasswordResetFromKeyView, self).form_valid(form)

    def _response_bad_token(self, request, uidb36, key, **kwargs):
        return self.render_to_response(self.get_context_data(token_fail=True))

password_reset_from_key = PasswordResetFromKeyView.as_view()


class PasswordResetFromKeyDoneView(TemplateView):
    template_name = "account/password_reset_from_key_done.html"

password_reset_from_key_done = PasswordResetFromKeyDoneView.as_view()


class LogoutView(TemplateResponseMixin, View):

    template_name = "account/logout.html"
    redirect_field_name = "next"

    def get(self, *args, **kwargs):
        if app_settings.LOGOUT_ON_GET:
            return self.post(*args, **kwargs)
        if not self.request.user.is_authenticated():
            return redirect(self.get_redirect_url())
        ctx = self.get_context_data()
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        url = self.get_redirect_url()
        if self.request.user.is_authenticated():
            self.logout()
        return redirect(url)

    def logout(self):
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'account/messages/logged_out.txt')
        auth_logout(self.request)

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_value = self.request.REQUEST \
            .get(self.redirect_field_name)
        ctx.update({
            "redirect_field_name": self.redirect_field_name,
            "redirect_field_value": redirect_field_value})
        return ctx

    def get_redirect_url(self):
        return (get_next_redirect_url(self.request,
                                      self.redirect_field_name)
                or get_adapter().get_logout_redirect_url(self.request))

logout = LogoutView.as_view()

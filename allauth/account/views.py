from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import (
    Http404,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateResponseMixin, TemplateView, View
from django.views.generic.edit import FormView

from allauth import ratelimit
from allauth.decorators import rate_limit
from allauth.exceptions import ImmediateHttpResponse
from allauth.utils import get_form_class, get_request_param

from . import app_settings, signals
from .adapter import get_adapter
from .forms import (
    AddEmailForm,
    ChangePasswordForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
    SignupForm,
    UserTokenForm,
)
from .models import EmailAddress, EmailConfirmation, EmailConfirmationHMAC
from .utils import (
    complete_signup,
    get_login_redirect_url,
    get_next_redirect_url,
    logout_on_password_change,
    passthrough_next_redirect_url,
    perform_login,
    send_email_confirmation,
    sync_user_email_addresses,
    url_str_to_user_pk,
)


INTERNAL_RESET_SESSION_KEY = "_password_reset_key"


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("oldpassword", "password", "password1", "password2")
)


def _ajax_response(request, response, form=None, data=None):
    adapter = get_adapter(request)
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


class RedirectAuthenticatedUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and app_settings.AUTHENTICATED_LOGIN_REDIRECTS:
            redirect_to = self.get_authenticated_redirect_url()
            response = HttpResponseRedirect(redirect_to)
            return _ajax_response(request, response)
        else:
            response = super(RedirectAuthenticatedUserMixin, self).dispatch(
                request, *args, **kwargs
            )
        return response

    def get_authenticated_redirect_url(self):
        redirect_field_name = self.redirect_field_name
        return get_login_redirect_url(
            self.request,
            url=self.get_success_url(),
            redirect_field_name=redirect_field_name,
        )


class AjaxCapableProcessFormViewMixin(object):
    def get(self, request, *args, **kwargs):
        response = super(AjaxCapableProcessFormViewMixin, self).get(
            request, *args, **kwargs
        )
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
            form = super(AjaxCapableProcessFormViewMixin, self).get_form(form_class)
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


class LogoutFunctionalityMixin(object):
    def logout(self):
        adapter = get_adapter(self.request)
        adapter.add_message(
            self.request, messages.SUCCESS, "account/messages/logged_out.txt"
        )
        adapter.logout(self.request)


class LoginView(
    RedirectAuthenticatedUserMixin, AjaxCapableProcessFormViewMixin, FormView
):
    form_class = LoginForm
    template_name = "account/login." + app_settings.TEMPLATE_EXTENSION
    success_url = None
    redirect_field_name = "next"

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "login", self.form_class)

    def form_valid(self, form):
        success_url = self.get_success_url()
        try:
            return form.login(self.request, redirect_url=success_url)
        except ImmediateHttpResponse as e:
            return e.response

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (
            get_next_redirect_url(self.request, self.redirect_field_name)
            or self.success_url
        )
        return ret

    def get_context_data(self, **kwargs):
        ret = super(LoginView, self).get_context_data(**kwargs)
        signup_url = passthrough_next_redirect_url(
            self.request, reverse("account_signup"), self.redirect_field_name
        )
        redirect_field_value = get_request_param(self.request, self.redirect_field_name)
        site = get_current_site(self.request)

        ret.update(
            {
                "signup_url": signup_url,
                "site": site,
                "redirect_field_name": self.redirect_field_name,
                "redirect_field_value": redirect_field_value,
            }
        )
        return ret


login = LoginView.as_view()


class CloseableSignupMixin(object):
    template_name_signup_closed = (
        "account/signup_closed." + app_settings.TEMPLATE_EXTENSION
    )

    def dispatch(self, request, *args, **kwargs):
        try:
            if not self.is_open():
                return self.closed()
        except ImmediateHttpResponse as e:
            return e.response
        return super(CloseableSignupMixin, self).dispatch(request, *args, **kwargs)

    def is_open(self):
        return get_adapter(self.request).is_open_for_signup(self.request)

    def closed(self):
        response_kwargs = {
            "request": self.request,
            "template": self.template_name_signup_closed,
        }
        return self.response_class(**response_kwargs)


@method_decorator(rate_limit(action="signup"), name="dispatch")
class SignupView(
    RedirectAuthenticatedUserMixin,
    CloseableSignupMixin,
    AjaxCapableProcessFormViewMixin,
    FormView,
):
    template_name = "account/signup." + app_settings.TEMPLATE_EXTENSION
    form_class = SignupForm
    redirect_field_name = "next"
    success_url = None

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "signup", self.form_class)

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (
            get_next_redirect_url(self.request, self.redirect_field_name)
            or self.success_url
        )
        return ret

    def form_valid(self, form):
        self.user = form.save(self.request)
        if not self.user:
            return get_adapter(self.request).respond_email_verification_sent(
                self.request, None
            )
        try:
            return complete_signup(
                self.request,
                self.user,
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url(),
            )
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):
        ret = super(SignupView, self).get_context_data(**kwargs)
        form = ret["form"]
        email = self.request.session.get("account_verified_email")
        if email:
            email_keys = ["email"]
            if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
                email_keys.append("email2")
            for email_key in email_keys:
                form.fields[email_key].initial = email
        login_url = passthrough_next_redirect_url(
            self.request, reverse("account_login"), self.redirect_field_name
        )
        redirect_field_name = self.redirect_field_name
        site = get_current_site(self.request)
        redirect_field_value = get_request_param(self.request, redirect_field_name)
        ret.update(
            {
                "login_url": login_url,
                "redirect_field_name": redirect_field_name,
                "redirect_field_value": redirect_field_value,
                "site": site,
            }
        )
        return ret


signup = SignupView.as_view()


class ConfirmEmailView(TemplateResponseMixin, LogoutFunctionalityMixin, View):

    template_name = "account/email_confirm." + app_settings.TEMPLATE_EXTENSION

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

        # In the event someone clicks on an email confirmation link
        # for one account while logged into another account,
        # logout of the currently logged in account.
        if (
            self.request.user.is_authenticated
            and self.request.user.pk != confirmation.email_address.user_id
        ):
            self.logout()

        get_adapter(self.request).add_message(
            self.request,
            messages.SUCCESS,
            "account/messages/email_confirmed.txt",
            {"email": confirmation.email_address.email},
        )
        if app_settings.LOGIN_ON_EMAIL_CONFIRMATION:
            resp = self.login_on_confirm(confirmation)
            if resp is not None:
                return resp
        # Don't -- allauth doesn't touch is_active so that sys admin can
        # use it to block users et al
        #
        # user = confirmation.email_address.user
        # user.is_active = True
        # user.save()
        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)
        return redirect(redirect_url)

    def login_on_confirm(self, confirmation):
        """
        Simply logging in the user may become a security issue. If you
        do not take proper care (e.g. don't purge used email
        confirmations), a malicious person that got hold of the link
        will be able to login over and over again and the user is
        unable to do anything about it. Even restoring their own mailbox
        security will not help, as the links will still work. For
        password reset this is different, this mechanism works only as
        long as the attacker has access to the mailbox. If they no
        longer has access they cannot issue a password request and
        intercept it. Furthermore, all places where the links are
        listed (log files, but even Google Analytics) all of a sudden
        need to be secured. Purging the email confirmation once
        confirmed changes the behavior -- users will not be able to
        repeatedly confirm (in case they forgot that they already
        clicked the mail).

        All in all, opted for storing the user that is in the process
        of signing up in the session to avoid all of the above.  This
        may not 100% work in case the user closes the browser (and the
        session gets lost), but at least we're secure.
        """
        user_pk = None
        user_pk_str = get_adapter(self.request).unstash_user(self.request)
        if user_pk_str:
            user_pk = url_str_to_user_pk(user_pk_str)
        user = confirmation.email_address.user
        if user_pk == user.pk and self.request.user.is_anonymous:
            return perform_login(
                self.request,
                user,
                app_settings.EmailVerificationMethod.NONE,
                # passed as callable, as this method
                # depends on the authenticated state
                redirect_url=self.get_redirect_url,
            )

        return None

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        emailconfirmation = EmailConfirmationHMAC.from_key(key)
        if not emailconfirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                emailconfirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                raise Http404()
        return emailconfirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx["confirmation"] = self.object
        site = get_current_site(self.request)
        ctx.update({"site": site})
        return ctx

    def get_redirect_url(self):
        return get_adapter(self.request).get_email_confirmation_redirect_url(
            self.request
        )


confirm_email = ConfirmEmailView.as_view()


@method_decorator(rate_limit(action="manage_email"), name="dispatch")
class EmailView(AjaxCapableProcessFormViewMixin, FormView):
    template_name = "account/email." + app_settings.TEMPLATE_EXTENSION
    form_class = AddEmailForm
    success_url = reverse_lazy("account_email")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "add_email", self.form_class)

    def dispatch(self, request, *args, **kwargs):
        sync_user_email_addresses(request.user)
        return super(EmailView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(EmailView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        email_address = form.save(self.request)
        get_adapter(self.request).add_message(
            self.request,
            messages.INFO,
            "account/messages/email_confirmation_sent.txt",
            {"email": form.cleaned_data["email"]},
        )
        signals.email_added.send(
            sender=self.request.user.__class__,
            request=self.request,
            user=self.request.user,
            email_address=email_address,
        )
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
            res = res or HttpResponseRedirect(self.get_success_url())
            # Given that we bypassed AjaxCapableProcessFormViewMixin,
            # we'll have to call invoke it manually...
            res = _ajax_response(request, res, data=self._get_ajax_data_if())
        else:
            # No email address selected
            res = HttpResponseRedirect(self.success_url)
            res = _ajax_response(request, res, data=self._get_ajax_data_if())
        return res

    def _get_email_address(self, request):
        email = request.POST["email"]
        try:
            return EmailAddress.objects.get_for_user(user=request.user, email=email)
        except EmailAddress.DoesNotExist:
            pass

    def _action_send(self, request, *args, **kwargs):
        email_address = self._get_email_address(request)
        if email_address:
            send_email_confirmation(
                self.request, request.user, email=email_address.email
            )

    def _action_remove(self, request, *args, **kwargs):
        email_address = self._get_email_address(request)
        if email_address:
            if email_address.primary:
                get_adapter(request).add_message(
                    request,
                    messages.ERROR,
                    "account/messages/cannot_delete_primary_email.txt",
                    {"email": email_address.email},
                )
            else:
                email_address.delete()
                signals.email_removed.send(
                    sender=request.user.__class__,
                    request=request,
                    user=request.user,
                    email_address=email_address,
                )
                get_adapter(request).add_message(
                    request,
                    messages.SUCCESS,
                    "account/messages/email_deleted.txt",
                    {"email": email_address.email},
                )
                return HttpResponseRedirect(self.get_success_url())

    def _action_primary(self, request, *args, **kwargs):
        email_address = self._get_email_address(request)
        if email_address:
            # Not primary=True -- Slightly different variation, don't
            # require verified unless moving from a verified
            # address. Ignore constraint if previous primary email
            # address is not verified.
            if (
                not email_address.verified
                and EmailAddress.objects.filter(
                    user=request.user, verified=True
                ).exists()
            ):
                get_adapter(request).add_message(
                    request,
                    messages.ERROR,
                    "account/messages/unverified_primary_email.txt",
                )
            else:
                # Sending the old primary address to the signal
                # adds a db query.
                try:
                    from_email_address = EmailAddress.objects.get(
                        user=request.user, primary=True
                    )
                except EmailAddress.DoesNotExist:
                    from_email_address = None
                email_address.set_as_primary()
                get_adapter(request).add_message(
                    request,
                    messages.SUCCESS,
                    "account/messages/primary_email_set.txt",
                )
                signals.email_changed.send(
                    sender=request.user.__class__,
                    request=request,
                    user=request.user,
                    from_email_address=from_email_address,
                    to_email_address=email_address,
                )
                return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ret = super(EmailView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret["add_email_form"] = ret.get("form")
        # (end NOTE)
        ret["can_add_email"] = EmailAddress.objects.can_add_email(self.request.user)
        return ret

    def get_ajax_data(self):
        data = []
        for emailaddress in self.request.user.emailaddress_set.all():
            data.append(
                {
                    "id": emailaddress.pk,
                    "email": emailaddress.email,
                    "verified": emailaddress.verified,
                    "primary": emailaddress.primary,
                }
            )
        return data


email = login_required(EmailView.as_view())


@method_decorator(rate_limit(action="change_password"), name="dispatch")
class PasswordChangeView(AjaxCapableProcessFormViewMixin, FormView):
    template_name = "account/password_change." + app_settings.TEMPLATE_EXTENSION
    form_class = ChangePasswordForm
    success_url = reverse_lazy("account_change_password")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "change_password", self.form_class)

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(PasswordChangeView, self).dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if not self.request.user.has_usable_password():
            return HttpResponseRedirect(reverse("account_set_password"))
        return super(PasswordChangeView, self).render_to_response(
            context, **response_kwargs
        )

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        logout_on_password_change(self.request, form.user)
        get_adapter(self.request).add_message(
            self.request,
            messages.SUCCESS,
            "account/messages/password_changed.txt",
        )
        signals.password_changed.send(
            sender=self.request.user.__class__,
            request=self.request,
            user=self.request.user,
        )
        return super(PasswordChangeView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordChangeView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret["password_change_form"] = ret.get("form")
        # (end NOTE)
        return ret


password_change = login_required(PasswordChangeView.as_view())


@method_decorator(
    # NOTE: 'change_password' (iso 'set_') is intentional, there is no need to
    # differentiate between set and change.
    rate_limit(action="change_password"),
    name="dispatch",
)
class PasswordSetView(AjaxCapableProcessFormViewMixin, FormView):
    template_name = "account/password_set." + app_settings.TEMPLATE_EXTENSION
    form_class = SetPasswordForm
    success_url = reverse_lazy("account_set_password")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "set_password", self.form_class)

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.has_usable_password():
            return HttpResponseRedirect(reverse("account_change_password"))
        return super(PasswordSetView, self).dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return super(PasswordSetView, self).render_to_response(
            context, **response_kwargs
        )

    def get_form_kwargs(self):
        kwargs = super(PasswordSetView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        logout_on_password_change(self.request, form.user)
        get_adapter(self.request).add_message(
            self.request, messages.SUCCESS, "account/messages/password_set.txt"
        )
        signals.password_set.send(
            sender=self.request.user.__class__,
            request=self.request,
            user=self.request.user,
        )
        return super(PasswordSetView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordSetView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret["password_set_form"] = ret.get("form")
        # (end NOTE)
        return ret


password_set = login_required(PasswordSetView.as_view())


@method_decorator(rate_limit(action="reset_password"), name="dispatch")
class PasswordResetView(AjaxCapableProcessFormViewMixin, FormView):
    template_name = "account/password_reset." + app_settings.TEMPLATE_EXTENSION
    form_class = ResetPasswordForm
    success_url = reverse_lazy("account_reset_password_done")
    redirect_field_name = "next"

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "reset_password", self.form_class)

    def form_valid(self, form):
        r429 = ratelimit.consume_or_429(
            self.request,
            action="reset_password_email",
            key=form.cleaned_data["email"].lower(),
        )
        if r429:
            return r429
        form.save(self.request)
        return super(PasswordResetView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordResetView, self).get_context_data(**kwargs)
        login_url = passthrough_next_redirect_url(
            self.request, reverse("account_login"), self.redirect_field_name
        )
        # NOTE: For backwards compatibility
        ret["password_reset_form"] = ret.get("form")
        # (end NOTE)
        ret.update({"login_url": login_url})
        return ret


password_reset = PasswordResetView.as_view()


class PasswordResetDoneView(TemplateView):
    template_name = "account/password_reset_done." + app_settings.TEMPLATE_EXTENSION


password_reset_done = PasswordResetDoneView.as_view()


@method_decorator(rate_limit(action="reset_password_from_key"), name="dispatch")
class PasswordResetFromKeyView(
    AjaxCapableProcessFormViewMixin, LogoutFunctionalityMixin, FormView
):
    template_name = "account/password_reset_from_key." + app_settings.TEMPLATE_EXTENSION
    form_class = ResetPasswordKeyForm
    success_url = reverse_lazy("account_reset_password_from_key_done")
    reset_url_key = "set-password"

    def get_form_class(self):
        return get_form_class(
            app_settings.FORMS, "reset_password_from_key", self.form_class
        )

    def dispatch(self, request, uidb36, key, **kwargs):
        self.request = request
        self.key = key

        if self.key == self.reset_url_key:
            self.key = self.request.session.get(INTERNAL_RESET_SESSION_KEY, "")
            # (Ab)using forms here to be able to handle errors in XHR #890
            token_form = UserTokenForm(data={"uidb36": uidb36, "key": self.key})
            if token_form.is_valid():
                self.reset_user = token_form.reset_user

                # In the event someone clicks on a password reset link
                # for one account while logged into another account,
                # logout of the currently logged in account.
                if (
                    self.request.user.is_authenticated
                    and self.request.user.pk != self.reset_user.pk
                ):
                    self.logout()
                    self.request.session[INTERNAL_RESET_SESSION_KEY] = self.key

                return super(PasswordResetFromKeyView, self).dispatch(
                    request, uidb36, self.key, **kwargs
                )
        else:
            token_form = UserTokenForm(data={"uidb36": uidb36, "key": self.key})
            if token_form.is_valid():
                # Store the key in the session and redirect to the
                # password reset form at a URL without the key. That
                # avoids the possibility of leaking the key in the
                # HTTP Referer header.
                self.request.session[INTERNAL_RESET_SESSION_KEY] = self.key
                redirect_url = self.request.path.replace(self.key, self.reset_url_key)
                return redirect(redirect_url)

        self.reset_user = None
        response = self.render_to_response(self.get_context_data(token_fail=True))
        return _ajax_response(self.request, response, form=token_form)

    def get_context_data(self, **kwargs):
        ret = super(PasswordResetFromKeyView, self).get_context_data(**kwargs)
        ret["action_url"] = reverse(
            "account_reset_password_from_key",
            kwargs={
                "uidb36": self.kwargs["uidb36"],
                "key": self.kwargs["key"],
            },
        )
        return ret

    def get_form_kwargs(self):
        kwargs = super(PasswordResetFromKeyView, self).get_form_kwargs()
        kwargs["user"] = self.reset_user
        kwargs["temp_key"] = self.key
        return kwargs

    def form_valid(self, form):
        form.save()
        adapter = get_adapter(self.request)

        if self.reset_user and app_settings.LOGIN_ATTEMPTS_LIMIT:
            # User successfully reset the password, clear any
            # possible cache entries for all email addresses.
            for email in self.reset_user.emailaddress_set.all():
                adapter._delete_login_attempts_cached_email(
                    self.request, email=email.email
                )

        adapter.add_message(
            self.request,
            messages.SUCCESS,
            "account/messages/password_changed.txt",
        )
        signals.password_reset.send(
            sender=self.reset_user.__class__,
            request=self.request,
            user=self.reset_user,
        )

        if app_settings.LOGIN_ON_PASSWORD_RESET:
            return perform_login(
                self.request,
                self.reset_user,
                email_verification=app_settings.EMAIL_VERIFICATION,
            )

        return super(PasswordResetFromKeyView, self).form_valid(form)


password_reset_from_key = PasswordResetFromKeyView.as_view()


class PasswordResetFromKeyDoneView(TemplateView):
    template_name = (
        "account/password_reset_from_key_done." + app_settings.TEMPLATE_EXTENSION
    )


password_reset_from_key_done = PasswordResetFromKeyDoneView.as_view()


class LogoutView(TemplateResponseMixin, LogoutFunctionalityMixin, View):

    template_name = "account/logout." + app_settings.TEMPLATE_EXTENSION
    redirect_field_name = "next"

    def get(self, *args, **kwargs):
        if app_settings.LOGOUT_ON_GET:
            return self.post(*args, **kwargs)
        if not self.request.user.is_authenticated:
            response = redirect(self.get_redirect_url())
            return _ajax_response(self.request, response)
        ctx = self.get_context_data()
        response = self.render_to_response(ctx)
        return _ajax_response(self.request, response)

    def post(self, *args, **kwargs):
        url = self.get_redirect_url()
        if self.request.user.is_authenticated:
            self.logout()
        response = redirect(url)
        return _ajax_response(self.request, response)

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_value = get_request_param(self.request, self.redirect_field_name)
        ctx.update(
            {
                "redirect_field_name": self.redirect_field_name,
                "redirect_field_value": redirect_field_value,
            }
        )
        return ctx

    def get_redirect_url(self):
        return get_next_redirect_url(
            self.request, self.redirect_field_name
        ) or get_adapter(self.request).get_logout_redirect_url(self.request)


logout = LogoutView.as_view()


class AccountInactiveView(TemplateView):
    template_name = "account/account_inactive." + app_settings.TEMPLATE_EXTENSION


account_inactive = AccountInactiveView.as_view()


class EmailVerificationSentView(TemplateView):
    template_name = "account/verification_sent." + app_settings.TEMPLATE_EXTENSION


email_verification_sent = EmailVerificationSentView.as_view()

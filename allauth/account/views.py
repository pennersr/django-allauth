import django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.validators import validate_email
from django.forms import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from allauth import app_settings as allauth_app_settings
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import (
    AddEmailForm,
    ChangePasswordForm,
    ConfirmEmailVerificationCodeForm,
    ConfirmLoginCodeForm,
    LoginForm,
    ReauthenticateForm,
    RequestLoginCodeForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
    SignupForm,
    UserTokenForm,
)
from allauth.account.internal import flows
from allauth.account.mixins import (
    AjaxCapableProcessFormViewMixin,
    CloseableSignupMixin,
    LogoutFunctionalityMixin,
    NextRedirectMixin,
    RedirectAuthenticatedUserMixin,
    _ajax_response,
)
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    get_emailconfirmation_model,
)
from allauth.account.stages import EmailVerificationStage, LoginStageController
from allauth.account.utils import (
    complete_signup,
    perform_login,
    send_email_confirmation,
    sync_user_email_addresses,
    url_str_to_user_pk,
    user_display,
)
from allauth.core import ratelimit
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.core.internal.httpkit import redirect
from allauth.decorators import rate_limit
from allauth.utils import get_form_class


INTERNAL_RESET_SESSION_KEY = "_password_reset_key"


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("oldpassword", "password", "password1", "password2")
)

if django.VERSION >= (5, 1):
    # Currently missing from django-stubs
    from django.contrib.auth.decorators import \
        login_not_required  # type: ignore [attr-defined]

    login_not_required_cls = method_decorator(login_not_required, name="dispatch")

else:

    # Dummy decorator for older Django versions
    def login_not_required_cls(obj):
        return obj


@method_decorator(rate_limit(action="login"), name="dispatch")
@login_not_required_cls
class LoginView(
    NextRedirectMixin,
    RedirectAuthenticatedUserMixin,
    AjaxCapableProcessFormViewMixin,
    FormView,
):
    form_class = LoginForm
    template_name = "account/login." + app_settings.TEMPLATE_EXTENSION
    success_url = None

    @sensitive_post_parameters_m
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if allauth_app_settings.SOCIALACCOUNT_ONLY and request.method != "GET":
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "login", self.form_class)

    def form_valid(self, form):
        redirect_url = self.get_success_url()
        try:
            return form.login(self.request, redirect_url=redirect_url)
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):
        passkey_login_enabled = False
        if allauth_app_settings.MFA_ENABLED:
            from allauth.mfa import app_settings as mfa_settings

            passkey_login_enabled = mfa_settings.PASSKEY_LOGIN_ENABLED
        ret = super().get_context_data(**kwargs)
        signup_url = None
        if not allauth_app_settings.SOCIALACCOUNT_ONLY:
            signup_url = self.passthrough_next_url(reverse("account_signup"))
        site = get_current_site(self.request)

        ret.update(
            {
                "signup_url": signup_url,
                "site": site,
                "SOCIALACCOUNT_ENABLED": allauth_app_settings.SOCIALACCOUNT_ENABLED,
                "SOCIALACCOUNT_ONLY": allauth_app_settings.SOCIALACCOUNT_ONLY,
                "LOGIN_BY_CODE_ENABLED": app_settings.LOGIN_BY_CODE_ENABLED,
                "PASSKEY_LOGIN_ENABLED": passkey_login_enabled,
            }
        )
        if app_settings.LOGIN_BY_CODE_ENABLED:
            request_login_code_url = self.passthrough_next_url(
                reverse("account_request_login_code")
            )
            ret["request_login_code_url"] = request_login_code_url
        return ret


login = LoginView.as_view()


@method_decorator(rate_limit(action="signup"), name="dispatch")
@login_not_required_cls
class SignupView(
    RedirectAuthenticatedUserMixin,
    CloseableSignupMixin,
    NextRedirectMixin,
    AjaxCapableProcessFormViewMixin,
    FormView,
):
    template_name = "account/signup." + app_settings.TEMPLATE_EXTENSION
    form_class = SignupForm

    @sensitive_post_parameters_m
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "signup", self.form_class)

    def form_valid(self, form):
        self.user, resp = form.try_save(self.request)
        if resp:
            return resp
        try:
            redirect_url = self.get_success_url()
            return complete_signup(
                self.request,
                self.user,
                email_verification=None,
                success_url=redirect_url,
            )
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        form = ret["form"]
        email = self.request.session.get("account_verified_email")
        if email:
            email_keys = ["email"]
            if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
                email_keys.append("email2")
            for email_key in email_keys:
                form.fields[email_key].initial = email
        login_url = self.passthrough_next_url(reverse("account_login"))
        site = get_current_site(self.request)
        ret.update(
            {
                "login_url": login_url,
                "site": site,
                "SOCIALACCOUNT_ENABLED": allauth_app_settings.SOCIALACCOUNT_ENABLED,
                "SOCIALACCOUNT_ONLY": allauth_app_settings.SOCIALACCOUNT_ONLY,
            }
        )
        return ret

    def get_initial(self):
        initial = super().get_initial()
        email = self.request.GET.get("email")
        if email:
            try:
                validate_email(email)
            except ValidationError:
                return initial
            initial["email"] = email
            if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
                initial["email2"] = email
        return initial


signup = SignupView.as_view()


@login_not_required_cls
class ConfirmEmailView(NextRedirectMixin, LogoutFunctionalityMixin, TemplateView):
    template_name = "account/email_confirm." + app_settings.TEMPLATE_EXTENSION

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.logout_other_user(self.object)
            if app_settings.CONFIRM_EMAIL_ON_GET:
                return self.post(*args, **kwargs)
        except Http404:
            self.object = None
        ctx = self.get_context_data()
        if not self.object and get_adapter().is_ajax(self.request):
            resp = HttpResponse()
            resp.status_code = 400
        else:
            resp = self.render_to_response(ctx)
        return _ajax_response(self.request, resp, data=self.get_ajax_data())

    def logout_other_user(self, confirmation):
        """
        In the event someone clicks on an email confirmation link
        for one account while logged into another account,
        logout of the currently logged in account.
        """
        if (
            self.request.user.is_authenticated
            and self.request.user.pk != confirmation.email_address.user_id
        ):
            self.logout()

    def post(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        email_address = confirmation.confirm(self.request)
        if not email_address:
            return self.respond(False)

        self.logout_other_user(self.object)

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
        return self.respond(True)

    def respond(self, success):
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
                email_verification=app_settings.EmailVerificationMethod.NONE,
                # passed as callable, as this method
                # depends on the authenticated state
                redirect_url=self.get_redirect_url,
            )

        return None

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        model = get_emailconfirmation_model()
        emailconfirmation = model.from_key(key)
        if not emailconfirmation:
            raise Http404()
        return emailconfirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs

    def get_ajax_data(self):
        ret = {
            "can_confirm": bool(self.object),
        }
        if self.object:
            ret["email"] = self.object.email_address.email
            ret["user"] = {"display": user_display(self.object.email_address.user)}
        return ret

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        site = get_current_site(self.request)
        ctx.update(
            {
                "site": site,
                "confirmation": self.object,
                "can_confirm": self.object
                and self.object.email_address.can_set_verified(),
            }
        )
        if self.object:
            ctx["email"] = self.object.email_address.email
        return ctx

    def get_redirect_url(self):
        url = self.get_next_url()
        if not url:
            url = get_adapter(self.request).get_email_verification_redirect_url(
                self.object.email_address,
            )
        return url


confirm_email = ConfirmEmailView.as_view()


@method_decorator(login_required, name="dispatch")
@method_decorator(rate_limit(action="manage_email"), name="dispatch")
class EmailView(AjaxCapableProcessFormViewMixin, FormView):
    template_name = (
        "account/email_change." if app_settings.CHANGE_EMAIL else "account/email."
    ) + app_settings.TEMPLATE_EXTENSION
    form_class = AddEmailForm
    success_url = reverse_lazy("account_email")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "add_email", self.form_class)

    def dispatch(self, request, *args, **kwargs):
        self._did_send_verification_email = False
        sync_user_email_addresses(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(EmailView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        flows.manage_email.add_email(self.request, form)
        self._did_send_verification_email = True
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        res = None
        if "action_add" in request.POST:
            res = super().post(request, *args, **kwargs)
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
            validate_email(email)
        except ValidationError:
            return None
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
            self._did_send_verification_email = True
        if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            return HttpResponseRedirect(reverse("account_email_verification_sent"))

    def _action_remove(self, request, *args, **kwargs):
        email_address = self._get_email_address(request)
        if email_address:
            if flows.manage_email.delete_email(request, email_address):
                return HttpResponseRedirect(self.get_success_url())

    def _action_primary(self, request, *args, **kwargs):
        email_address = self._get_email_address(request)
        if email_address:
            if flows.manage_email.mark_as_primary(request, email_address):
                return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ret = super(EmailView, self).get_context_data(**kwargs)
        emails = list(
            EmailAddress.objects.filter(user=self.request.user).order_by("email")
        )
        ret.update(
            {
                "emailaddresses": emails,
                "emailaddress_radios": [
                    {
                        "id": f"email_radio_{i}",
                        "checked": email.primary or len(emails) == 1,
                        "emailaddress": email,
                    }
                    for i, email in enumerate(emails)
                ],
                "add_email_form": ret.get("form"),
                "can_add_email": EmailAddress.objects.can_add_email(self.request.user),
            }
        )
        if app_settings.CHANGE_EMAIL:
            ret.update(
                {
                    "new_emailaddress": EmailAddress.objects.get_new(self.request.user),
                    "current_emailaddress": EmailAddress.objects.get_verified(
                        self.request.user
                    ),
                }
            )
        return ret

    def get_ajax_data(self):
        data = []
        for emailaddress in self.request.user.emailaddress_set.all().order_by("pk"):
            data.append(
                {
                    "id": emailaddress.pk,
                    "email": emailaddress.email,
                    "verified": emailaddress.verified,
                    "primary": emailaddress.primary,
                }
            )
        return data

    def get_success_url(self):
        if (
            self._did_send_verification_email
            and app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED
        ):
            return reverse("account_email_verification_sent")
        return self.success_url


email = EmailView.as_view()


@method_decorator(login_required, name="dispatch")
@method_decorator(rate_limit(action="change_password"), name="dispatch")
class PasswordChangeView(AjaxCapableProcessFormViewMixin, NextRedirectMixin, FormView):
    template_name = "account/password_change." + app_settings.TEMPLATE_EXTENSION
    form_class = ChangePasswordForm

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "change_password", self.form_class)

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_usable_password():
            return HttpResponseRedirect(reverse("account_set_password"))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_default_success_url(self):
        return get_adapter().get_password_change_redirect_url(self.request)

    def form_valid(self, form):
        form.save()
        flows.password_change.finalize_password_change(self.request, form.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret["password_change_form"] = ret.get("form")
        # (end NOTE)
        return ret


password_change = PasswordChangeView.as_view()


@method_decorator(login_required, name="dispatch")
@method_decorator(
    # NOTE: 'change_password' (iso 'set_') is intentional, there is no need to
    # differentiate between set and change.
    rate_limit(action="change_password"),
    name="dispatch",
)
class PasswordSetView(AjaxCapableProcessFormViewMixin, NextRedirectMixin, FormView):
    template_name = "account/password_set." + app_settings.TEMPLATE_EXTENSION
    form_class = SetPasswordForm

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "set_password", self.form_class)

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.has_usable_password():
            return HttpResponseRedirect(reverse("account_change_password"))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_default_success_url(self):
        return get_adapter().get_password_change_redirect_url(self.request)

    def form_valid(self, form):
        form.save()
        flows.password_change.finalize_password_set(self.request, form.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret["password_set_form"] = ret.get("form")
        # (end NOTE)
        return ret


password_set = PasswordSetView.as_view()


@login_not_required_cls
class PasswordResetView(NextRedirectMixin, AjaxCapableProcessFormViewMixin, FormView):
    template_name = "account/password_reset." + app_settings.TEMPLATE_EXTENSION
    form_class = ResetPasswordForm
    success_url = reverse_lazy("account_reset_password_done")

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "reset_password", self.form_class)

    def form_valid(self, form):
        r429 = ratelimit.consume_or_429(
            self.request,
            action="reset_password",
            key=form.cleaned_data["email"].lower(),
        )
        if r429:
            return r429
        form.save(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        login_url = self.passthrough_next_url(reverse("account_login"))
        # NOTE: For backwards compatibility
        ret["password_reset_form"] = ret.get("form")
        # (end NOTE)
        ret.update({"login_url": login_url})
        return ret


password_reset = PasswordResetView.as_view()


@login_not_required_cls
class PasswordResetDoneView(TemplateView):
    template_name = "account/password_reset_done." + app_settings.TEMPLATE_EXTENSION


password_reset_done = PasswordResetDoneView.as_view()


@method_decorator(rate_limit(action="reset_password_from_key"), name="dispatch")
@login_not_required_cls
class PasswordResetFromKeyView(
    AjaxCapableProcessFormViewMixin,
    NextRedirectMixin,
    LogoutFunctionalityMixin,
    FormView,
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

        user_token_form_class = get_form_class(
            app_settings.FORMS, "user_token", UserTokenForm
        )
        is_ajax = get_adapter().is_ajax(request)
        if self.key == self.reset_url_key or is_ajax:
            if not is_ajax:
                self.key = self.request.session.get(INTERNAL_RESET_SESSION_KEY, "")
            # (Ab)using forms here to be able to handle errors in XHR #890
            token_form = user_token_form_class(data={"uidb36": uidb36, "key": self.key})
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

                return super().dispatch(request, uidb36, self.key, **kwargs)
        else:
            token_form = user_token_form_class(data={"uidb36": uidb36, "key": self.key})
            if token_form.is_valid():
                # Store the key in the session and redirect to the
                # password reset form at a URL without the key. That
                # avoids the possibility of leaking the key in the
                # HTTP Referer header.
                self.request.session[INTERNAL_RESET_SESSION_KEY] = self.key
                redirect_url = self.passthrough_next_url(
                    self.request.path.replace(self.key, self.reset_url_key)
                )
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
        flows.password_reset.finalize_password_reset(self.request, self.reset_user)
        if app_settings.LOGIN_ON_PASSWORD_RESET:
            return perform_login(
                self.request,
                self.reset_user,
            )
        return super(PasswordResetFromKeyView, self).form_valid(form)


password_reset_from_key = PasswordResetFromKeyView.as_view()


@login_not_required_cls
class PasswordResetFromKeyDoneView(TemplateView):
    template_name = (
        "account/password_reset_from_key_done." + app_settings.TEMPLATE_EXTENSION
    )


password_reset_from_key_done = PasswordResetFromKeyDoneView.as_view()


@login_not_required_cls
class LogoutView(NextRedirectMixin, LogoutFunctionalityMixin, TemplateView):
    template_name = "account/logout." + app_settings.TEMPLATE_EXTENSION

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

    def get_redirect_url(self):
        return self.get_next_url() or get_adapter(self.request).get_logout_redirect_url(
            self.request
        )


logout = LogoutView.as_view()


@login_not_required_cls
class AccountInactiveView(TemplateView):
    template_name = "account/account_inactive." + app_settings.TEMPLATE_EXTENSION


account_inactive = AccountInactiveView.as_view()


@login_not_required_cls
class EmailVerificationSentView(TemplateView):
    template_name = "account/verification_sent." + app_settings.TEMPLATE_EXTENSION


@login_not_required_cls
class ConfirmEmailVerificationCodeView(FormView):
    template_name = (
        "account/confirm_email_verification_code." + app_settings.TEMPLATE_EXTENSION
    )
    form_class = ConfirmEmailVerificationCodeForm

    def dispatch(self, request, *args, **kwargs):
        self.stage = LoginStageController.enter(request, EmailVerificationStage.key)
        self.verification, self.pending_verification = (
            flows.email_verification_by_code.get_pending_verification(
                request, peek=True
            )
        )
        # preventing enumeration?
        verification_is_fake = (
            self.pending_verification and "code" not in self.pending_verification
        )
        # Can we at all continue?
        if (
            # No verification pending?
            (
                not self.pending_verification
            )  # Anonymous, yet no stage (or fake verifcation)?
            or (
                request.user.is_anonymous
                and not self.stage
                and not verification_is_fake
            )
        ):
            return HttpResponseRedirect(
                reverse(
                    "account_login" if request.user.is_anonymous else "account_email"
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_form_class(
            app_settings.FORMS, "confirm_email_verification_code", self.form_class
        )

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["code"] = self.verification.key if self.verification else ""
        return ret

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret["email"] = self.pending_verification["email"]
        ret["cancel_url"] = (
            reverse("account_login") if self.stage else reverse("account_email")
        )
        return ret

    def form_valid(self, form):
        email_address = self.verification.confirm(self.request)
        if self.stage:
            if not email_address:
                return self.stage.abort()
            return self.stage.exit()
        return HttpResponseRedirect(reverse("account_email"))

    def form_invalid(self, form):
        attempts_left = flows.email_verification_by_code.record_invalid_attempt(
            self.request, self.pending_verification
        )
        if attempts_left:
            return super().form_invalid(form)
        adapter = get_adapter(self.request)
        adapter.add_message(
            self.request,
            messages.ERROR,
            message=adapter.error_messages["too_many_login_attempts"],
        )
        return HttpResponseRedirect(reverse("account_login"))


@login_not_required_cls
def email_verification_sent(request):
    if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        return ConfirmEmailVerificationCodeView.as_view()(request)
    else:
        return EmailVerificationSentView.as_view()(request)


@login_not_required_cls
class BaseReauthenticateView(NextRedirectMixin, FormView):
    def dispatch(self, request, *args, **kwargs):
        resp = self._check_reauthentication_method_available(request)
        if resp:
            return resp
        resp = self._check_ratelimit(request)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)

    def _check_ratelimit(self, request):
        return ratelimit.consume_or_429(
            self.request,
            action="reauthenticate",
            user=self.request.user,
        )

    def _check_reauthentication_method_available(self, request):
        methods = get_adapter().get_reauthentication_methods(self.request.user)
        if any([m["url"] == request.path for m in methods]):
            # Method is available
            return None
        if not methods:
            # Reauthentication not available
            raise PermissionDenied("Reauthentication not available")
        url = self.passthrough_next_url(methods[0]["url"])
        return HttpResponseRedirect(url)

    def get_default_success_url(self):
        url = get_adapter(self.request).get_login_redirect_url(self.request)
        return url

    def form_valid(self, form):
        response = flows.reauthentication.resume_request(self.request)
        if response:
            return response
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret.update(
            {
                "reauthentication_alternatives": self.get_reauthentication_alternatives(),
            }
        )
        return ret

    def get_reauthentication_alternatives(self):
        methods = get_adapter().get_reauthentication_methods(self.request.user)
        alts = []
        for method in methods:
            alt = dict(method)
            if self.request.path == alt["url"]:
                continue
            alt["url"] = self.passthrough_next_url(alt["url"])
            alts.append(alt)
        alts = sorted(alts, key=lambda alt: alt["description"])
        return alts


@method_decorator(login_required, name="dispatch")
class ReauthenticateView(BaseReauthenticateView):
    form_class = ReauthenticateForm
    template_name = "account/reauthenticate." + app_settings.TEMPLATE_EXTENSION

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "reauthenticate", self.form_class)

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret["user"] = self.request.user
        return ret

    def form_valid(self, form):
        flows.reauthentication.reauthenticate_by_password(self.request)
        return super().form_valid(form)


reauthenticate = ReauthenticateView.as_view()


@login_not_required_cls
class RequestLoginCodeView(RedirectAuthenticatedUserMixin, NextRedirectMixin, FormView):
    form_class = RequestLoginCodeForm
    template_name = "account/request_login_code." + app_settings.TEMPLATE_EXTENSION

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "request_login_code", self.form_class)

    def form_valid(self, form):
        flows.login_by_code.request_login_code(self.request, form.cleaned_data["email"])
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return None
        url = reverse_lazy("account_confirm_login_code")
        url = self.passthrough_next_url(reverse("account_confirm_login_code"))
        return url

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        site = get_current_site(self.request)
        ret.update({"site": site})
        return ret


request_login_code = RequestLoginCodeView.as_view()


@login_not_required_cls
class ConfirmLoginCodeView(RedirectAuthenticatedUserMixin, NextRedirectMixin, FormView):
    form_class = ConfirmLoginCodeForm
    template_name = "account/confirm_login_code." + app_settings.TEMPLATE_EXTENSION

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.user, self.pending_login = flows.login_by_code.get_pending_login(
            request, peek=True
        )
        if not self.pending_login:
            return HttpResponseRedirect(reverse("account_request_login_code"))
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "confirm_login_code", self.form_class)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["code"] = self.pending_login.get("code", "")
        return kwargs

    def form_valid(self, form):
        redirect_url = self.get_next_url()
        return flows.login_by_code.perform_login_by_code(
            self.request, self.user, redirect_url, self.pending_login
        )

    def form_invalid(self, form):
        attempts_left = flows.login_by_code.record_invalid_attempt(
            self.request, self.pending_login
        )
        if attempts_left:
            return super().form_invalid(form)
        adapter = get_adapter(self.request)
        adapter.add_message(
            self.request,
            messages.ERROR,
            message=adapter.error_messages["too_many_login_attempts"],
        )
        return HttpResponseRedirect(reverse("account_request_login_code"))

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        site = get_current_site(self.request)
        ret.update(
            {
                "site": site,
                "email": self.pending_login["email"],
            }
        )
        return ret


confirm_login_code = ConfirmLoginCodeView.as_view()

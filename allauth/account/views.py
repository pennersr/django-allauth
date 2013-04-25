from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View
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
        return get_login_redirect_url(self.request, 
                                      url=self.get_success_url(),
                                      redirect_field_name=self.redirect_field_name)
        
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
        ret.update({
                "signup_url": passthrough_next_redirect_url(self.request,
                                                            reverse("account_signup"),
                                                            self.redirect_field_name),
                "site": Site.objects.get_current(),
                "redirect_field_name": self.redirect_field_name,
                "redirect_field_value": self.request.REQUEST.get(self.redirect_field_name),
                })
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


class SignupView(RedirectAuthenticatedUserMixin, CloseableSignupMixin, FormView):
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
        ret = super(SignupView, self).get_context_data(**kwargs)
        login_url = passthrough_next_redirect_url(self.request,
                                                  reverse("account_login"),
                                                  self.redirect_field_name)
        redirect_field_name = self.redirect_field_name
        redirect_field_value = self.request.REQUEST.get(redirect_field_name)
        ret.update({"login_url": login_url,
                    "redirect_field_name": redirect_field_name,
                    "redirect_field_value": redirect_field_value })
        return ret


signup = SignupView.as_view()

class ConfirmEmailView(TemplateResponseMixin, View):
    
    messages = {
        "email_confirmed": {
            "level": messages.SUCCESS,
            "text": _("You have confirmed %(email)s.")
        }
    }
    
    def get_template_names(self):
        if self.request.method == 'POST':
            return ["account/email_confirmed.html"]
        else:
            return [ "account/email_confirm.html" ]
    
    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
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
        if self.messages.get("email_confirmed"):
            messages.add_message(
                self.request,
                self.messages["email_confirmed"]["level"],
                self.messages["email_confirmed"]["text"] % {
                    "email": confirmation.email_address.email
                }
            )
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

@login_required
def email(request, **kwargs):
    form_class = kwargs.pop("form_class", AddEmailForm)
    template_name = kwargs.pop("template_name", "account/email.html")
    sync_user_email_addresses(request.user)
    if request.method == "POST" and request.user.is_authenticated():
        if "action_add" in request.POST:
            add_email_form = form_class(request.user, request.POST)
            if add_email_form.is_valid():
                email_address = add_email_form.save(request)
                messages.add_message(request, messages.INFO,
                    ugettext(u"Confirmation e-mail sent to %(email)s") % {
                            "email": add_email_form.cleaned_data["email"]
                        }
                    )
                signals.email_added.send(sender=request.user.__class__,
                        request=request, user=request.user,
                        email_address=email_address)
                return HttpResponseRedirect(reverse('account_email'))
        else:
            add_email_form = form_class()
            if request.POST.get("email"):
                if "action_send" in request.POST:
                    email = request.POST["email"]
                    try:
                        email_address = EmailAddress.objects.get(
                            user=request.user,
                            email=email,
                        )
                        messages.add_message(request, messages.INFO,
                            ugettext("Confirmation e-mail sent to %(email)s") % {
                                "email": email,
                            }
                        )
                        email_address.send_confirmation(request)
                        return HttpResponseRedirect(reverse('account_email'))
                    except EmailAddress.DoesNotExist:
                        pass
                elif "action_remove" in request.POST:
                    email = request.POST["email"]
                    try:
                        email_address = EmailAddress.objects.get(
                            user=request.user,
                            email=email
                        )
                        if email_address.primary:
                            messages.add_message \
                                (request, messages.ERROR,
                                 ugettext("You cannot remove your primary"
                                          " e-mail address (%(email)s)")
                                 % { "email": email })
                        else:
                            email_address.delete()
                            signals.email_removed.send(sender=request.user.__class__,
                                                       request=request, 
                                                       user=request.user,
                                                       email_address=email_address)
                            messages.add_message(request, messages.SUCCESS,
                                ugettext("Removed e-mail address %(email)s") % {
                                    "email": email,
                                }
                            )
                            return HttpResponseRedirect(reverse('account_email'))
                    except EmailAddress.DoesNotExist:
                        pass
                elif "action_primary" in request.POST:
                    email = request.POST["email"]
                    try:
                        email_address = EmailAddress.objects.get(
                            user=request.user,
                            email=email,
                        )
                        if not email_address.verified and \
                                EmailAddress.objects.filter(
                                        user=request.user,
                                        verified=True#,
                                        #primary=True
                                        # Slightly different variation, don't
                                        # require verified unless moving from a
                                        # verified address. Ignore constraint
                                        # if previous primary email address is
                                        # not verified.
                                    ).exists():
                            messages.add_message(request, messages.ERROR,
                                    ugettext("Your primary e-mail address must "
                                        "be verified"))
                        else:
                            # Sending the old primary address to the signal
                            # adds a db query.
                            try:
                                from_email_address = EmailAddress.objects.get(
                                        user=request.user, primary=True )
                            except EmailAddress.DoesNotExist:
                                from_email_address = None
                            email_address.set_as_primary()
                            messages.add_message(request, messages.SUCCESS,
                                         ugettext("Primary e-mail address set"))
                            signals.email_changed.send(
                                    sender=request.user.__class__,
                                    request=request, user=request.user,
                                    from_email_address=from_email_address,
                                    to_email_address=email_address)
                            return HttpResponseRedirect(reverse('account_email'))
                    except EmailAddress.DoesNotExist:
                        pass
    else:
        add_email_form = form_class()
    ctx = { "add_email_form": add_email_form }
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def password_change(request, **kwargs):

    form_class = kwargs.pop("form_class", ChangePasswordForm)
    template_name = kwargs.pop("template_name", "account/password_change.html")

    if not request.user.has_usable_password():
        return HttpResponseRedirect(reverse(password_set))

    if request.method == "POST":
        password_change_form = form_class(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Password successfully changed.")
            )
            signals.password_changed.send(sender=request.user.__class__,
                    request=request, user=request.user)
            password_change_form = form_class(request.user)
    else:
        password_change_form = form_class(request.user)
    ctx = { "password_change_form": password_change_form }
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def password_set(request, **kwargs):

    form_class = kwargs.pop("form_class", SetPasswordForm)
    template_name = kwargs.pop("template_name", "account/password_set.html")

    if request.user.has_usable_password():
        return HttpResponseRedirect(reverse(password_change))

    if request.method == "POST":
        password_set_form = form_class(request.user, request.POST)
        if password_set_form.is_valid():
            password_set_form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Password successfully set.")
            )
            signals.password_set.send(sender=request.user.__class__,
                    request=request, user=request.user)
            return HttpResponseRedirect(reverse(password_change))
    else:
        password_set_form = form_class(request.user)
    ctx = { "password_set_form": password_set_form }
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset(request, **kwargs):

    form_class = kwargs.pop("form_class", ResetPasswordForm)
    template_name = kwargs.pop("template_name", "account/password_reset.html")

    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            password_reset_form.save()
            return HttpResponseRedirect(reverse(password_reset_done))
    else:
        password_reset_form = form_class()

    return render_to_response(template_name, RequestContext(request, { "password_reset_form": password_reset_form, }))


def password_reset_done(request, **kwargs):

    return render_to_response(kwargs.pop("template_name", "account/password_reset_done.html"), RequestContext(request, {}))


def password_reset_from_key(request, uidb36, key, **kwargs):

    form_class = kwargs.get("form_class", ResetPasswordKeyForm)
    template_name = kwargs.get("template_name", "account/password_reset_from_key.html")
    token_generator = kwargs.get("token_generator", default_token_generator)

    # pull out user
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)

    if token_generator.check_token(user, key):
        if request.method == "POST":
            password_reset_key_form = form_class(request.POST, user=user, temp_key=key)
            if password_reset_key_form.is_valid():
                password_reset_key_form.save()
                messages.add_message(request, messages.SUCCESS,
                    ugettext(u"Password successfully changed.")
                )
                signals.password_reset.send(sender=request.user.__class__,
                        request=request, user=request.user)
                password_reset_key_form = None
        else:
            password_reset_key_form = form_class()
        ctx = { "form": password_reset_key_form, }
    else:
        ctx = { "token_fail": True, }

    return render_to_response(template_name, RequestContext(request, ctx))


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
        messages.add_message(self.request, messages.SUCCESS,
                             ugettext("You have signed out."))
        auth_logout(self.request)

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "redirect_field_name": self.redirect_field_name,
            "redirect_field_value": self.request.REQUEST.get(self.redirect_field_name),
        })
        return ctx
    
    def get_redirect_url(self):
        return (get_next_redirect_url(self.request, 
                                      self.redirect_field_name)
                or get_adapter().get_logout_redirect_url(self.request))


logout = LogoutView.as_view()

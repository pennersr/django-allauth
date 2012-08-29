from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect

from allauth.utils import passthrough_login_redirect_url

from utils import get_default_redirect, complete_signup
from forms import AddEmailForm, ChangePasswordForm
from forms import LoginForm, ResetPasswordKeyForm
from forms import ResetPasswordForm, SetPasswordForm, SignupForm
from utils import sync_user_email_addresses
from models import EmailAddress, EmailConfirmation

import app_settings

def login(request, **kwargs):
    form_class = kwargs.pop("form_class", LoginForm)
    template_name = kwargs.pop("template_name", "account/login.html")
    success_url = kwargs.pop("success_url", None)
    url_required = kwargs.pop("url_required", False)
    extra_context = kwargs.pop("extra_context", {})
    redirect_field_name = kwargs.pop("redirect_field_name", "next")

    if extra_context is None:
        extra_context = {}
    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)

    if request.method == "POST" and not url_required:
        form = form_class(request.POST)
        if form.is_valid():
            return form.login(request, redirect_url=success_url)
    else:
        form = form_class()

    ctx = {
        "form": form,
        "signup_url": passthrough_login_redirect_url(request,
                                                     reverse("account_signup")),
        "site": Site.objects.get_current(),
        "url_required": url_required,
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
    }
    ctx.update(extra_context)
    return render_to_response(template_name, RequestContext(request, ctx))


def signup(request, **kwargs):

    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", "account/signup.html")
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    success_url = kwargs.pop("success_url", None)

    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            return complete_signup(request, user, success_url)
    else:
        form = form_class()
    ctx = {"form": form,
           "login_url": passthrough_login_redirect_url(request,
                                                       reverse("account_login")),
           "redirect_field_name": redirect_field_name,
           "redirect_field_value": request.REQUEST.get(redirect_field_name) }
    return render_to_response(template_name, RequestContext(request, ctx))


class ConfirmEmailView(TemplateResponseMixin, View):
    
    messages = {
        "email_confirmed": {
            "level": messages.SUCCESS,
            "text": _("You have confirmed %(email)s.")
        }
    }
    
    def get_template_names(self):
        return {
            "GET": ["account/email_confirm.html"],
            "POST": ["account/email_confirmed.html"],
        }[self.request.method]
    
    def get(self, *args, **kwargs):
        self.object = self.get_object()
        ctx = self.get_context_data()
        return self.render_to_response(ctx)
    
    def post(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm()
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
        qs = EmailConfirmation.objects.all()
        qs = qs.select_related("email_address__user")
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx["confirmation"] = self.object
        return ctx
    
    def get_redirect_url(self):
        if self.request.user.is_authenticated():
            return app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL
        else:
            return app_settings.EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL


confirm_email = ConfirmEmailView.as_view()

@login_required
def email(request, **kwargs):
    form_class = kwargs.pop("form_class", AddEmailForm)
    template_name = kwargs.pop("template_name", "account/email.html")
    sync_user_email_addresses(request.user)
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST.has_key("action_add"):
            add_email_form = form_class(request.user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                messages.add_message(request, messages.INFO,
                    ugettext(u"Confirmation e-mail sent to %(email)s") % {
                            "email": add_email_form.cleaned_data["email"]
                        }
                    )
                return HttpResponseRedirect(reverse('account_email'))
        else:
            add_email_form = form_class()
            if request.POST.get("email"):
                if request.POST.has_key("action_send"):
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
                        email_address.send_confirmation()
                        return HttpResponseRedirect(reverse('account_email'))
                    except EmailAddress.DoesNotExist:
                        pass
                elif request.POST.has_key("action_remove"):
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
                            messages.add_message(request, messages.SUCCESS,
                                ugettext("Removed e-mail address %(email)s") % {
                                    "email": email,
                                }
                            )
                            return HttpResponseRedirect(reverse('account_email'))
                    except EmailAddress.DoesNotExist:
                        pass
                elif request.POST.has_key("action_primary"):
                    email = request.POST["email"]
                    try:
                        email_address = EmailAddress.objects.get(
                            user=request.user,
                            email=email,
                        )
                        email_address.set_as_primary()
                        messages.add_message(request, messages.SUCCESS,
                                             ugettext("Primary e-mail address set"))
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
                password_reset_key_form = None
        else:
            password_reset_key_form = form_class()
        ctx = { "form": password_reset_key_form, }
    else:
        ctx = { "token_fail": True, }

    return render_to_response(template_name, RequestContext(request, ctx))


def logout(request, **kwargs):
    messages.add_message(request, messages.SUCCESS,
        ugettext("You have signed out.")
    )
    kwargs['template_name'] = kwargs.pop('template_name', 'account/logout.html')
    from django.contrib.auth.views import logout as _logout
    return _logout(request, **kwargs)

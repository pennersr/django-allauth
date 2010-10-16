from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from emailconfirmation.models import EmailAddress, EmailConfirmation

# association_model = models.get_model("django_openid", "Association")
# if association_model is not None:
#     from django_openid.models import UserOpenidAssociation

from utils import get_default_redirect, user_display, complete_signup
from forms import AddEmailForm, ChangePasswordForm
from forms import LoginForm, ResetPasswordKeyForm
from forms import ResetPasswordForm, SetPasswordForm, SignupForm

import app_settings

def group_and_bridge(kwargs):
    """
    Given kwargs from the view (with view specific keys popped) pull out the
    bridge and fetch group from database.
    """
    
    bridge = kwargs.pop("bridge", None)
    
    if bridge:
        try:
            group = bridge.get_group(**kwargs)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    return {
        "group": group,
    }


def login(request, **kwargs):
    
    form_class = kwargs.pop("form_class", LoginForm)
    template_name = kwargs.pop("template_name", "account/login.html")
    success_url = kwargs.pop("success_url", None)
#    associate_openid = kwargs.pop("associate_openid", False)
#    openid_success_url = kwargs.pop("openid_success_url", None)
    url_required = kwargs.pop("url_required", False)
    extra_context = kwargs.pop("extra_context", {})
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    
    group, bridge = group_and_bridge(kwargs)
    
    if extra_context is None:
        extra_context = {}
    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)
    
    if request.method == "POST" and not url_required:
        form = form_class(request.POST, group=group)
        if form.is_valid():
            form.login(request)
#            if associate_openid and association_model is not None:
#                for openid in request.session.get("openids", []):
#                    assoc, created = UserOpenidAssociation.objects.get_or_create(
#                        user=form.user, openid=openid.openid
#                    )
#                success_url = openid_success_url or success_url
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Successfully signed in as %(user)s.") % {
                    "user": user_display(form.user)
                }
            )
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(group=group)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "form": form,
        "url_required": url_required,
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
    })
    ctx.update(extra_context)
    
    return render_to_response(template_name, RequestContext(request, ctx))


def signup(request, **kwargs):
    
    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", "account/signup.html")
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    success_url = kwargs.pop("success_url", None)
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)
    
    if request.method == "POST":
        form = form_class(request.POST, group=group)
        if form.is_valid():
            user = form.save(request=request)
            return complete_signup(request, user, success_url)
    else:
        form = form_class(group=group)
    
    ctx.update({
        "form": form,
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))

@login_required
def email(request, **kwargs):
    form_class = kwargs.pop("form_class", AddEmailForm)
    template_name = kwargs.pop("template_name", "account/email.html")
    
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
                add_email_form = form_class() # @@@
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
                        EmailConfirmation.objects.send_confirmation(email_address)
                    except EmailAddress.DoesNotExist:
                        pass
                elif request.POST.has_key("action_remove"):
                    email = request.POST["email"]
                    try:
                        email_address = EmailAddress.objects.get(
                            user=request.user,
                            email=email
                        )
                        email_address.delete()
                        messages.add_message(request, messages.SUCCESS,
                            ugettext("Removed e-mail address %(email)s") % {
                                "email": email,
                            }
                        )
                    except EmailAddress.DoesNotExist:
                        pass
                elif request.POST.has_key("action_primary"):
                    email = request.POST["email"]
                    email_address = EmailAddress.objects.get(
                        user=request.user,
                        email=email,
                    )
                    email_address.set_as_primary()
                    messages.add_message(request, messages.SUCCESS,
                                         ugettext("Primary e-mail address set"))
    else:
        add_email_form = form_class()
    
    ctx = {
        "add_email_form": add_email_form,
    }
    
    return render_to_response(template_name, RequestContext(request, ctx))

@login_required
def password_change(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ChangePasswordForm)
    template_name = kwargs.pop("template_name", "account/password_change.html")
    
    group, bridge = group_and_bridge(kwargs)
    
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
    
    ctx = group_context(group, bridge)
    ctx.update({
        "password_change_form": password_change_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def password_set(request, **kwargs):
    
    form_class = kwargs.pop("form_class", SetPasswordForm)
    template_name = kwargs.pop("template_name", "account/password_set.html")
    
    group, bridge = group_and_bridge(kwargs)
    
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
    
    ctx = group_context(group, bridge)
    ctx.update({
        "password_set_form": password_set_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


# @login_required
# def password_delete(request, **kwargs):
#     
#     template_name = kwargs.pop("template_name", "account/password_delete.html")
#     
#     # prevent this view when openids is not present or it is empty.
#     if not request.user.password or \
#         (not hasattr(request, "openids") or \
#             not getattr(request, "openids", None)):
#         return HttpResponseForbidden()
#     
#     group, bridge = group_and_bridge(kwargs)
#     
#     if request.method == "POST":
#         request.user.password = u""
#         request.user.save()
#         return HttpResponseRedirect(reverse("acct_passwd_delete_done"))
#     
#     ctx = group_context(group, bridge)
#     
#     return render_to_response(template_name, RequestContext(request, ctx))


def password_reset(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ResetPasswordForm)
    template_name = kwargs.pop("template_name", "account/password_reset.html")
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            
            if group:
                redirect_to = bridge.reverse(password_reset_done, group)
            else:
                redirect_to = reverse(password_reset_done)
            return HttpResponseRedirect(redirect_to)
    else:
        password_reset_form = form_class()
    
    ctx.update({
        "password_reset_form": password_reset_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset_done(request, **kwargs):
    
    template_name = kwargs.pop("template_name", "account/password_reset_done.html")
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset_from_key(request, uidb36, key, **kwargs):
    
    form_class = kwargs.get("form_class", ResetPasswordKeyForm)
    template_name = kwargs.get("template_name", "account/password_reset_from_key.html")
    token_generator = kwargs.get("token_generator", default_token_generator)
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
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
        ctx.update({
            "form": password_reset_key_form,
        })
    else:
        ctx.update({
            "token_fail": True,
        })
    
    return render_to_response(template_name, RequestContext(request, ctx))







def logout(request):
    messages.add_message(request, messages.SUCCESS,
        ugettext("You have signed out.")
    )
    from django.contrib.auth.views import logout as _logout
    return _logout(request, template_name="account/logout.html")

from __future__ import unicode_literals

import re
import warnings
import json

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from ..utils import (import_attribute, get_user_model,
                     generate_unique_username,
                     resolve_url, get_current_site,
                     build_absolute_uri)

from . import app_settings

# Don't bother turning this into a setting, as changing this also
# requires changing the accompanying form error message. So if you
# need to change any of this, simply override clean_username().
USERNAME_REGEX = re.compile(r'^[\w.@+-]+$', re.UNICODE)


class DefaultAccountAdapter(object):

    def stash_verified_email(self, request, email):
        request.session['account_verified_email'] = email

    def unstash_verified_email(self, request):
        ret = request.session.get('account_verified_email')
        request.session['account_verified_email'] = None
        return ret

    def stash_user(self, request, user):
        request.session['account_user'] = user

    def unstash_user(self, request):
        return request.session.pop('account_user', None)

    def is_email_verified(self, request, email):
        """
        Checks whether or not the email address is already verified
        beyond allauth scope, for example, by having accepted an
        invitation before signing up.
        """
        ret = False
        verified_email = request.session.get('account_verified_email')
        if verified_email:
            ret = verified_email.lower() == email.lower()
        return ret

    def format_email_subject(self, subject):
        prefix = app_settings.EMAIL_SUBJECT_PREFIX
        if prefix is None:
            site = get_current_site()
            prefix = "[{name}] ".format(name=site.name)
        return prefix + force_text(subject)

    def render_mail(self, template_prefix, email, context):
        """
        Renders an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                                   context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = '{0}_message.{1}'.format(template_prefix, ext)
                bodies[ext] = render_to_string(template_name,
                                               context).strip()
            except TemplateDoesNotExist:
                if ext == 'txt' and not bodies:
                    # We need at least one body
                    raise
        if 'txt' in bodies:
            msg = EmailMultiAlternatives(subject,
                                         bodies['txt'],
                                         settings.DEFAULT_FROM_EMAIL,
                                         [email])
            if 'html' in bodies:
                msg.attach_alternative(bodies['html'], 'text/html')
        else:
            msg = EmailMessage(subject,
                               bodies['html'],
                               settings.DEFAULT_FROM_EMAIL,
                               [email])
            msg.content_subtype = 'html'  # Main content is now text/html
        return msg

    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        msg.send()

    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.  Note
        that URLs passed explicitly (e.g. by passing along a `next`
        GET parameter) take precedence over the value returned here.
        """
        assert request.user.is_authenticated()
        url = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if url:
            warnings.warn("LOGIN_REDIRECT_URLNAME is deprecated, simply"
                          " use LOGIN_REDIRECT_URL with a URL name",
                          DeprecationWarning)
        else:
            url = settings.LOGIN_REDIRECT_URL
        return resolve_url(url)

    def get_logout_redirect_url(self, request):
        """
        Returns the URL to redirect to after the user logs out. Note that
        this method is also invoked if you attempt to log out while no users
        is logged in. Therefore, request.user is not guaranteed to be an
        authenticated user.
        """
        return resolve_url(app_settings.LOGOUT_REDIRECT_URL)

    def get_email_confirmation_redirect_url(self, request):
        """
        The URL to return to after successful e-mail confirmation.
        """
        if request.user.is_authenticated():
            if app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL:
                return  \
                    app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL
            else:
                return self.get_login_redirect_url(request)
        else:
            return app_settings.EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        return True

    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        return user

    def populate_username(self, request, user):
        """
        Fills in a valid username, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        from .utils import user_username, user_email, user_field
        first_name = user_field(user, 'first_name')
        last_name = user_field(user, 'last_name')
        email = user_email(user)
        username = user_username(user)
        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username(user,
                          username
                          or self.generate_unique_username([first_name,
                                                            last_name,
                                                            email,
                                                            'user']))

    def generate_unique_username(self, txts, regex=None):
        return generate_unique_username(txts, regex)

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from .utils import user_username, user_email, user_field

        data = form.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        username = data.get('username')
        user_email(user, email)
        user_username(user, username)
        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user

    def clean_username(self, username, shallow=False):
        """
        Validates the username. You can hook into this if you want to
        (dynamically) restrict what usernames can be chosen.
        """
        if not USERNAME_REGEX.match(username):
            raise forms.ValidationError(_("Usernames can only contain "
                                          "letters, digits and @/./+/-/_."))

        # TODO: Add regexp support to USERNAME_BLACKLIST
        username_blacklist_lower = [ub.lower()
                                    for ub in app_settings.USERNAME_BLACKLIST]
        if username.lower() in username_blacklist_lower:
            raise forms.ValidationError(_("Username can not be used. "
                                          "Please use other username."))
        # Skipping database lookups when shallow is True, needed for unique
        # username generation.
        if not shallow:
            username_field = app_settings.USER_MODEL_USERNAME_FIELD
            assert username_field
            user_model = get_user_model()
            try:
                query = {username_field + '__iexact': username}
                user_model.objects.get(**query)
            except user_model.DoesNotExist:
                return username
            raise forms.ValidationError(
                _("This username is already taken. Please choose another."))
        return username

    def clean_email(self, email):
        """
        Validates an email value. You can hook into this if you want to
        (dynamically) restrict what email addresses can be chosen.
        """
        return email

    def clean_password(self, password):
        """
        Validates a password. You can hook into this if you want to
        restric the allowed password choices.
        """
        min_length = app_settings.PASSWORD_MIN_LENGTH
        if len(password) < min_length:
            raise forms.ValidationError(_("Password must be a minimum of {0} "
                                          "characters.").format(min_length))
        return password

    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        """
        Wrapper of `django.contrib.messages.add_message`, that reads
        the message text from a template.
        """
        if 'django.contrib.messages' in settings.INSTALLED_APPS:
            try:
                if message_context is None:
                    message_context = {}
                message = render_to_string(message_template,
                                           message_context).strip()
                if message:
                    messages.add_message(request, level, message,
                                         extra_tags=extra_tags)
            except TemplateDoesNotExist:
                pass

    def ajax_response(self, request, response, redirect_to=None, form=None):
        data = {}
        status = response.status_code

        if redirect_to:
            status = 200
            data['location'] = redirect_to
        if form:
            if form.is_valid():
                status = 200
            else:
                status = 400
                data['form_errors'] = form._errors
            if hasattr(response, 'render'):
                response.render()
            data['html'] = response.content.decode('utf8')
        return HttpResponse(json.dumps(data),
                            status=status,
                            content_type='application/json')

    def login(self, request, user):
        # HACK: This is not nice. The proper Django way is to use an
        # authentication backend
        if not hasattr(user, 'backend'):
            user.backend \
                = "allauth.account.auth_backends.AuthenticationBackend"
        django_login(request, user)

    def logout(self, request):
        django_logout(request)

    def confirm_email(self, request, email_address):
        """
        Marks the email address as confirmed on the db
        """
        email_address.verified = True
        email_address.set_as_primary(conditional=True)
        email_address.save()

    def set_password(self, user, password):
        user.set_password(password)
        user.save()

    def get_user_search_fields(self):
        user = get_user_model()()
        return filter(lambda a: a and hasattr(user, a),
                      [app_settings.USER_MODEL_USERNAME_FIELD,
                       'first_name', 'last_name', 'email'])

    def is_safe_url(self, url):
        from django.utils.http import is_safe_url
        return is_safe_url(url)

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse(
            "account_confirm_email",
            args=[emailconfirmation.key])
        ret = build_absolute_uri(
            request,
            url,
            protocol=app_settings.DEFAULT_HTTP_PROTOCOL)
        return ret

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()

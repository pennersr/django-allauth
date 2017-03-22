from __future__ import unicode_literals

import hashlib
import json
import time
import warnings

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_backends,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import app_settings
from ..compat import is_authenticated, reverse, validate_password
from ..utils import (
    build_absolute_uri,
    email_address_exists,
    generate_unique_username,
    get_user_model,
    import_attribute,
)
from .signals import user_logged_out


try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


class DefaultAccountAdapter(object):

    error_messages = {
        'username_blacklisted':
        _('Username can not be used. Please use other username.'),
        'username_taken':
        AbstractUser._meta.get_field('username').error_messages['unique'],
        'too_many_login_attempts':
        _('Too many failed login attempts. Try again later.'),
        'email_taken':
        _("A user is already registered with this e-mail address."),
    }

    def __init__(self, request=None):
        self.request = request

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
            site = get_current_site(self.request)
            prefix = "[{name}] ".format(name=site.name)
        return prefix + force_text(subject)

    def get_from_email(self):
        """
        This is a hook that can be overridden to programatically
        set the 'from' email address for sending emails
        """
        return settings.DEFAULT_FROM_EMAIL

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

        from_email = self.get_from_email()

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
                                         from_email,
                                         [email])
            if 'html' in bodies:
                msg.attach_alternative(bodies['html'], 'text/html')
        else:
            msg = EmailMessage(subject,
                               bodies['html'],
                               from_email,
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
        assert is_authenticated(request.user)
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
        if is_authenticated(request.user):
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
            user_username(
                user,
                username or self.generate_unique_username([
                    first_name,
                    last_name,
                    email,
                    username,
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
        for validator in app_settings.USERNAME_VALIDATORS:
            validator(username)

        # TODO: Add regexp support to USERNAME_BLACKLIST
        username_blacklist_lower = [ub.lower()
                                    for ub in app_settings.USERNAME_BLACKLIST]
        if username.lower() in username_blacklist_lower:
            raise forms.ValidationError(
                self.error_messages['username_blacklisted'])
        # Skipping database lookups when shallow is True, needed for unique
        # username generation.
        if not shallow:
            from .utils import filter_users_by_username
            if filter_users_by_username(username).exists():
                user_model = get_user_model()
                username_field = app_settings.USER_MODEL_USERNAME_FIELD
                error_message = user_model._meta.get_field(
                    username_field).error_messages.get('unique')
                if not error_message:
                    error_message = self.error_messages['username_taken']
                raise forms.ValidationError(error_message)
        return username

    def clean_email(self, email):
        """
        Validates an email value. You can hook into this if you want to
        (dynamically) restrict what email addresses can be chosen.
        """
        return email

    def clean_password(self, password, user=None):
        """
        Validates a password. You can hook into this if you want to
        restric the allowed password choices.
        """
        min_length = app_settings.PASSWORD_MIN_LENGTH
        if min_length and len(password) < min_length:
            raise forms.ValidationError(_("Password must be a minimum of {0} "
                                          "characters.").format(min_length))
        validate_password(password, user)
        return password

    def validate_unique_email(self, email):
        if email_address_exists(email):
            raise forms.ValidationError(self.error_messages['email_taken'])
        return email

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

    def ajax_response(self, request, response, redirect_to=None, form=None,
                      data=None):
        resp = {}
        status = response.status_code

        if redirect_to:
            status = 200
            resp['location'] = redirect_to
        if form:
            if request.method == 'POST':
                if form.is_valid():
                    status = 200
                else:
                    status = 400
            else:
                status = 200
            resp['form'] = self.ajax_response_form(form)
            if hasattr(response, 'render'):
                response.render()
            resp['html'] = response.content.decode('utf8')
            if data is not None:
                resp['data'] = data
        return HttpResponse(json.dumps(resp),
                            status=status,
                            content_type='application/json')

    def ajax_response_form(self, form):
        form_spec = {
            'fields': {},
            'field_order': [],
            'errors': form.non_field_errors()
        }
        for field in form:
            field_spec = {
                'label': force_text(field.label),
                'value': field.value(),
                'help_text': force_text(field.help_text),
                'errors': [
                    force_text(e) for e in field.errors
                ],
                'widget': {
                    'attrs': {
                        k: force_text(v)
                        for k, v in field.field.widget.attrs.items()
                    }
                }
            }
            form_spec['fields'][field.html_name] = field_spec
            form_spec['field_order'].append(field.html_name)
        return form_spec

    def login(self, request, user):
        # HACK: This is not nice. The proper Django way is to use an
        # authentication backend
        if not hasattr(user, 'backend'):
            from .auth_backends import AuthenticationBackend
            backends = get_backends()
            backend = None
            for b in backends:
                if isinstance(b, AuthenticationBackend):
                    # prefer our own backend
                    backend = b
                    break
                elif not backend and hasattr(b, 'get_user'):
                    # Pick the first vald one
                    backend = b
            backend_path = '.'.join([backend.__module__,
                                     backend.__class__.__name__])
            user.backend = backend_path
        django_login(request, user)

    def logout(self, request):
        user = request.user
        django_logout(request)
        user_logged_out.send(
            sender=user.__class__,
            request=request,
            user=user)

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
            url)
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

    def respond_user_inactive(self, request, user):
        return HttpResponseRedirect(
            reverse('account_inactive'))

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect(
            reverse('account_email_verification_sent'))

    def _get_login_attempts_cache_key(self, request, **credentials):
        site = get_current_site(request)
        login = credentials.get('email', credentials.get('username', ''))
        login_key = hashlib.sha256(login.encode('utf8')).hexdigest()
        return 'allauth/login_attempts@{site_id}:{login}'.format(
            site_id=site.pk,
            login=login_key)

    def pre_authenticate(self, request, **credentials):
        if app_settings.LOGIN_ATTEMPTS_LIMIT:
            cache_key = self._get_login_attempts_cache_key(
                request, **credentials)
            login_data = cache.get(cache_key, None)
            if login_data:
                dt = timezone.now()
                current_attempt_time = time.mktime(dt.timetuple())
                if (len(login_data) >= app_settings.LOGIN_ATTEMPTS_LIMIT and
                        current_attempt_time < (
                            login_data[-1] +
                            app_settings.LOGIN_ATTEMPTS_TIMEOUT)):
                    raise forms.ValidationError(
                        self.error_messages['too_many_login_attempts'])

    def authenticate(self, request, **credentials):
        """Only authenticates, does not actually login. See `login`"""
        self.pre_authenticate(request, **credentials)
        user = authenticate(**credentials)
        if user:
            cache_key = self._get_login_attempts_cache_key(
                request, **credentials)
            cache.delete(cache_key)
        else:
            self.authentication_failed(request, **credentials)
        return user

    def authentication_failed(self, request, **credentials):
        cache_key = self._get_login_attempts_cache_key(request, **credentials)
        data = cache.get(cache_key, [])
        dt = timezone.now()
        data.append(time.mktime(dt.timetuple()))
        cache.set(cache_key, data, app_settings.LOGIN_ATTEMPTS_TIMEOUT)


def get_adapter(request=None):
    return import_attribute(app_settings.ADAPTER)(request)

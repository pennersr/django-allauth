import warnings

from django.conf import settings
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib import messages

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from ..utils import (import_attribute, get_user_model,
                     generate_unique_username,
                     resolve_url)

from . import app_settings


class DefaultAccountAdapter(object):

    def stash_verified_email(self, request, email):
        request.session['account_verified_email'] = email

    def unstash_verified_email(self, request):
        ret = request.session.get('account_verified_email')
        request.session['account_verified_email'] = None
        return ret

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
            site = Site.objects.get_current()
            prefix = u"[{name}] ".format(name=site.name)
        return prefix + force_text(subject)

    def send_mail(self, template_prefix, email, context):
        """
        Sends an e-mail to `email`.  `template_prefix` identifies the
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
        Returns the URL to redriect to after the user logs out. Note that
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
                          or generate_unique_username([first_name,
                                                       last_name,
                                                       email,
                                                       'user']))

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
        user_field(user, 'first_name', first_name or '')
        user_field(user, 'last_name', last_name or '')
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

    def clean_username(self, username):
        """
        Validates the username. You can hook into this if you want to
        (dynamically) restrict what usernames can be chosen.
        """
        from django.contrib.auth.forms import UserCreationForm
        USERNAME_REGEX = UserCreationForm().fields['username'].regex
        if not USERNAME_REGEX.match(username):
            raise forms.ValidationError(_("Usernames can only contain "
                                          "letters, digits and @/./+/-/_."))

        # TODO: Add regexp support to USERNAME_BLACKLIST
        if username in app_settings.USERNAME_BLACKLIST:
            raise forms.ValidationError(_("Username can not be used. "
                                          "Please use other username."))
        username_field = app_settings.USER_MODEL_USERNAME_FIELD
        assert username_field
        user_model = get_user_model()
        try:
            query = {username_field + '__iexact': username}
            user_model.objects.get(**query)
        except user_model.DoesNotExist:
            return username
        raise forms.ValidationError(_("This username is already taken. Please "
                                      "choose another."))

    def clean_email(self, email):
        """
        Validates an email value. You can hook into this if you want to
        (dynamically) restrict what email addresses can be chosen.
        """
        return email

    def add_message(self, request, level, message_template,
                    message_context={}, extra_tags=''):
        """
        Wrapper of `django.contrib.messages.add_message`, that reads
        the message text from a template.
        """
        if 'django.contrib.messages' in settings.INSTALLED_APPS:
            try:
                message = render_to_string(message_template,
                                           message_context).strip()
                if message:
                    messages.add_message(request, level, message,
                                         extra_tags=extra_tags)
            except TemplateDoesNotExist:
                pass


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()

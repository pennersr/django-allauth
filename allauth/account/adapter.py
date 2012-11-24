from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import send_mail

from allauth.utils import import_attribute

import app_settings

class DefaultAccountAdapter(object):

    def stash_email_verified(self, request, email):
        request.session['account_email_verified'] = email

    def is_email_verified(self, request, email):
        """
        Checks whether or not the email address is already verified
        beyond allauth scope, for example, by having accepted an
        invitation before signing up.
        """
        ret = False
        verified_email = request.session.get('account_email_verified')
        if verified_email:
            ret = verified_email.lower() == email.lower()
        return ret

    def format_email_subject(self, subject):
        prefix = app_settings.EMAIL_SUBJECT_PREFIX
        if prefix is None:
            site = Site.objects.get_current()
            prefix = "[{name}] ".format(name=site.name)
        return prefix + unicode(subject)

    def send_mail(self, template_prefix, email, context):
        """
        Sends an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                                   context)
        body = render_to_string('{0}_message.txt'.format(template_prefix),
                                context).strip()
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])

def get_adapter():
    return import_attribute(app_settings.ADAPTER)()


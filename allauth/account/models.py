from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from django.utils.crypto import get_random_string

from ..utils import build_absolute_uri
from .. import app_settings as allauth_app_settings
from . import app_settings
from . import signals

from .utils import user_email
from .managers import EmailAddressManager, EmailConfirmationManager
from .adapter import get_adapter


@python_2_unicode_compatible
class EmailAddress(models.Model):

    user = models.ForeignKey(allauth_app_settings.USER_MODEL,
                             verbose_name=_('user'))
    email = models.EmailField(unique=app_settings.UNIQUE_EMAIL,
                              verbose_name=_('e-mail address'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    primary = models.BooleanField(verbose_name=_('primary'), default=False)

    objects = EmailAddressManager()

    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        if not app_settings.UNIQUE_EMAIL:
            unique_together = [("user", "email")]

    def __str__(self):
        return "%s (%s)" % (self.email, self.user)

    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        user_email(self.user, self.email)
        self.user.save()
        return True

    def send_confirmation(self, request, signup=False):
        confirmation = EmailConfirmation.create(self)
        confirmation.send(request, signup=signup)
        return confirmation

    def change(self, request, new_email, confirm=True):
        """
        Given a new email address, change self and re-confirm.
        """
        with transaction.commit_on_success():
            user_email(self.user, new_email)
            self.user.save()
            self.email = new_email
            self.verified = False
            self.save()
            if confirm:
                self.send_confirmation(request)


@python_2_unicode_compatible
class EmailConfirmation(models.Model):

    email_address = models.ForeignKey(EmailAddress,
                                      verbose_name=_('e-mail address'))
    created = models.DateTimeField(verbose_name=_('created'),
                                   default=timezone.now)
    sent = models.DateTimeField(verbose_name=_('sent'), null=True)
    key = models.CharField(verbose_name=_('key'), max_length=64, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")

    def __str__(self):
        return "confirmation for %s" % self.email_address

    @classmethod
    def create(cls, email_address):
        key = get_random_string(64).lower()
        return cls._default_manager.create(email_address=email_address,
                                           key=key)

    def key_expired(self):
        expiration_date = self.sent \
            + datetime.timedelta(days=app_settings
                                 .EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= timezone.now()
    key_expired.boolean = True

    def confirm(self, request):
        if not self.key_expired() and not self.email_address.verified:
            email_address = self.email_address
            get_adapter().confirm_email(request, email_address)
            signals.email_confirmed.send(sender=self.__class__,
                                         request=request,
                                         email_address=email_address)
            return email_address

    def send(self, request, signup=False, **kwargs):
        current_site = kwargs["site"] if "site" in kwargs \
            else Site.objects.get_current()
        activate_url = reverse("account_confirm_email", args=[self.key])
        activate_url = build_absolute_uri(request,
                                          activate_url,
                                          protocol=app_settings.DEFAULT_HTTP_PROTOCOL)
        ctx = {
            "user": self.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": self.key,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        get_adapter().send_mail(email_template,
                                self.email_address.email,
                                ctx)
        self.sent = timezone.now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__,
                                             confirmation=self)

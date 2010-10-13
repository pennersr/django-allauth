import sys

from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import get_language_from_request, ugettext_lazy as _

from django.contrib.auth.models import User, AnonymousUser

from emailconfirmation.models import EmailAddress, EmailConfirmation
from emailconfirmation.signals import email_confirmed


# class PasswordReset(models.Model):
#     user = models.ForeignKey(User, verbose_name=_("user"))
#     
#     temp_key = models.CharField(_("temp_key"), max_length=100)
#     timestamp = models.DateTimeField(_("timestamp"), default=datetime.now)
#     reset = models.BooleanField(_("reset yet?"), default=False)
#     
#     def __unicode__(self):
#         return "%s (key=%s, reset=%r)" % (
#             self.user.username,
#             self.temp_key,
#             self.reset
#         )


def mark_user_active(sender, instance=None, **kwargs):
    user = kwargs.get("email_address").user
    user.is_active = True
    user.save()


email_confirmed.connect(mark_user_active, sender=EmailConfirmation)

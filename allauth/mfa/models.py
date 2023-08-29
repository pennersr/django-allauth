from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuthenticatorManager(models.Manager):
    def delete_dangling_recovery_codes(self, user):
        qs = Authenticator.objects.filter(user=user)
        if not qs.exclude(type=Authenticator.Type.RECOVERY_CODES).exists():
            qs.delete()


class Authenticator(models.Model):
    class Type(models.TextChoices):
        RECOVERY_CODES = "recovery_codes", _("Recovery codes")
        TOTP = "totp", _("TOTP Authenticator")

    objects = AuthenticatorManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=Type.choices)
    data = models.JSONField()

    class Meta:
        unique_together = (("user", "type"),)

    def wrap(self):
        from allauth.mfa.recovery_codes import RecoveryCodes
        from allauth.mfa.totp import TOTP

        return {
            self.Type.TOTP: TOTP,
            self.Type.RECOVERY_CODES: RecoveryCodes,
        }[
            self.type
        ](self)

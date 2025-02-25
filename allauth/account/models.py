import datetime
import time
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.core import signing
from django.db import models
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.managers import (
    EmailAddressManager,
    EmailConfirmationManager,
)


class EmailAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
    )
    email = models.EmailField(
        db_index=True,
        max_length=app_settings.EMAIL_MAX_LENGTH,
        verbose_name=_("email address"),
    )
    verified = models.BooleanField(verbose_name=_("verified"), default=False)
    primary = models.BooleanField(verbose_name=_("primary"), default=False)

    objects = EmailAddressManager()

    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        unique_together = [("user", "email")]
        constraints = [
            UniqueConstraint(
                fields=["user", "primary"],
                name="unique_primary_email",
                condition=Q(primary=True),
            )
        ]
        if app_settings.UNIQUE_EMAIL:
            constraints.append(
                UniqueConstraint(
                    fields=["email"],
                    name="unique_verified_email",
                    condition=Q(verified=True),
                )
            )

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.email.lower()

    def can_set_verified(self):
        if self.verified:
            return True
        conflict = False
        if app_settings.UNIQUE_EMAIL:
            conflict = (
                EmailAddress.objects.exclude(pk=self.pk)
                .filter(verified=True, email=self.email)
                .exists()
            )
        return not conflict

    def set_verified(self, commit=True):
        if self.verified:
            return True
        if self.can_set_verified():
            self.verified = True
            if commit:
                self.save(update_fields=["verified"])
        return self.verified

    def set_as_primary(self, conditional=False):
        """Marks the email address as primary. In case of `conditional`, it is
        only marked as primary if there is no other primary email address set.
        """
        from allauth.account.utils import user_email

        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        user_email(self.user, self.email, commit=True)
        return True

    def send_confirmation(self, request=None, signup=False):
        model = get_emailconfirmation_model()
        confirmation = model.create(self)
        confirmation.send(request, signup=signup)
        return confirmation

    def remove(self):
        from allauth.account.utils import user_email

        self.delete()
        if user_email(self.user) == self.email:
            alt = (
                EmailAddress.objects.filter(user=self.user)
                .order_by("-verified")
                .first()
            )
            alt_email = ""
            if alt:
                alt_email = alt.email
            user_email(self.user, alt_email, commit=True)


class EmailConfirmationMixin:
    def confirm(self, request) -> Optional[EmailAddress]:
        email_address = self.email_address  # type: ignore[attr-defined]
        if not email_address.verified:
            confirmed = get_adapter().confirm_email(request, email_address)
            if confirmed:
                return email_address
        return None

    def send(self, request=None, signup=False) -> None:
        get_adapter().send_confirmation_mail(request, self, signup)
        signals.email_confirmation_sent.send(
            sender=self.__class__,
            request=request,
            confirmation=self,
            signup=signup,
        )


class EmailConfirmation(EmailConfirmationMixin, models.Model):
    email_address = models.ForeignKey(
        EmailAddress,
        verbose_name=_("email address"),
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(verbose_name=_("created"), default=timezone.now)
    sent = models.DateTimeField(verbose_name=_("sent"), null=True)
    key = models.CharField(verbose_name=_("key"), max_length=64, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")

    def __str__(self):
        return "confirmation for %s" % self.email_address

    @classmethod
    def create(cls, email_address):
        key = get_adapter().generate_emailconfirmation_key(email_address.email)
        return cls._default_manager.create(email_address=email_address, key=key)

    @classmethod
    def from_key(cls, key):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        emailconfirmation = qs.filter(key=key.lower()).first()
        return emailconfirmation

    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
        )
        return expiration_date <= timezone.now()

    key_expired.boolean = True  # type: ignore[attr-defined]

    def confirm(self, request) -> Optional[EmailAddress]:
        if not self.key_expired():
            return super().confirm(request)
        return None

    def send(self, request=None, signup=False) -> None:
        super().send(request=request, signup=signup)
        self.sent = timezone.now()
        self.save()


class EmailConfirmationHMAC(EmailConfirmationMixin):
    def __init__(self, email_address):
        self.email_address = email_address

    @classmethod
    def create(cls, email_address):
        return EmailConfirmationHMAC(email_address)

    @property
    def key(self):
        return signing.dumps(obj=self.email_address.pk, salt=app_settings.SALT)

    @classmethod
    def from_key(cls, key):
        try:
            max_age = 60 * 60 * 24 * app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
            pk = signing.loads(key, max_age=max_age, salt=app_settings.SALT)
            ret = EmailConfirmationHMAC(EmailAddress.objects.get(pk=pk, verified=False))
        except (
            signing.SignatureExpired,
            signing.BadSignature,
            EmailAddress.DoesNotExist,
        ):
            ret = None
        return ret

    def key_expired(self):
        return False


class Login:
    """
    Represents a user that is in the process of logging in.

    Keyword arguments:

    signup -- Indicates whether or not sending the
    email is essential (during signup), or if it can be skipped (e.g. in
    case email verification is optional and we are only logging in).
    """

    # Optional, because we might be prentending logins to prevent user
    # enumeration.
    user: Optional[AbstractBaseUser]
    email_verification: app_settings.EmailVerificationMethod
    signal_kwargs: Optional[Dict]
    signup: bool
    email: Optional[str]
    state: Dict
    initiated_at: float
    redirect_url: Optional[str]

    def __init__(
        self,
        user,
        email_verification: Optional[app_settings.EmailVerificationMethod] = None,
        redirect_url: Optional[str] = None,
        signal_kwargs: Optional[Dict] = None,
        signup: bool = False,
        email: Optional[str] = None,
        state: Optional[Dict] = None,
        initiated_at: Optional[float] = None,
    ):
        self.user = user
        if not email_verification:
            email_verification = app_settings.EMAIL_VERIFICATION
        self.email_verification = email_verification
        self.redirect_url = redirect_url
        self.signal_kwargs = signal_kwargs
        self.signup = signup
        self.email = email
        self.state = {} if state is None else state
        self.initiated_at = initiated_at if initiated_at else time.time()

    def serialize(self):
        from allauth.account.utils import user_pk_to_url_str

        # :-( Knowledge of the `socialaccount` is entering the `account` app.
        signal_kwargs = self.signal_kwargs
        if signal_kwargs is not None:
            sociallogin = signal_kwargs.get("sociallogin")
            if sociallogin is not None:
                signal_kwargs = signal_kwargs.copy()
                signal_kwargs["sociallogin"] = sociallogin.serialize()

        data = {
            "user_pk": user_pk_to_url_str(self.user) if self.user else None,
            "email_verification": self.email_verification,
            "signup": self.signup,
            "redirect_url": self.redirect_url,
            "email": self.email,
            "signal_kwargs": signal_kwargs,
            "state": self.state,
            "initiated_at": self.initiated_at,
        }
        return data

    @classmethod
    def deserialize(cls, data):
        from allauth.account.utils import url_str_to_user_pk

        user = None
        user_pk = data["user_pk"]
        if user_pk is not None:
            user = (
                get_user_model().objects.filter(pk=url_str_to_user_pk(user_pk)).first()
            )
        try:
            # :-( Knowledge of the `socialaccount` is entering the `account` app.
            signal_kwargs = data["signal_kwargs"]
            if signal_kwargs is not None:
                sociallogin = signal_kwargs.get("sociallogin")
                if sociallogin is not None:
                    from allauth.socialaccount.models import SocialLogin

                    signal_kwargs = signal_kwargs.copy()
                    signal_kwargs["sociallogin"] = SocialLogin.deserialize(sociallogin)

            return Login(
                user=user,
                email_verification=data["email_verification"],
                redirect_url=data["redirect_url"],
                signup=data["signup"],
                signal_kwargs=signal_kwargs,
                state=data["state"],
                initiated_at=data["initiated_at"],
            )
        except KeyError:
            raise ValueError()


def get_emailconfirmation_model():
    if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        from allauth.account.internal.flows.email_verification_by_code import (
            EmailVerificationModel,
        )

        return EmailVerificationModel
    elif app_settings.EMAIL_CONFIRMATION_HMAC:
        model = EmailConfirmationHMAC
    else:
        model = EmailConfirmation
    return model

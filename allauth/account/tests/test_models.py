import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from allauth.account.models import EmailAddress


class UUIDUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


def test_add_new_email(rf, user, settings):
    settings.ACCOUNT_CHANGE_EMAIL = True
    request = rf.get("/")
    assert EmailAddress.objects.filter(user=user).count() == 1
    new_email = EmailAddress.objects.add_new_email(request, user, "new@email.org")
    assert not new_email.verified
    assert not new_email.primary
    assert EmailAddress.objects.filter(user=user).count() == 2
    EmailAddress.objects.add_new_email(request, user, "new2@email.org")
    assert EmailAddress.objects.filter(user=user).count() == 2
    new_email.refresh_from_db()
    assert new_email.email == "new2@email.org"

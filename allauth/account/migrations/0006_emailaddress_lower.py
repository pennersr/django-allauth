from django.conf import settings
from django.db import migrations
from django.db.models.functions import Lower

from allauth.account import app_settings


def forwards(apps, schema_editor):
    EmailAddress = apps.get_model("account.EmailAddress")
    User = apps.get_model(settings.AUTH_USER_MODEL)
    EmailAddress.objects.all().exclude(email=Lower("email")).update(
        email=Lower("email")
    )
    email_field = app_settings.USER_MODEL_EMAIL_FIELD
    if email_field:
        User.objects.all().exclude(**{email_field: Lower(email_field)}).update(
            **{email_field: Lower(email_field)}
        )


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0005_emailaddress_idx_upper_email"),
    ]

    operations = [migrations.RunPython(forwards)]

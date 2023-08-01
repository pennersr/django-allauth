# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", True)
EMAIL_MAX_LENGTH = getattr(settings, "ACCOUNT_EMAIL_MAX_LENGTH", 254)


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailaddress",
            name="email",
            field=models.EmailField(
                unique=UNIQUE_EMAIL,
                max_length=EMAIL_MAX_LENGTH,
                verbose_name="email address",
            ),
        ),
    ]

    if not UNIQUE_EMAIL:
        operations += [
            migrations.AlterUniqueTogether(
                name="emailaddress",
                unique_together=set([("user", "email")]),
            ),
        ]

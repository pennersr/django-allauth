# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("socialaccount", "0002_token_max_lengths"),
    ]

    operations = [
        migrations.AlterField(
            model_name="socialaccount",
            name="extra_data",
            field=models.TextField(default="{}", verbose_name="extra data"),
            preserve_default=True,
        ),
    ]

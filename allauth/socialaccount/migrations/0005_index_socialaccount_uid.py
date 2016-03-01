# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0004_foreignkey_relation_between_app_and_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialaccount',
            name='uid',
            field=models.CharField(db_index=True, max_length=255, verbose_name='uid'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialaccount',
            name='uid',
            field=models.CharField(db_index=True, max_length=255, verbose_name='uid'),
        ),
    ]

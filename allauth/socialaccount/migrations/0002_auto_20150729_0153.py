# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialapp',
            name='sites',
            field=models.ManyToManyField(to='sites.Site', related_name='socialaccount_socialapp_set', blank=True),
        ),
    ]

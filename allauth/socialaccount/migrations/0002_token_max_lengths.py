# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialaccount',
            name='uid',
            field=models.CharField(max_length=getattr(settings, 'SOCIALACCOUNT_UID_MAX_LENGTH', 191), verbose_name='uid'),
        ),
        migrations.AlterField(
            model_name='socialapp',
            name='client_id',
            field=models.CharField(help_text='App ID, or consumer key', max_length=191, verbose_name='client id'),
        ),
        migrations.AlterField(
            model_name='socialapp',
            name='key',
            field=models.CharField(help_text='Key', max_length=191, verbose_name='key', blank=True),
        ),
        migrations.AlterField(
            model_name='socialapp',
            name='secret',
            field=models.CharField(help_text='API secret, client secret, or consumer secret', max_length=191, verbose_name='secret key', blank=True),
        ),
    ]

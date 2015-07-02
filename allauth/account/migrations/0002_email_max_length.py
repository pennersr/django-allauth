# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

UNIQUE_EMAIL = getattr(settings, 'ACCOUNT_UNIQUE_EMAIL', True)


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaddress',
            name='email',
            field=models.EmailField(unique=UNIQUE_EMAIL, max_length=254, verbose_name='e-mail address'),
        ),
    ]

    if not UNIQUE_EMAIL:
       operations += [
           migrations.AlterUniqueTogether(
               name='emailaddress',
               unique_together=set([('user', 'email')]),
           ),
       ]

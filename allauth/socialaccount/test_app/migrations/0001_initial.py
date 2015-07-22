# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    run_before = [
        ('socialaccount', '__first__'),
    ]
    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialAppSwapped',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('provider', models.CharField(max_length=30, verbose_name='provider', choices=[('bitbucket', 'Bitbucket'), ('dropbox', 'Dropbox'), ('instagram', 'Instagram'), ('openid', 'OpenID'), ('feedly', 'Feedly'), ('coinbase', 'Coinbase'), ('soundcloud', 'SoundCloud'), ('evernote', 'Evernote'), ('vk', 'VK'), ('hubic', 'Hubic'), ('orcid', 'Orcid.org'), ('windowslive', 'Live'), ('foursquare', 'Foursquare'), ('mailru', 'Mail.RU'), ('baidu', 'Baidu'), ('twitch', 'Twitch'), ('flickr', 'Flickr'), ('facebook', 'Facebook'), ('vimeo', 'Vimeo'), ('weibo', 'Weibo'), ('paypal', 'Paypal'), ('dropbox_oauth2', 'Dropbox'), ('google', 'Google'), ('twitter', 'Twitter'), ('odnoklassniki', 'Odnoklassniki'), ('xing', 'Xing'), ('linkedin_oauth2', 'LinkedIn'), ('github', 'GitHub'), ('tumblr', 'Tumblr'), ('bitly', 'Bitly'), ('persona', 'Persona'), ('angellist', 'AngelList'), ('linkedin', 'LinkedIn'), ('amazon', 'Amazon'), ('douban', 'Douban'), ('stackexchange', 'Stack Exchange'), ('spotify', 'Spotify')])),
                ('name', models.CharField(max_length=40, verbose_name='name')),
                ('client_id', models.CharField(max_length=100, help_text='App ID, or consumer key', verbose_name='client id')),
                ('secret', models.CharField(max_length=100, help_text='API secret, client secret, or consumer secret', verbose_name='secret key')),
                ('key', models.CharField(blank=True, max_length=100, help_text='Key', verbose_name='key')),
                ('new_field', models.CharField(max_length=100)),
                ('sites', models.ManyToManyField(blank=True, to='sites.Site')),
            ],
            options={
                'verbose_name': 'social application',
                'verbose_name_plural': 'social applications',
                'abstract': False,
            },
        ),
    ]

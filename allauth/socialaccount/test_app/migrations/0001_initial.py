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
                ('provider', models.CharField(max_length=30, verbose_name='provider', choices=[('stackexchange', 'Stack Exchange'), ('mailru', 'Mail.RU'), ('orcid', 'Orcid.org'), ('bitly', 'Bitly'), ('openid', 'OpenID'), ('angellist', 'AngelList'), ('xing', 'Xing'), ('github', 'GitHub'), ('soundcloud', 'SoundCloud'), ('weibo', 'Weibo'), ('facebook', 'Facebook'), ('bitbucket', 'Bitbucket'), ('linkedin_oauth2', 'LinkedIn'), ('twitter', 'Twitter'), ('coinbase', 'Coinbase'), ('windowslive', 'Live'), ('douban', 'Douban'), ('odnoklassniki', 'Odnoklassniki'), ('amazon', 'Amazon'), ('instagram', 'Instagram'), ('google', 'Google'), ('flickr', 'Flickr'), ('spotify', 'Spotify'), ('evernote', 'Evernote'), ('paypal', 'Paypal'), ('dropbox', 'Dropbox'), ('feedly', 'Feedly'), ('foursquare', 'Foursquare'), ('tumblr', 'Tumblr'), ('vk', 'VK'), ('linkedin', 'LinkedIn'), ('baidu', 'Baidu'), ('twitch', 'Twitch'), ('dropbox_oauth2', 'Dropbox'), ('vimeo', 'Vimeo'), ('persona', 'Persona'), ('hubic', 'Hubic')])),
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

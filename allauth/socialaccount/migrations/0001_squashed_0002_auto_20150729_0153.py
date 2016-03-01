# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import allauth.socialaccount.fields
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('socialaccount', '0001_initial'), ('socialaccount', '0002_auto_20150729_0153')]

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('provider', models.CharField(max_length=30, choices=[('xing', 'Xing'), ('mailru', 'Mail.RU'), ('instagram', 'Instagram'), ('odnoklassniki', 'Odnoklassniki'), ('stackexchange', 'Stack Exchange'), ('flickr', 'Flickr'), ('douban', 'Douban'), ('twitch', 'Twitch'), ('coinbase', 'Coinbase'), ('bitly', 'Bitly'), ('foursquare', 'Foursquare'), ('hubic', 'Hubic'), ('amazon', 'Amazon'), ('baidu', 'Baidu'), ('weibo', 'Weibo'), ('feedly', 'Feedly'), ('linkedin_oauth2', 'LinkedIn'), ('linkedin', 'LinkedIn'), ('dropbox', 'Dropbox'), ('facebook', 'Facebook'), ('soundcloud', 'SoundCloud'), ('github', 'GitHub'), ('windowslive', 'Live'), ('google', 'Google'), ('paypal', 'Paypal'), ('twitter', 'Twitter'), ('evernote', 'Evernote'), ('bitbucket', 'Bitbucket'), ('tumblr', 'Tumblr'), ('orcid', 'Orcid.org'), ('openid', 'OpenID'), ('angellist', 'AngelList'), ('vk', 'VK'), ('vimeo', 'Vimeo'), ('dropbox_oauth2', 'Dropbox'), ('spotify', 'Spotify'), ('persona', 'Persona')], verbose_name='provider')),
                ('uid', models.CharField(max_length=255, verbose_name='uid')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('extra_data', allauth.socialaccount.fields.JSONField(default='{}', verbose_name='extra data')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'swappable': 'SOCIALACCOUNT_SOCIAL_ACCOUNT_MODEL',
                'verbose_name_plural': 'social accounts',
                'verbose_name': 'social account',
            },
        ),
        migrations.CreateModel(
            name='SocialApp',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('provider', models.CharField(max_length=30, choices=[('xing', 'Xing'), ('mailru', 'Mail.RU'), ('instagram', 'Instagram'), ('odnoklassniki', 'Odnoklassniki'), ('stackexchange', 'Stack Exchange'), ('flickr', 'Flickr'), ('douban', 'Douban'), ('twitch', 'Twitch'), ('coinbase', 'Coinbase'), ('bitly', 'Bitly'), ('foursquare', 'Foursquare'), ('hubic', 'Hubic'), ('amazon', 'Amazon'), ('baidu', 'Baidu'), ('weibo', 'Weibo'), ('feedly', 'Feedly'), ('linkedin_oauth2', 'LinkedIn'), ('linkedin', 'LinkedIn'), ('dropbox', 'Dropbox'), ('facebook', 'Facebook'), ('soundcloud', 'SoundCloud'), ('github', 'GitHub'), ('windowslive', 'Live'), ('google', 'Google'), ('paypal', 'Paypal'), ('twitter', 'Twitter'), ('evernote', 'Evernote'), ('bitbucket', 'Bitbucket'), ('tumblr', 'Tumblr'), ('orcid', 'Orcid.org'), ('openid', 'OpenID'), ('angellist', 'AngelList'), ('vk', 'VK'), ('vimeo', 'Vimeo'), ('dropbox_oauth2', 'Dropbox'), ('spotify', 'Spotify'), ('persona', 'Persona')], verbose_name='provider')),
                ('name', models.CharField(max_length=40, verbose_name='name')),
                ('client_id', models.CharField(max_length=100, help_text='App ID, or consumer key', verbose_name='client id')),
                ('secret', models.CharField(max_length=100, help_text='API secret, client secret, or consumer secret', verbose_name='secret key')),
                ('key', models.CharField(max_length=100, help_text='Key', blank=True, verbose_name='key')),
                ('sites', models.ManyToManyField(blank=True, related_name='socialaccount_socialapp_set', to='sites.Site')),
            ],
            options={
                'swappable': 'SOCIALACCOUNT_SOCIAL_APP_MODEL',
                'verbose_name_plural': 'social applications',
                'verbose_name': 'social application',
            },
        ),
        migrations.CreateModel(
            name='SocialToken',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('token', models.TextField(help_text='"oauth_token" (OAuth1) or access token (OAuth2)', verbose_name='token')),
                ('token_secret', models.TextField(help_text='"oauth_token_secret" (OAuth1) or refresh token (OAuth2)', blank=True, verbose_name='token secret')),
                ('expires_at', models.DateTimeField(blank=True, verbose_name='expires at', null=True)),
                ('account', models.ForeignKey(to=settings.SOCIALACCOUNT_SOCIAL_ACCOUNT_MODEL)),
                ('app', models.ForeignKey(to=settings.SOCIALACCOUNT_SOCIAL_APP_MODEL)),
            ],
            options={
                'verbose_name_plural': 'social application tokens',
                'verbose_name': 'social application token',
            },
        ),
        migrations.AlterUniqueTogether(
            name='socialtoken',
            unique_together=set([('app', 'account')]),
        ),
        migrations.AlterUniqueTogether(
            name='socialaccount',
            unique_together=set([('provider', 'uid')]),
        ),
    ]

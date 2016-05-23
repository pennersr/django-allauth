# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import allauth


class Migration(migrations.Migration):

    run_before = [
        ('socialaccount', '__first__'),
    ]
    dependencies = [
        ('auth', '0001_initial'),
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
        migrations.CreateModel(
            name='SocialAccountSwapped',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('provider', models.CharField(choices=[('bitly', 'Bitly'), ('foursquare', 'Foursquare'), ('flickr', 'Flickr'), ('github', 'GitHub'), ('linkedin_oauth2', 'LinkedIn'), ('angellist', 'AngelList'), ('facebook', 'Facebook'), ('google', 'Google'), ('evernote', 'Evernote'), ('vimeo', 'Vimeo'), ('dropbox_oauth2', 'Dropbox'), ('dropbox', 'Dropbox'), ('xing', 'Xing'), ('amazon', 'Amazon'), ('stackexchange', 'Stack Exchange'), ('coinbase', 'Coinbase'), ('openid', 'OpenID'), ('feedly', 'Feedly'), ('vk', 'VK'), ('weibo', 'Weibo'), ('odnoklassniki', 'Odnoklassniki'), ('spotify', 'Spotify'), ('baidu', 'Baidu'), ('paypal', 'Paypal'), ('twitch', 'Twitch'), ('windowslive', 'Live'), ('hubic', 'Hubic'), ('orcid', 'Orcid.org'), ('tumblr', 'Tumblr'), ('twitter', 'Twitter'), ('linkedin', 'LinkedIn'), ('persona', 'Persona'), ('mailru', 'Mail.RU'), ('soundcloud', 'SoundCloud'), ('douban', 'Douban'), ('instagram', 'Instagram'), ('bitbucket', 'Bitbucket')], verbose_name='provider', max_length=30)),
                ('uid', models.CharField(verbose_name='uid', max_length=255)),
                ('last_login', models.DateTimeField(verbose_name='last login', auto_now=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', auto_now_add=True)),
                ('extra_data', allauth.socialaccount.fields.JSONField(verbose_name='extra data', default='{}')),
                ('new_field', models.CharField(max_length=100)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='test_swappable_app_socialaccountswapped_set')),
            ],
            options={
                'verbose_name': 'social account',
                'verbose_name_plural': 'social accounts',
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='socialaccountswapped',
            unique_together=set([('provider', 'uid')]),
        ),
    ]

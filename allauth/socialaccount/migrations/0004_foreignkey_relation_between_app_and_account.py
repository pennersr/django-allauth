# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

def set_social_app(apps, schema_editor):
    SocialApp = apps.get_model(settings.SOCIALACCOUNT_SOCIAL_APP_MODEL)
    SocialAccount = apps.get_model(settings.SOCIALACCOUNT_SOCIAL_ACCOUNT_MODEL)

    for social_account in SocialAccount.objects.filter(app__isnull=True):
        social_account.app = SocialApp.objects.first(provider=social_account.provider)
        social_account.save()

class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialaccount',
            name='app',
            field=models.ForeignKey(null=True, to=settings.SOCIALACCOUNT_SOCIAL_APP_MODEL),
        ),
        migrations.RunPython(set_social_app, lambda x, y: None),
        migrations.AlterField(
            model_name='socialaccount',
            name='app',
            field=models.ForeignKey(null=False, to=settings.SOCIALACCOUNT_SOCIAL_APP_MODEL),
        ),
        migrations.AlterField(
            model_name='socialaccount',
            name='provider',
            field=models.CharField(max_length=30, choices=[('vk', 'VK'), ('tumblr', 'Tumblr'), ('instagram', 'Instagram'), ('linkedin_oauth2', 'LinkedIn'), ('google', 'Google'), ('github', 'GitHub'), ('dropbox', 'Dropbox'), ('angellist', 'AngelList'), ('soundcloud', 'SoundCloud'), ('xing', 'Xing'), ('stackexchange', 'Stack Exchange'), ('vimeo', 'Vimeo'), ('dropbox_oauth2', 'Dropbox'), ('hubic', 'Hubic'), ('spotify', 'Spotify'), ('facebook', 'Facebook'), ('feedly', 'Feedly'), ('bitly', 'Bitly'), ('bitbucket', 'Bitbucket'), ('mailru', 'Mail.RU'), ('amazon', 'Amazon'), ('persona', 'Persona'), ('openid', 'OpenID'), ('odnoklassniki', 'Odnoklassniki'), ('windowslive', 'Live'), ('baidu', 'Baidu'), ('coinbase', 'Coinbase'), ('twitter', 'Twitter'), ('flickr', 'Flickr'), ('linkedin', 'LinkedIn'), ('twitch', 'Twitch'), ('orcid', 'Orcid.org'), ('weibo', 'Weibo'), ('foursquare', 'Foursquare'), ('douban', 'Douban'), ('evernote', 'Evernote'), ('paypal', 'Paypal')], verbose_name='provider'),
        ),
        migrations.AlterField(
            model_name='socialaccount',
            name='user',
            field=models.ForeignKey(related_name='socialaccount_socialaccount_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='socialapp',
            name='provider',
            field=models.CharField(max_length=30, choices=[('vk', 'VK'), ('tumblr', 'Tumblr'), ('instagram', 'Instagram'), ('linkedin_oauth2', 'LinkedIn'), ('google', 'Google'), ('github', 'GitHub'), ('dropbox', 'Dropbox'), ('angellist', 'AngelList'), ('soundcloud', 'SoundCloud'), ('xing', 'Xing'), ('stackexchange', 'Stack Exchange'), ('vimeo', 'Vimeo'), ('dropbox_oauth2', 'Dropbox'), ('hubic', 'Hubic'), ('spotify', 'Spotify'), ('facebook', 'Facebook'), ('feedly', 'Feedly'), ('bitly', 'Bitly'), ('bitbucket', 'Bitbucket'), ('mailru', 'Mail.RU'), ('amazon', 'Amazon'), ('persona', 'Persona'), ('openid', 'OpenID'), ('odnoklassniki', 'Odnoklassniki'), ('windowslive', 'Live'), ('baidu', 'Baidu'), ('coinbase', 'Coinbase'), ('twitter', 'Twitter'), ('flickr', 'Flickr'), ('linkedin', 'LinkedIn'), ('twitch', 'Twitch'), ('orcid', 'Orcid.org'), ('weibo', 'Weibo'), ('foursquare', 'Foursquare'), ('douban', 'Douban'), ('evernote', 'Evernote'), ('paypal', 'Paypal')], verbose_name='provider'),
        ),
        migrations.AlterUniqueTogether(
            name='socialaccount',
            unique_together=set([('app', 'uid')]),
        ),
    ]

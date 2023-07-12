# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models

import allauth.socialaccount.fields
from allauth import app_settings
from allauth.socialaccount.providers import registry


class Migration(migrations.Migration):
    dependencies = (
        [
            ("sites", "0001_initial"),
        ]
        if app_settings.SITES_ENABLED
        else []
        + [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ]
    )

    operations = [
        migrations.CreateModel(
            name="SocialAccount",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        max_length=30,
                        verbose_name="provider",
                        choices=registry.as_choices(),
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        max_length=getattr(
                            settings, "SOCIALACCOUNT_UID_MAX_LENGTH", 191
                        ),
                        verbose_name="uid",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(auto_now=True, verbose_name="last login"),
                ),
                (
                    "date_joined",
                    models.DateTimeField(auto_now_add=True, verbose_name="date joined"),
                ),
                (
                    "extra_data",
                    allauth.socialaccount.fields.JSONField(
                        default="{}", verbose_name="extra data"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name": "social account",
                "verbose_name_plural": "social accounts",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SocialApp",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        max_length=30,
                        verbose_name="provider",
                        choices=registry.as_choices(),
                    ),
                ),
                ("name", models.CharField(max_length=40, verbose_name="name")),
                (
                    "client_id",
                    models.CharField(
                        help_text="App ID, or consumer key",
                        max_length=100,
                        verbose_name="client id",
                    ),
                ),
                (
                    "secret",
                    models.CharField(
                        help_text="API secret, client secret, or consumer secret",
                        max_length=100,
                        verbose_name="secret key",
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        help_text="Key",
                        max_length=100,
                        verbose_name="key",
                        blank=True,
                    ),
                ),
            ]
            + (
                [
                    ("sites", models.ManyToManyField(to="sites.Site", blank=True)),
                ]
                if app_settings.SITES_ENABLED
                else []
            ),
            options={
                "verbose_name": "social application",
                "verbose_name_plural": "social applications",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SocialToken",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "token",
                    models.TextField(
                        help_text='"oauth_token" (OAuth1) or access token (OAuth2)',
                        verbose_name="token",
                    ),
                ),
                (
                    "token_secret",
                    models.TextField(
                        help_text='"oauth_token_secret" (OAuth1) or refresh token (OAuth2)',
                        verbose_name="token secret",
                        blank=True,
                    ),
                ),
                (
                    "expires_at",
                    models.DateTimeField(
                        null=True, verbose_name="expires at", blank=True
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        to="socialaccount.SocialAccount",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "app",
                    models.ForeignKey(
                        to="socialaccount.SocialApp", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name": "social application token",
                "verbose_name_plural": "social application tokens",
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="socialtoken",
            unique_together=set([("app", "account")]),
        ),
        migrations.AlterUniqueTogether(
            name="socialaccount",
            unique_together=set([("provider", "uid")]),
        ),
    ]

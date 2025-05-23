import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import allauth.idp.oidc.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=allauth.idp.oidc.models.default_client_id,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Client ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "secret",
                    models.CharField(
                        default=allauth.idp.oidc.models.default_client_secret,
                        max_length=200,
                    ),
                ),
                (
                    "scopes",
                    models.TextField(
                        default="openid",
                        help_text="The scope(s) the client is allowed to request. Provide one value per line, e.g.: openid(ENTER)profile(ENTER)email(ENTER)",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("confidential", "Confidential"),
                            ("public", "Public"),
                        ],
                        default="confidential",
                        max_length=20,
                    ),
                ),
                (
                    "grant_types",
                    models.TextField(
                        default="authorization_code",
                        help_text="A list of allowed grant types. Provide one value per line, e.g.: authorization_code(ENTER)client_credentials(ENTER)refresh_token(ENTER)",
                    ),
                ),
                (
                    "redirect_uris",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="A list of allowed redirect (callback) URLs, one per line.",
                    ),
                ),
                (
                    "cors_origins",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="A list of allowed origins for cross-origin requests, one per line.",
                        verbose_name="CORS allowed origins",
                    ),
                ),
                (
                    "response_types",
                    models.TextField(
                        default="code",
                        help_text="A list of allowed response types. Provide one value per line, e.g.: code(ENTER)id_token token(ENTER)",
                    ),
                ),
                (
                    "skip_consent",
                    models.BooleanField(
                        default=False,
                        help_text="Flag to allow skip the consent screen for this client",
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("data", models.JSONField(blank=True, default=None, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "client",
                "verbose_name_plural": "clients",
            },
        ),
        migrations.CreateModel(
            name="Token",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("ia", "Initial access token"),
                            ("at", "Access token"),
                            ("rt", "Refresh token"),
                            ("ac", "Authorization code"),
                        ],
                        max_length=2,
                    ),
                ),
                ("hash", models.CharField(max_length=255)),
                ("data", models.JSONField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "expires_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("scopes", models.TextField(default="")),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="allauth_idp_oidc.client",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("type", "hash")},
            },
        ),
    ]

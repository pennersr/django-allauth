from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("allauth_idp_oidc", "0002_client_default_scopes"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="allow_uri_wildcards",
            field=models.BooleanField(
                default=False,
                help_text="Allow wildcards (*) in redirect URIs and CORS origins. When enabled, URIs can contain a single asterisk to match subdomains.",
                verbose_name="Allow URI wildcards",
            ),
        ),
    ]

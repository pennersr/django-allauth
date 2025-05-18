from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("allauth_idp_oidc", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="default_scopes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="In case the client does not specify any scope, these default scopes are used. Provide one value per line, e.g.: openid(ENTER)profile(ENTER)email(ENTER)",
            ),
        ),
    ]

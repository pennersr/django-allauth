from django.conf import settings
from django.db import migrations, models


EMAIL_MAX_LENGTH = getattr(settings, "ACCOUNT_EMAIL_MAX_LENGTH", 254)


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0003_alter_emailaddress_create_unique_verified_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailaddress",
            name="email",
            field=models.EmailField(
                max_length=EMAIL_MAX_LENGTH, verbose_name="email address"
            ),
        ),
    ]

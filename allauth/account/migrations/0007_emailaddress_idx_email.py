from django.conf import settings
from django.db import migrations, models


EMAIL_MAX_LENGTH = getattr(settings, "ACCOUNT_EMAIL_MAX_LENGTH", 254)


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0006_emailaddress_lower"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="emailaddress",
            name="account_emailaddress_upper",
        ),
        migrations.AlterField(
            model_name="emailaddress",
            name="email",
            field=models.EmailField(
                db_index=True, max_length=EMAIL_MAX_LENGTH, verbose_name="email address"
            ),
        ),
    ]

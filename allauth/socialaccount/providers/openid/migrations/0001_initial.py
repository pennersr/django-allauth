from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OpenIDNonce",
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
                ("server_url", models.CharField(max_length=255)),
                ("timestamp", models.IntegerField()),
                ("salt", models.CharField(max_length=255)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="OpenIDStore",
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
                ("server_url", models.CharField(max_length=255)),
                ("handle", models.CharField(max_length=255)),
                ("secret", models.TextField()),
                ("issued", models.IntegerField()),
                ("lifetime", models.IntegerField()),
                ("assoc_type", models.TextField()),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]

# Generated by Django 4.1.6 on 2023-02-08 22:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_collections", "0002_collection_chunks"),
    ]

    operations = [
        migrations.CreateModel(
            name="Planets",
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
                ("url", models.CharField(max_length=255)),
                ("verbose_name", models.CharField(max_length=255)),
            ],
        ),
    ]

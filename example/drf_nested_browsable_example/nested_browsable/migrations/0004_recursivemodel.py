# Generated by Django 5.0.2 on 2024-04-29 07:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nested_browsable", "0003_otherinnermodel"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecursiveModel",
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
                ("key", models.CharField(max_length=50)),
                ("value", models.CharField(max_length=50)),
                (
                    "parent",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="nested_browsable.recursivemodel",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

# Generated by Django 5.0.1 on 2025-07-15 09:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0006_fileversion_content_hash"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="fileversion",
            unique_together={("file_obj", "version_number")},
        ),
    ]

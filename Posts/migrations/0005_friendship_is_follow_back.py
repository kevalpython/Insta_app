# Generated by Django 5.0.6 on 2024-07-22 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0004_postimagevideo_file_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendship',
            name='is_follow_back',
            field=models.BooleanField(default=False),
        ),
    ]
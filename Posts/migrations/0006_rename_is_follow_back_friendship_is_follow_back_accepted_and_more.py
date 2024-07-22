# Generated by Django 5.0.6 on 2024-07-22 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0005_friendship_is_follow_back'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendship',
            old_name='is_follow_back',
            new_name='is_follow_back_accepted',
        ),
        migrations.AddField(
            model_name='friendship',
            name='is_follow_back_requested',
            field=models.BooleanField(default=False),
        ),
    ]
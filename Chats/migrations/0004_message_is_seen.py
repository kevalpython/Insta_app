# Generated by Django 5.0.6 on 2024-07-17 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chats', '0003_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.0.6 on 2024-07-19 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0003_alter_like_post_alter_postimagevideo_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='postimagevideo',
            name='file_type',
            field=models.TextField(blank=True, null=True),
        ),
    ]

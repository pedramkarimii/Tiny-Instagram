# Generated by Django 5.0.3 on 2024-03-15 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_follow',
            field=models.BooleanField(default=False),
        ),
    ]

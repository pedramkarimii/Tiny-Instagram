# Generated by Django 5.0.3 on 2024-03-16 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_post_dislikes_post_likes_alter_comment_post'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='comment',
            name='owner_post_unique',
        ),
    ]

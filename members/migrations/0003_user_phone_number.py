# Generated by Django 5.0 on 2024-01-10 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_broadcast_email_user_password_confirmation'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.IntegerField(default=1, max_length=10, unique=True),
            preserve_default=False,
        ),
    ]
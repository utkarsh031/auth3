# Generated by Django 5.0 on 2024-01-11 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=10),
        ),
    ]
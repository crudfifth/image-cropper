# Generated by Django 4.2.5 on 2023-09-26 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_user_co2_unit_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hashed_pushlog_api_key',
            field=models.CharField(max_length=512, null=True, unique=True),
        ),
    ]

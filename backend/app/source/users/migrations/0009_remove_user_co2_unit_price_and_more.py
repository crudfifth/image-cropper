# Generated by Django 4.2.5 on 2023-09-22 05:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_company_admin_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='co2_unit_price',
        ),
        migrations.RemoveField(
            model_name='user',
            name='electric_unit_co2',
        ),
        migrations.RemoveField(
            model_name='user',
            name='electric_unit_price',
        ),
        migrations.RemoveField(
            model_name='user',
            name='fuel_unit_co2',
        ),
        migrations.RemoveField(
            model_name='user',
            name='fuel_unit_price',
        ),
        migrations.RemoveField(
            model_name='user',
            name='water_unit_price',
        ),
    ]

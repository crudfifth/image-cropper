# Generated by Django 4.2.11 on 2024-03-14 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ihiapp', '0080_remove_channeladapter_entity_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='input_source',
            field=models.IntegerField(choices=[(1, 'DEVICE'), (2, 'MANUAL'), (3, 'CSV')], default=1, verbose_name='入力元'),
        ),
    ]

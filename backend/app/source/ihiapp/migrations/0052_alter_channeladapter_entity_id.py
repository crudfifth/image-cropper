# Generated by Django 4.2.9 on 2024-01-15 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ihiapp', '0051_channelgateway_channelbasicunit_channeladapter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channeladapter',
            name='entity_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ihiapp.entity', verbose_name='CHエンティティ'),
        ),
    ]

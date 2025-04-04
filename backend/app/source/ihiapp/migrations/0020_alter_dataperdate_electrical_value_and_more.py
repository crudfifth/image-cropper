# Generated by Django 4.2.5 on 2023-10-05 02:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ihiapp', '0019_remove_economicactivityunit_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataperdate',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='dataperdate',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='dataperdate',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='dataperhour',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='dataperhour',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='dataperhour',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='datapermonth',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='datapermonth',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='datapermonth',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='dataperyear',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='dataperyear',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='dataperyear',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedataperdate',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='devicedataperdate',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedataperdate',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedataperhour',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='devicedataperhour',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedataperhour',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedatapermonth',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='devicedatapermonth',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedatapermonth',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedataperyear',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='devicedataperyear',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='devicedataperyear',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='deviceunitprice',
            name='co2_unit_price',
            field=models.FloatField(default=0, verbose_name='CO2(円/t-CO2)'),
        ),
        migrations.AlterField(
            model_name='deviceunitprice',
            name='electric_unit_price',
            field=models.FloatField(default=0, verbose_name='電気(円/kWh)'),
        ),
        migrations.AlterField(
            model_name='deviceunitprice',
            name='fuel_unit_price',
            field=models.FloatField(default=0, verbose_name='燃料(円/m3)'),
        ),
        migrations.AlterField(
            model_name='deviceunitprice',
            name='water_unit_price',
            field=models.FloatField(default=0, verbose_name='水(円/m3)'),
        ),
        migrations.AlterField(
            model_name='jcreditapplication',
            name='electrical_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='電気/取得値(kW)'),
        ),
        migrations.AlterField(
            model_name='jcreditapplication',
            name='fuel_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='燃料/取得値(L)'),
        ),
        migrations.AlterField(
            model_name='jcreditapplication',
            name='water_value',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='水/取得値(L)'),
        ),
    ]

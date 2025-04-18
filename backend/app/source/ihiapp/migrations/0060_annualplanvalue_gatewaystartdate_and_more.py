# Generated by Django 4.2.10 on 2024-02-08 02:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_user_is_agreed_to_terms_of_service'),
        ('ihiapp', '0059_dataperminute_channeldataperminute'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnualPlanValue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('utility_cost', models.IntegerField(default=0, verbose_name='光熱費')),
                ('electric', models.IntegerField(default=0, verbose_name='電力量')),
                ('electric_reduce', models.IntegerField(default=0, verbose_name='電力削減量')),
                ('co2_emissions', models.IntegerField(default=0, verbose_name='CO2排出量')),
                ('co2_emissions_reduce', models.IntegerField(default=0, verbose_name='CO2削減量')),
                ('carbon_credit', models.IntegerField(default=0, verbose_name='カーボンクレジット量')),
                ('carbon_credit_price', models.IntegerField(default=0, verbose_name='カーボンクレジット価格')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='企業')),
            ],
            options={
                'verbose_name': '年間計画値の設定',
                'verbose_name_plural': '年間計画値の設定',
            },
        ),
        migrations.CreateModel(
            name='GatewayStartdate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('started_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='利用開始日')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='企業')),
                ('gateway_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ihiapp.gateway', verbose_name='ゲートウェイ')),
            ],
            options={
                'verbose_name': 'Gatewayへの利用開始日の設定',
                'verbose_name_plural': 'Gatewayへの利用開始日の設定',
            },
        ),
        migrations.RemoveField(
            model_name='channelgateway',
            name='company_id',
        ),
        migrations.RemoveField(
            model_name='channelgateway',
            name='gateway_id',
        ),
        migrations.DeleteModel(
            name='ChannelBasicUnit',
        ),
        migrations.DeleteModel(
            name='ChannelGateway',
        ),
    ]

# Generated by Django 4.2.10 on 2024-02-13 11:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_user_is_agreed_to_terms_of_service'),
        ('ihiapp', '0065_alter_annualplanvalues_company_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='GatewayMaster',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('gateway_type', models.CharField(max_length=30, verbose_name='ゲートウェイ種別')),
                ('license_type', models.CharField(max_length=30, verbose_name='ライセンス種別')),
                ('license_limit', models.DateField(verbose_name='利用可能期限')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('gateway_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ihiapp.gateway', verbose_name='ゲートウェイ')),
            ],
            options={
                'verbose_name': 'ゲートウェイマスタ',
                'verbose_name_plural': 'ゲートウェイマスタ',
            },
        ),
        migrations.CreateModel(
            name='RegisteredLimit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_limit', models.IntegerField(default=0, verbose_name='ユーザー登録上限数')),
                ('gateway_limit', models.IntegerField(default=0, verbose_name='ゲートウェイ登録上限数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('company_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='企業')),
            ],
            options={
                'verbose_name': '登録数上限一覧',
                'verbose_name_plural': '登録上限数一覧',
            },
        ),
        migrations.CreateModel(
            name='GatewayRegistration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='企業')),
                ('gateway_master', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ihiapp.gatewaymaster', verbose_name='ゲートウェイ')),
            ],
            options={
                'verbose_name': 'ゲートウェイ一覧',
                'verbose_name_plural': 'ゲートウェイ一覧',
            },
        ),
    ]

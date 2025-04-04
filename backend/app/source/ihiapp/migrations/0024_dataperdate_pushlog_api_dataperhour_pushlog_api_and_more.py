# Generated by Django 4.2.6 on 2023-11-02 04:27

import hashlib

import django.db.models.deletion
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.paginator import Paginator
from django.db import migrations, models, transaction
from django.db.models import F


def do_create_and_set_pushlog_api(apps, target_model):
    User = apps.get_model("users", "User")
    PushlogApi = apps.get_model("ihiapp", "PushlogApi")

    # ユーザーとハッシュ済みキーの辞書を作成
    user_dict = {
        user.pk: user for user in User.objects.filter(pushlog_api_key__isnull=False)
    }

    # 既存のPushlogApiのキャッシュを作成
    existing_pushlog_api_dict = {
        api.hashed_key: api for api in PushlogApi.objects.all()
    }

    # 新規に作成するPushlogApiのリスト
    pushlog_apis_to_create = []

    # Paginator を使って target_model のクエリセットをページ分割
    queryset = target_model.objects.all().order_by('pk')
    paginator = Paginator(queryset, 1000)  # ページあたり1000件

    for page_number in paginator.page_range:
        with transaction.atomic():
            page = paginator.page(page_number)
            for target_object in page.object_list:
                user = user_dict.get(target_object.user_id.pk)
                if user:
                    pepper = settings.ENCRYPTION_KEY
                    hashed_key = hashlib.sha256((user.pushlog_api_key + pepper).encode()).hexdigest()

                    pushlog_api = existing_pushlog_api_dict.get(hashed_key)

                    # PushlogApiがまだ存在しない場合は新規作成
                    if not pushlog_api:
                        pushlog_api = PushlogApi(
                            key=Fernet(settings.ENCRYPTION_KEY).encrypt(user.pushlog_api_key.encode()).decode(),
                            company=user.company_id,
                            hashed_key=hashed_key,
                        )
                        pushlog_apis_to_create.append(pushlog_api)
                        existing_pushlog_api_dict[hashed_key] = pushlog_api

                    target_object.pushlog_api_id = pushlog_api.id
            # 新規PushlogApiを一括作成
            PushlogApi.objects.bulk_create(pushlog_apis_to_create)

            # target_model の変更を一括更新
            target_model_ids = [obj.pk for obj in page.object_list]
            target_model.objects.filter(pk__in=target_model_ids).update(pushlog_api_id=F('pushlog_api_id'))

            # 作成と更新リストをクリア
            pushlog_apis_to_create.clear()

def create_and_set_pushlog_api(apps, schema_editor):
    models = [
        apps.get_model("ihiapp", "dataperhour"),
        apps.get_model("ihiapp", "dataperdate"),
        apps.get_model("ihiapp", "datapermonth"),
        apps.get_model("ihiapp", "dataperyear"),
        apps.get_model("ihiapp", "devicedataperhour"),
        apps.get_model("ihiapp", "devicedataperdate"),
        apps.get_model("ihiapp", "devicedatapermonth"),
        apps.get_model("ihiapp", "devicedataperyear"),
    ]
    for model in models:
        do_create_and_set_pushlog_api(apps, model)


class Migration(migrations.Migration):
    dependencies = [
        ("ihiapp", "0023_alter_pushlogapi_options_gateway_pushlog_api"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataperdate",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="dataperhour",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="datapermonth",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="dataperyear",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="devicedataperdate",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="devicedataperhour",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="devicedatapermonth",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="devicedataperyear",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        migrations.AddField(
            model_name="jcreditapplication",
            name="pushlog_api",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ihiapp.pushlogapi",
                verbose_name="PUSHLOG API ID",
            ),
        ),
        # migrations.RunPython(
        #     create_and_set_pushlog_api, reverse_code=migrations.RunPython.noop
        # ),
    ]

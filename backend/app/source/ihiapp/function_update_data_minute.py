import concurrent.futures
import datetime
import logging
import uuid
from threading import Thread

import requests
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .constants import (DATA_TYPE_ELECTRICITY, DATA_TYPE_FUEL, DATA_TYPE_WATER,
                        ENV_TYPE_ELECTRICITY, ENV_TYPE_FUEL, ENV_TYPE_WATER)
from .models import Data, DataType, Device, Gateway, PushLogApi

PUSH_LOG_URL = "https://api.pushlog.jp/v3/gateways"



# Dataへの「分」ごとのデータ書き込み
# 　Noneデータの書き込みを許す
# 　normalで取得できなかった場合にNoneにする
def save_device_data_minute(value, target_device, pushlog_api_id: uuid.UUID, response_data_captured_at):
    # year = response_data_captured_at.year
    # month = response_data_captured_at.month
    # date = response_data_captured_at.day
    # hour = response_data_captured_at.hour
    # minute = response_data_captured_at.minute
    entity = target_device.entity

    filter = {
        'date_type': Data.DateType.MINUTE,
        'entity': entity,
        # 'get_data_at__year': year,
        # 'get_data_at__month': month,
        # 'get_data_at__day': date,
        # 'get_data_at__hour': hour,
        # 'get_data_at__minute': minute,
        'get_data_at': response_data_captured_at,
    }
    try:
        if Data.objects.filter(**filter).exists():
            logging.info(f'すでにデータが存在します: {filter}')
        elif target_device.unit_id is None:
            logging.info(f"単位が設定されていない機器です device: {target_device}")
        elif target_device.entity is None:
            logging.info(f"Entityが設定されていない機器です device: {target_device}")
        elif target_device.unit_id.environmental_type_id.name == ENV_TYPE_ELECTRICITY:
            # 電力の場合
            try:
                data_type = DataType.objects.filter(name=DATA_TYPE_ELECTRICITY).first()
                if data_type is None:
                    raise Exception('data_type=電気が未作成です')
                Data.save_data_minute(
                    date_type = Data.DateType.MINUTE,
                    device = target_device,
                    value = float(value),
                    data_type = data_type,
                    entity = entity,
                    # get_data_at = datetime.datetime(year, month, date, hour, minute)
                    get_data_at = response_data_captured_at
                )
                logging.info(f'Data（分）を新規作成しました (電力): {value} A, entity: {entity}, captured_at {response_data_captured_at}')
            except Exception as e:
                logging.warn(f"電力のデータが不正です: {value} {target_device.unit_id.name}, {target_device} {e}")

    except Exception as e:
        logging.error(f'Dataの新規作成に失敗しました: {e}')


# デバイスごとのデータを登録する
def create_timeseries_data_by_normal(header, pushlog_api_id: uuid.UUID, gateway_id: str):
    # 事前にstatusでGatewayがconnectかどうかを確認する
    url = PUSH_LOG_URL + f"/{gateway_id}/status"
    try:
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            logging.error(f'{url} データの取得に失敗しました: {response}')
            return
    except Exception as e:
        logging.error(f'{url} データの取得に失敗しました: {e}')
        return
    # json形式データを取得
    response_data = response.json()
    # 接続してない場合はlog出力して処理を終える
    try:
        connected = response_data['connected']
        if connected == False:
            logging.info(f"Gatewayが接続されていません gateway: {gateway_id}")
            return
    except:
        logging.info(f"要求されたGatewayのデータが空です gateway: {gateway_id}")
        return

    # normalデータ用のURL
    url = PUSH_LOG_URL + f"/{gateway_id}/realtime/normal"

    # データを取得
    try:
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            # エラーである
            logging.error(f'{url} データの取得に失敗しました: {response}')
            return
    except Exception as e:
        logging.error(f'{url} データの取得に失敗しました: {e}')
        return

    # json形式データを取得
    response_data = response.json()
    # response_dataが空の場合は、エラーとする
    if len(response_data) == 0:
        logging.info(f"要求されたGatewayのデータが空です gateway: {gateway_id}")
        return

    for trigger_data in response_data:
        # 収集時刻を取得して、秒以下を丸める
        captured_at = datetime.datetime.strptime(trigger_data['capturedAt'], '%Y-%m-%dT%H:%M:%S%z')
        #captured_at = captured_at.replace(second=0, microsecond=0, tzinfo=None)

        # 取得したデータからデバイスごとのデータを取り出す
        for device_data in trigger_data['capturedData']:
            # Deviceを取得
            if Device.objects.filter(gateway_id=gateway_id,device_number=device_data['deviceId']).exists():
                target_device = Device.objects.filter(gateway_id=gateway_id,device_number=device_data['deviceId']).first()
                if target_device is None:
                    continue
                if target_device.entity is None:
                    # Channel登録されていない機器になるので、無視する
                    # logging.info(f"Entityが設定されていない機器です device: {target_device}, データ取得対象名：{target_device.data_source_name}")
                    continue
                if target_device.enable_data_collection == False:
                    # エラーではない
                    logging.info(f"データ収集が無効な機器です device: {target_device}")
                    continue
                if target_device.unit_id is None:
                    logging.info(f"単位が設定されていない機器です device: {target_device}, データ取得対象名：{target_device.data_source_name}")
                    continue

                # デバイスごとのデータを取得する：瞬時値
                try:
                    value = float(device_data['value'])
                except:
                    # 値が不正値（float/intでない）の場合は、無視する
                    continue

                # 保存する
                logging.info(f'start save_device_data: {target_device}')
                # save_device_data(value=diff_value, target_device=target_device, pushlog_api_id=pushlog_api_id, response_data_captured_at=target_time_0)
                save_device_data_minute(value=value, target_device=target_device, pushlog_api_id=pushlog_api_id, response_data_captured_at=captured_at)

def update_pushlog_api_data_minute(pushlog_api: PushLogApi):
    if pushlog_api.key is None:
        return
    header = {
        "X-Pushlog-API-Key" : pushlog_api.key,
    }

    # gatewayデータを取得
    gateways = Gateway.objects.filter(pushlog_api_id=pushlog_api.id)
    gateway_id_list = [gw.id for gw in gateways]

    # 時系列データの作成
    for gateway_id in gateway_id_list:
        logging.info(f'start create_timeseries_data: {gateway_id}')
        create_timeseries_data_by_normal(header, pushlog_api.id, gateway_id)

# cron.pyから呼ばれる
# pushlog_apiごと（pushlog_api_keyごと）の処理
def update_push_log_minute(pushlog_api_id=None):
    # Tableがない(migrateがまだの)状態では、Exceptionで落ちて、
    # appコンテナ自体が立ち上がらなくなるので、それを回避するための処理
    try:
        if pushlog_api_id is not None:
            # 指定されたPushlogAPIのみを対象とする
            target_pushlog_apis = PushLogApi.objects.filter(id=pushlog_api_id)
        else:
            target_pushlog_apis = PushLogApi.objects.all()
        # target_pushlog_apis = target_pushlog_apis.filter(company__batch_enabled=True)

        _ = target_pushlog_apis.exists()
    except:
        logging.info("PushLogApiが存在しません")
        return

    # pushlog_api_key単位での並列処理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for pushlog_api in target_pushlog_apis:
            futures.append(
                executor.submit(
                    update_pushlog_api_data_minute,
                    pushlog_api=pushlog_api,
                )
            )
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(e)


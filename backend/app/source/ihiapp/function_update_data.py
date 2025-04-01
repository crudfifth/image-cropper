import concurrent.futures
import datetime
import logging
import pytz
import queue
import random
import threading
import time
import re
import uuid
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from itertools import islice
from threading import Thread
from typing import List, Dict, Any

from .constants import (DATA_TYPE_ELECTRICITY, ENV_TYPE_ELECTRICITY)
from .models import (Data, DataStructure, DataType, Device, Entity, EnvironmentalType,
                     Gateway, GatewayMaster, PushLogApi, Unit)
from .function_calls import (email_notification_invalid, 
                             email_notification_data_is_empty,
                             PushlogApiCall)

# 追加と削除のコンフリクトを回避するためのロック
lock_data = threading.Lock()
# 削除するオブジェクトを格納するQueue
delete_q = queue.Queue()    # 減算処理
delete_q2 = queue.Queue()   # オブジェクトの削除

# Dataへの「分」ごとのデータ書き込み
# 　Noneデータの書き込みを許す
# 　normalで取得できなかった場合にNoneにする
def save_device_data_minute(value, target_device, response_data_captured_at):
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
    if Data.objects.filter(**filter).exists():
        logging.info(f'すでにデータが存在します: {filter}')
        return
    elif target_device.entity is None:
        logging.info(f"Entityが設定されていない機器です device: {target_device}")
        return

    try:
        # 単位が設定されていない場合、電力「kWh」「Wh」以外の単位
        if (target_device.unit_id is None or target_device.unit_id.environmental_type_id is None or 
            target_device.unit_id.environmental_type_id.name != ENV_TYPE_ELECTRICITY):
            data_type = None
            Data.save_minute_hierarchical_data(
                device = target_device,
                value = value,
                data_type = data_type,
                entity = entity,
                get_data_at = response_data_captured_at
            )
            unit_name = "<Unknown Unit>" if target_device.unit_id is None else target_device.unit_id.name
            logging.info(f'Data（分）を新規作成しました (その他): {value} [{unit_name}], entity: {entity}')


        elif target_device.unit_id.environmental_type_id.name == ENV_TYPE_ELECTRICITY:
            # 電力の場合
            try:
                data_type = DataType.objects.filter(name=DATA_TYPE_ELECTRICITY).first()
                if data_type is None:
                    raise Exception('data_type=電気が未作成です')
                if target_device.unit_id.name == 'W' or target_device.unit_id.name == 'Wh':
                    # 単位：Wh → kWh
                    electrical_value = None if value is None else float(value)*0.001
                    Data.save_minute_hierarchical_data(
                        device = target_device,
                        value = electrical_value,
                        data_type = data_type,
                        entity = entity,
                        # get_data_at = datetime.datetime(year, month, date, hour, minute)
                        get_data_at = response_data_captured_at
                    )
                    logging.info(f'Data（分）を新規作成しました (電力): {electrical_value} [kWh], entity: {entity}, captured_at {response_data_captured_at}')
                elif target_device.unit_id.name == 'kW' or target_device.unit_id.name == 'kWh':
                    # 単位： kWh まま
                    electrical_value = None if value is None else float(value)
                    Data.save_minute_hierarchical_data(
                        device = target_device,
                        value = electrical_value,
                        data_type = data_type,
                        entity = entity,
                        # get_data_at = datetime.datetime(year, month, date, hour, minute)
                        get_data_at = response_data_captured_at
                    )
                    logging.info(f'Dataを新規作成しました (電力): {electrical_value} [kWh], entity: {entity}, captured_at {response_data_captured_at}')
                else:
                    logging.info(f"電力の単位が不正な機器です device: {target_device.unit_id.name}, {target_device}")

            except Exception as e:
                gateway_id = target_device.gateway_id_id
                pushlog_api = target_device.pushlog_api
                email_notification_invalid(pushlog_api=pushlog_api, gateway_id=gateway_id, device_name=target_device.name, data_source_name=target_device.data_source_name, additional_msg=f'{e}')
                logging.warn(f"電力のデータが不正です: {value} {target_device.unit_id.name}, {target_device} {e}")

    except Exception as e:
        logging.error(f'Data（分）の新規作成に失敗しました: {e}')

# Dataへの時間ごとのデータ書き込み
# 　Noneデータの書き込みを許す
# 　historicalデータで、from、toの一方もしくは両方が取得できなかった場合にNoneにする
def save_device_data(value, target_device, response_data_captured_at):
    year = response_data_captured_at.year
    month = response_data_captured_at.month
    date = response_data_captured_at.day
    hour = response_data_captured_at.hour
    minute = response_data_captured_at.minute
    entity = target_device.entity
    filter = {
        'date_type': Data.DateType.HOUR,
        'entity': entity,
        'get_data_at__year': year,
        'get_data_at__month': month,
        'get_data_at__day': date,
        'get_data_at__hour': hour,
        'get_data_at__minute': minute,
    }
    if Data.objects.filter(**filter).exists():
        logging.info(f'すでにデータが存在します: {filter}')
        return
    elif target_device.entity is None:
        logging.info(f"Entityが設定されていない機器です device: {target_device}")
        return

    try:
        # 単位が設定されていない場合、電力「kWh」「Wh」以外の単位
        if (target_device.unit_id is None or target_device.unit_id.environmental_type_id is None or 
            target_device.unit_id.environmental_type_id.name != ENV_TYPE_ELECTRICITY):
            data_type = None
            Data.save_all_hierarchical_data(
                device = target_device,
                value = value,
                data_type = data_type,
                entity = entity,
                get_data_at = datetime.datetime(year, month, date, hour, minute)
            )
            unit_name = "<Unknown Unit>" if target_device.unit_id is None else target_device.unit_id.name
            logging.info(f'Dataを新規作成しました (その他): {value} [{unit_name}], entity: {entity}')

        elif target_device.unit_id.environmental_type_id.name == ENV_TYPE_ELECTRICITY:
            # 電力の場合
            try:
                data_type = DataType.objects.filter(name=DATA_TYPE_ELECTRICITY).first()
                if data_type is None:
                    raise Exception('data_type=電気が未作成です')
                if target_device.unit_id.name == 'W' or target_device.unit_id.name == 'Wh':
                    # 単位：Wh → kWh
                    electrical_value = None if value is None else float(value)*0.001
                    Data.save_all_hierarchical_data(
                        device = target_device,
                        value = electrical_value,
                        data_type = data_type,
                        entity = entity,
                        get_data_at = datetime.datetime(year, month, date, hour, minute)
                    )
                    logging.info(f'Dataを新規作成しました (電力): {electrical_value} [kWh], entity: {entity}')
                elif target_device.unit_id.name == 'kW' or target_device.unit_id.name == 'kWh':
                    # 単位： kWh まま
                    electrical_value = None if value is None else float(value)
                    Data.save_all_hierarchical_data(
                        device = target_device,
                        value = electrical_value,
                        data_type = data_type,
                        entity = entity,
                        get_data_at = datetime.datetime(year, month, date, hour, minute)
                    )
                    logging.info(f'Dataを新規作成しました (電力): {electrical_value} [kWh], entity: {entity}')
                else:
                    logging.info(f"電力の単位が不正な機器です device: {target_device.unit_id.name}, {target_device}")
            except Exception as e:
                gateway_id = target_device.gateway_id_id
                pushlog_api = target_device.pushlog_api
                email_notification_invalid(pushlog_api=pushlog_api, gateway_id=gateway_id, device_name=target_device.name, data_source_name=target_device.data_source_name, additional_msg=f'{e}')
                logging.warn(f"電力のデータが不正です: {value} {target_device.unit_id.name}, {target_device} {e}")

        # elif target_device.unit_id.environmental_type_id.name == ENV_TYPE_WATER:
        #     # 水の場合
        #     try:
        #         data_type = DataType.objects.filter(name=DATA_TYPE_WATER).first()
        #         if data_type is None:
        #             raise Exception('data_type=水が未作成です')
        #         if target_device.unit_id.name == 'L':
        #             # 単位： L -> m3
        #             water_value = None if value is None else float(value)*0.001
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = water_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (水): {water_value} m3, entity: {entity}')
        #         elif target_device.unit_id.name == 'm3':
        #             # 単位： m3 まま
        #             water_value = None if value is None else float(value)
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = water_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (水): {water_value} m3, entity: {entity}')
        #         elif target_device.unit_id.name == 'kg':
        #             # 単位： kg -> m3
        #             water_value = None if value is None else float(value)*0.001
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = water_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (水): {water_value} m3, entity: {entity}')
        #         elif target_device.unit_id.name == 'ton':
        #             # 単位： ton -> m3
        #             water_value = None if value is None else float(value)
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = water_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (水): {water_value} m3, entity: {entity}')
        #         else:
        #             logging.info(f"水の単位が不正な機器です device: {target_device.unit_id.name}, {target_device}")
        #     except Exception as e:
        #         pushlog_api = PushLogApi.objects.get(id=pushlog_api_id)
        #         gateway_id = target_device.gateway_id_id
        #         email_notification_invalid(pushlog_api=pushlog_api, gateway_id=gateway_id, device_name=target_device.name, data_source_name=target_device.data_source_name, additional_msg=f'{e}')
        #         logging.warn(f"水のデータが不正です: {value}, {target_device}, {e}")

        # elif target_device.unit_id.environmental_type_id.name == ENV_TYPE_FUEL:
        #     # 燃料の場合
        #     try:
        #         data_type = DataType.objects.filter(name=DATA_TYPE_FUEL).first()
        #         if data_type is None:
        #             raise Exception('data_type=燃料が未作成です')

        #         rho = target_device.specific_gravity        # 燃料の比重ρ
        #         if rho is None:
        #             # エラーである
        #             pushlog_api = PushLogApi.objects.get(id=pushlog_api_id)
        #             gateway_id = target_device.gateway_id_id
        #             email_notification_rho_not_set(pushlog_api=pushlog_api, gateway_id=gateway_id, device_name=target_device.name, data_source_name=target_device.data_source_name)
        #             logging.warn(f'specific_gravity（比重）が未設定です: {value} {target_device.unit_id.name},  {target_device}, entity: {entity}')
        #             return

        #         if target_device.unit_id.name == "L":
        #             # 単位： L -> m3
        #             fuel_value = None if value is None else float(value)*0.001
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = fuel_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (燃料): {fuel_value} m3, entity: {entity}')
        #         elif target_device.unit_id.name == "m3":
        #             # 単位： m3 まま
        #             fuel_value = None if value is None else float(value)
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = fuel_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (燃料): {fuel_value} m3, entity: {entity}')
        #         elif target_device.unit_id.name == "kg":
        #             # 単位： kg -> m3
        #             fuel_value = None if value is None else float(value)/float(rho)*0.001
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = fuel_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (燃料): {fuel_value} m3, entity: {entity}')
        #         elif target_device.unit_id.name == "ton":
        #             # 単位： ton -> m3
        #             fuel_value = None if value is None else float(value)/float(rho)
        #             Data.save_all_hierarchical_data(
        #                 device = target_device,
        #                 date_type = Data.DateType.HOUR,
        #                 value = fuel_value,
        #                 data_type = data_type,
        #                 entity = entity,
        #                 get_data_at = datetime.datetime(year, month, date, hour, minute)
        #             )
        #             logging.info(f'Dataを新規作成しました (燃料): {fuel_value} m3, entity: {entity}')
        #         else:
        #             logging.info(f"燃料の単位が不正な機器です device: {target_device.unit_id.name}, {target_device}")
        #     except Exception as e:
        #         pushlog_api = PushLogApi.objects.get(id=pushlog_api_id)
        #         gateway_id = target_device.gateway_id_id
        #         email_notification_invalid(pushlog_api=pushlog_api, gateway_id=gateway_id, device_name=target_device.name, data_source_name=target_device.data_source_name, additional_msg=f'{e}')
        #         logging.warn(f"燃料のデータが不正です: {value} {target_device.unit_id.name}, {target_device}, {e}")

    except Exception as e:
        logging.error(f'Dataの新規作成に失敗しました: {e}')


def create_demo_timeseries_data():
    # demo_devices = Device.objects.filter(pushlog_api__company__admin_user_id__is_demo=True)
    demo_devices = Device.objects.filter(entity__company__admin_user_id__is_demo=True)
    for demo_device in demo_devices:
        logging.info(f'start save demo device data : {demo_device}')

        now = datetime.datetime.now()
        interval = INTERVAL_MINUTES
        to_target_time = round_time_to_prev_min(now, interval)

        value = random.randint(1000, 10000) # デモデバイスには乱数のデータを保存
        if demo_device.pushlog_api is not None:
            save_device_data(value=value, target_device=demo_device, response_data_captured_at=to_target_time)


# デバイスごとのデータを登録する：瞬時値
def create_instantaneous_timeseries_data(target_device:Device, historical_values:List[Dict[str, Any]],
                                         target_time_0, target_time_1, target_time_2, target_time_3):
    # デバイスごとのデータを計算する：瞬時値
    # 積算値では、今回の値と前回の値との差分を計算する
    # 欠損値は10分以内の間隔がある場合は前後の値の平均で補完する
    target_time3_dash = target_time_3 - datetime.timedelta(minutes=BUFFER_MINUTES + 1)
    range_data = []
    for historical_value in historical_values:
        try:
            # 値を取得
            value = float(historical_value['value'])

            # 収集時刻を取得して、秒以下を丸める
            captured_at_second = datetime.datetime.strptime(historical_value['date'], '%Y-%m-%dT%H:%M:%S%z')
            captured_at = captured_at_second.replace(second=0, microsecond=0, tzinfo=None)

            if target_time3_dash < captured_at <= target_time_0:
                # 必要な範囲のデータ
                range_data.append( {'captured_at':captured_at, 'captured_at_second':captured_at_second, 'value':value} )                
        except Exception as e:
            # 値が不正値（float/intでない）の場合、エラーメッセージを出力して終了
            value = historical_value['value']
            gateway_id = target_device.gateway_id_id
            pushlog_api = target_device.pushlog_api
            email_notification_invalid(pushlog_api=pushlog_api, gateway_id=gateway_id, device_name=target_device.name, data_source_name=target_device.data_source_name, additional_msg=f'{e}')
            logging.warn(f"データが不正です: {value} {target_device.unit_id.name}, {target_device} {e}")
            return

    # 値が何も入っていない＝登録データがない → 終了
    if len(range_data) == 0:
        return

    # 昇順にソート
    range_data = sorted(range_data, key=lambda x:x['captured_at_second'])

    # 欠損値を補完
    filled_data = fill_missing_values(range_data)

    # 同じ年月日時分のデータを合算
    filled_data = aggregate_same_minute_data(filled_data)

    # target_time_1より大きい値を取得：合算を求めるのでtarget_time_1の値を含めない
    filled_data_target_0 = [datum for datum in filled_data if datum['captured_at'] > target_time_1]
    # 登録の失敗が多いため、2インターバル前まで過去データ登録を行う(すでにデータが存在すれば保存処理は行われない)
    filled_data_target_1 = [datum for datum in filled_data if target_time_2 < datum['captured_at'] <= target_time_1]
    filled_data_target_2 = [datum for datum in filled_data if target_time_3 < datum['captured_at'] <= target_time_2]
 
    if len(filled_data) == 0:
        return

    # 30分データを計算
    value30_target_0 = sum([datum['value'] for datum in filled_data_target_0])
    value30_target_1 = sum([datum['value'] for datum in filled_data_target_1])
    value30_target_2 = sum([datum['value'] for datum in filled_data_target_2])

    # 1分ごとデータを計算
    minute_data_list = [datum for datum in filled_data if datum['captured_at'] > target_time_3 and datum['captured_at'] <= target_time_0]

    # データ保存
    logging.info(f'start save_device_data: {target_device}, {value30_target_0}, {target_time_0}')
    # 30分データを保存する
    if len(filled_data_target_0) > 0:
        save_device_data(value=value30_target_0, target_device=target_device, response_data_captured_at=target_time_0)
    if len(filled_data_target_1) > 0:
        save_device_data(value=value30_target_1, target_device=target_device, response_data_captured_at=target_time_1)
    if len(filled_data_target_2) > 0:
        save_device_data(value=value30_target_2, target_device=target_device, response_data_captured_at=target_time_2)

    # 1分データを保存する
    for minute_data in minute_data_list:
        save_device_data_minute(value=minute_data['value'], 
                                target_device=target_device, 
                                response_data_captured_at=minute_data['captured_at'])                        




# デバイスごとのデータを登録する：積算値
def create_cumulative_timeseries_data(target_device:Device, historical_values:List[Dict[str, Any]],
                                      target_time_0, target_time_1, target_time_2, target_time_3):
    # デバイスごとのデータを計算する：積算値
    # 積算値では、今回の値と前回の値との差分を計算する
    # 欠損値は10分以内の間隔がある場合は前後の値の平均で補完する
    target_time3_dash = target_time_3 - datetime.timedelta(minutes=BUFFER_MINUTES)
    range_data = []
    for historical_value in historical_values:
        try:
            # 値を取得
            value = float(historical_value['value'])

            # 収集時刻を取得して、秒以下を丸める
            captured_at_second = datetime.datetime.strptime(historical_value['date'], '%Y-%m-%dT%H:%M:%S%z')
            captured_at = captured_at_second.replace(second=0, microsecond=0, tzinfo=None)

            if target_time3_dash < captured_at <= target_time_0:
                # 必要な範囲のデータ
                range_data.append( {'captured_at':captured_at, 'captured_at_second':captured_at_second, 'value':value} )                
        except Exception as e:
            # 値が不正値（float/intでない）の場合、エラーメッセージを出力して終了
            value = historical_value['value']
            gateway_id = target_device.gateway_id_id
            pushlog_api = target_device.pushlog_api
            email_notification_invalid(pushlog_api=pushlog_api, gateway_id=gateway_id, device_name=target_device.name, data_source_name=target_device.data_source_name, additional_msg=f'{e}')
            logging.warn(f"データが不正です: {value} {target_device.unit_id.name}, {target_device} {e}")
            return

    # 値が何も入っていない＝登録データがない → 終了
    if len(range_data) == 0:
        return

    # 昇順にソート
    range_data = sorted(range_data, key=lambda x:x['captured_at_second'])

    # 差分データを作成する
    difference_data = make_difference_values(range_data)

    # 欠損値を補完
    filled_data = fill_missing_values(difference_data)

    # 同じ年月日時分のデータを合算
    filled_data = aggregate_same_minute_data(filled_data)

    # target_time_1より大きい値を取得：合算を求めるのでtarget_time_1の値を含めない
    filled_data_target_0 = [datum for datum in filled_data if datum['captured_at'] > target_time_1]
    # 登録の失敗が多いため、90分前までデータ登録を行う(すでにデータが存在すれば保存処理は行われない)
    filled_data_target_1 = [datum for datum in filled_data if target_time_2 < datum['captured_at'] <= target_time_1]
    filled_data_target_2 = [datum for datum in filled_data if target_time_3 < datum['captured_at'] <= target_time_2]
 
    if len(filled_data) == 0:
        return

    # 30分データを計算
    value30_target_0 = sum([datum['value'] for datum in filled_data_target_0])
    value30_target_1 = sum([datum['value'] for datum in filled_data_target_1])
    value30_target_2 = sum([datum['value'] for datum in filled_data_target_2])

    # 1分ごとデータを計算
    minute_data_list = [datum for datum in filled_data if datum['captured_at'] > target_time_3 and datum['captured_at'] <= target_time_0]

    # データ保存
    logging.info(f'start save_device_data: {target_device}, {value30_target_0}, {target_time_0}')
    # 30分データを保存する
    if len(filled_data_target_0) > 0:
        save_device_data(value=value30_target_0, target_device=target_device, response_data_captured_at=target_time_0)
    if len(filled_data_target_1) > 0:
        save_device_data(value=value30_target_1, target_device=target_device, response_data_captured_at=target_time_1)
    if len(filled_data_target_2) > 0:
        save_device_data(value=value30_target_2, target_device=target_device, response_data_captured_at=target_time_2)
    # 1分データを保存する
    for minute_data in minute_data_list:
        save_device_data_minute(value=minute_data['value'], 
                                target_device=target_device, 
                                response_data_captured_at=minute_data['captured_at'])                        

# 積算値を差分データに変換
# その際、欠損値があれば、差分を均等割して補完する
# 逆転値があれば、そこはさらに欠損値とする
def make_difference_values(range_data):
    """
    指定された範囲データの積算値の欠損値を補完する関数。
    
    データが上限を超えた場合＝積算なのに値が逆転した場合は、欠損値扱い
    指定された範囲データ内で、時間差が1分以上10分以下のデータに対して、
    前後のデータを基に線形補間を行い、欠損値を補完する。
    補完された値間の差分データのリストを返す。
    
    Parameters:
    - range_data: 補完対象の範囲データリスト。各データは辞書型で、次の要素を持つ
        - "captured_at"（取得時間）
        - "captured_at_adjust"（補正された取得時間）
        - "value"（値）
        - "captured_at"で昇順にソートされている
    Returns:
    - filled_data: 補完された差分データのリスト。
                    各データは辞書型で、"captured_at"（捕捉時間）と"value"（値）のキーを持つ。
    """
    difference_data = []
    for i in range(len(range_data)):
        current_time = range_data[i]["captured_at"]
        current_value = range_data[i]["value"]

        if i > 0:
            time_diff = (current_time - prev_time).total_seconds() / 60            
            value_diff = current_value - prev_value

            if value_diff >= 0:
                if 1 < time_diff <= 10:
                        value_delta = value_diff / time_diff
                        for j in range(1, int(time_diff)):
                            filled_time = prev_time + datetime.timedelta(minutes=j)
                            filled_value = value_delta
                            difference_data.append({"captured_at": filled_time, "value": filled_value})
                elif time_diff <= 1:
                    difference_data.append({"captured_at": current_time, "value": value_diff})

        prev_time = current_time
        prev_value = current_value
    return difference_data

# 欠損値を補完する
def fill_missing_values(range_data):
    """
    指定された範囲データの値の欠損値を補完する関数。
    
    指定された範囲データ内で、時間差が1分以上10分以下のデータに対して、
    前後のデータを基に線形補間を行い、欠損値を補完する。
    補完後のデータリストを返す。
    
    Parameters:
    - range_data: 補完対象の範囲データリスト。各データは辞書型で、次の要素を持つ
        - "captured_at"（取得時間）
        - "captured_at_adjust"（補正された取得時間）
        - "value"（値）
        - "captured_at"で昇順にソートされている
    Returns:
    - filled_data: 補完後のデータリスト。各データは辞書型で、"captured_at"（捕捉時間）と
                   "value"（値）のキーを持つ。
    """
    filled_data = []
    for i in range(len(range_data)):
        current_time = range_data[i]["captured_at"]
        current_value = range_data[i]["value"]
        
        if i > 0:
            time_diff = (current_time - prev_time).total_seconds() / 60            

            if 1 < time_diff <= 10:
                value_diff = (current_value - prev_value) / time_diff
                for j in range(1, int(time_diff)):
                    filled_time = prev_time + datetime.timedelta(minutes=j)
                    filled_value = prev_value + value_diff * j
                    filled_data.append({"captured_at": filled_time, "value": filled_value})

        filled_data.append({"captured_at": current_time, "value": current_value})
        prev_time = current_time
        prev_value = current_value
    return filled_data

# 同じ年月日時分のデータを加算する関数
def aggregate_same_minute_data(data):
    aggregated_data = {}
    for item in data:
        key = item["captured_at"]
        if key in aggregated_data:
            aggregated_data[key] = aggregated_data[key] + item["value"]
        else:
            aggregated_data[key] = item["value"]
    
    # 辞書をリストに変換
    result = [{"captured_at": captured_at, "value": value} for captured_at, value in aggregated_data.items()]
    return sorted(result, key=lambda x: x["captured_at"])

# UNIXTIMEを計算
def get_unix_time(dt):
    return(int(time.mktime(dt.timetuple())))

# 指定時間を、インターバルでキリの良い時間に繰り下げ
def round_time_to_prev_min(dt, interval):
    minute = dt.minute
    delta = minute - minute // interval * interval
    rounded_dt = dt - datetime.timedelta(minutes=delta)
#    return rounded_dt.replace(second=0, microsecond=0)
    return rounded_dt.replace(second=0, microsecond=0, tzinfo=None)

# 指定時間を、インターバルでキリの良い時間に繰り上げ
def round_time_to_next_min(dt, interval):
    # 分の現在値から次のintervalに繰り上げるための差分を計算
    minute = dt.minute
    delta = interval - (minute % interval)
    if delta == interval:  # 既にキリの良い時間だった場合
        delta = 0

    # deltaを足して次のキリの良い時間に繰り上げる
    rounded_dt = dt + datetime.timedelta(minutes=delta)
    return rounded_dt.replace(second=0, microsecond=0, tzinfo=None)

INTERVAL_MINUTES = 30
BUFFER_MINUTES = 10
# デバイスごとのデータを登録する：積算値/瞬時値
def create_timeseries_data(pushlog_api_id: uuid.UUID, gateway_id: str):
    pushlog_api_call = PushlogApiCall(pushlog_api_id=pushlog_api_id)

    # 事前にstatusでGatewayがconnectかどうかを確認する
    connected  = pushlog_api_call.is_connected(gateway_id=gateway_id)
    # gateway_master.connectedを設定
    gateway_master = GatewayMaster.objects.filter(gateway_id=gateway_id).first()
    if gateway_master is None:
        # Master登録されてなければMaster登録する
        gateway = Gateway.objects.filter(id=gateway_id).first()
        # 検索したGatewayオブジェクトが存在する場合、GatewayMasterにその情報を設定
        if gateway:
            gateway_master = GatewayMaster.objects.create(gateway_id=gateway, gateway_type="PUSHLOG", connected=connected)
        else:
            # Gatewayオブジェクトが見つからない場合は何もせず終了
            return
    else:
        # 登録済みなら、connectedを更新する
        gateway_master.connected = connected
        gateway_master.save()

    # 接続していない場合は、何もしない
    if connected == False:
        return


    # historicalデータの取得
    # 現在時を取得
    now = datetime.datetime.now()
    # 実際に取得する対象時刻＝現在時刻をインターバルで丸める
    interval = INTERVAL_MINUTES                  # 30分間隔

    # before_val in (time_2, time_1], current_val in (time_1, time_0]
    # target_val = current_val - before_val
    target_time_0 = round_time_to_prev_min(now, interval)
    target_time_1 = target_time_0 - datetime.timedelta(minutes=interval)
    target_time_2 = target_time_1 - datetime.timedelta(minutes=interval)
    target_time_3 = target_time_2 - datetime.timedelta(minutes=interval)

    # （対象時刻）データ取得の終了時刻＝直近のインターバルの開始時刻 + 1分
    to_unixtime = get_unix_time(target_time_0 + datetime.timedelta(minutes=1))
    # （対象時刻）データ取得の開始時刻＝直近のインターバルの３つ前のインターバルの開始時刻 - 10分
    from_unixtime = get_unix_time(target_time_3 - datetime.timedelta(minutes=BUFFER_MINUTES))

    # パラメータを設定
    params = {
        'from' : from_unixtime,
        'to' : to_unixtime,
    }
    # 呼び出し
    api_name = 'historical'
    response_data = pushlog_api_call.historical(gateway_id=gateway_id, params=params)
    if response_data == None:
        return

    # 対象gatewayに紐づいたデータ取得対象名一覧が、取得したデータに含まれているかチェック
    chk_data_source_name_list = [str(n) for n in Device.objects.filter(gateway_id=gateway_id, enable_data_collection=True).values_list('data_source_name', flat=True)]
    for trigger_data in response_data:
        for data_source_nm in trigger_data['data'].keys():
            if data_source_nm is not None and data_source_nm in chk_data_source_name_list:
                chk_data_source_name_list.remove(data_source_nm)
    # 含まれていないデバイス名があれば、エラーとする
    for data_source_nm in chk_data_source_name_list:
        if data_source_nm is not None:
            device_name = Device.objects.filter(gateway_id=gateway_id,data_source_name=data_source_nm).first().name
            email_notification_data_is_empty(pushlog_api_id=pushlog_api_id, gateway_id=gateway_id, api_name=api_name, device_name=device_name, data_source_name=data_source_nm)
            logging.info(f"要求されたデバイスのデータが空です デバイス名: {device_name}, データ取得対象名：{data_source_nm}")


    for trigger_data in response_data:
        # 取得したデバイスごとのデータを取り出して、登録する
        for data_source_nm, historical_values in trigger_data['data'].items():
            # Deviceを取得
            if Device.objects.filter(gateway_id=gateway_id,data_source_name=data_source_nm).exists():
                target_device = Device.objects.filter(gateway_id=gateway_id,data_source_name=data_source_nm).first()
                if target_device is not None:

                    if target_device.enable_data_collection == False:
                        # エラーではない
                        logging.info(f"データ収集が無効な機器です device: {target_device}")
                        continue

                    # Entity登録されてないDeviceはないはず。EntityなければData登録できないので、無視する
                    if target_device.entity is None:
                        continue

                    # 単位なしも許すので、unit_id=Noneも許す
                    # if target_device.unit_id is None:
                    #     pass

                    # 瞬時値(True)/積算値(False)のフラグを確認
                    is_instantaneous = target_device.is_instantaneous

                    if is_instantaneous:
                        create_instantaneous_timeseries_data(target_device, historical_values, target_time_0, target_time_1, target_time_2, target_time_3)    # 瞬時値
                    else:
                        create_cumulative_timeseries_data(target_device, historical_values, target_time_0, target_time_1, target_time_2, target_time_3)       # 積算値


def process_device_data(device_data_list, pushlog_api_id: uuid.UUID, gateway_id: str):
    devices_mapping = {
        f"{gateway_id}-{data['deviceId']}": data for data in device_data_list
    }

    # デバイスの存在チェック
    existing_devices = Device.objects.filter(
        pushlog_unique_id__in=devices_mapping.keys()
    )
    existing_pushlog_ids = existing_devices.values_list("pushlog_unique_id", flat=True)

    # 更新が必要なデバイスデータの準備
    devices_to_update = []
    for device in existing_devices:
        if device.pushlog_unique_id:
            data = devices_mapping[device.pushlog_unique_id]
            if device.data_source_name != data['deviceName']:
                device.data_source_name = data['deviceName']
                devices_to_update.append(device)

    # 既存のデバイスを更新
    Device.objects.bulk_update(devices_to_update, ['data_source_name'])
    logging.info(f"{len(devices_to_update)} 個のデバイスを更新しました")

    # 新規作成が必要なデバイスデータの準備
    non_existing_pushlog_unique_ids = set(devices_mapping.keys()) - set(existing_pushlog_ids)

    # Bizでは単位は自動生成。基本的には「kWh」「Wh」しか認識してない。他の単位の時には数値をそのまま残すだけ
    unit_pattern = r'[\(\[](.*?)[\)\]]$'
    devices_to_create = []
    data_structures_to_create = []
    for pushlog_unique_id in non_existing_pushlog_unique_ids:
        data_source_name = devices_mapping[pushlog_unique_id]['deviceName']
        device_number = devices_mapping[pushlog_unique_id]['deviceId']
        # 名前の先頭15文字以内に「積算」があれば積算値。それ以外なら瞬時値
        is_instantaneous = (not data_source_name) or ("積算" not in data_source_name)
        # 単位の取得:データ取得対象名の末尾に()か[]で囲まれている。ない場合もある
        # 本来的には、データ取得対象名に書かれている単位を使用するところであるが
        # グラフ表示は電力値を前提としているので、kWh, Wh 以外が指定された場合の単位はkWhにする
        unit_id = None
        unit_name = None
        unit_match = re.search(unit_pattern, data_source_name)
        if unit_match:
            unit_name = unit_match.group(1)
            # if unit_name:
            #     unit_id = Unit.objects.filter(name=unit_name).first()
            #     if not unit_id:
            #         if unit_name in ["kWh", "Wh"]:
            #             environmental_type_id = EnvironmentalType.objects.filter(name=ENV_TYPE_ELECTRICITY)
            #         else:
            #             environmental_type_id = None
            #         unit_id = Unit.objects.create(name=unit_name, environmental_type_id=environmental_type_id)
        if unit_name is None or unit_name not in ["kWh", "Wh"]:
            unit_name = "kWh"
        unit_id = Unit.objects.filter(name=unit_name).first()

        # Entityはこのタイミングで作成する。DataStructure,　Deviceに設定するため。
        entity = Entity.objects.create(
            name = pushlog_unique_id,
            company = None
        )
        data_structure = DataStructure(
            ancestor = entity,
            descendant = entity,
            depth = 0
        )
        device = Device(
            pushlog_unique_id=pushlog_unique_id,
            pushlog_api_id=pushlog_api_id,
            gateway_id_id=gateway_id,
            device_number=device_number,
            data_source_name=data_source_name,
            name = pushlog_unique_id,
            # Biz用の追加
            unit_id = unit_id,
            enable_data_collection = True,
            entity = entity,
            is_instantaneous = is_instantaneous
        )
        devices_to_create.append(device)
        data_structures_to_create.append(data_structure)

    # 新規デバイスを一括作成
    Device.objects.bulk_create(devices_to_create)
    DataStructure.objects.bulk_create(data_structures_to_create)
    logging.info(f"{len(devices_to_create)} 個の新規デバイスを作成しました")

def update_pushlog_api_data(pushlog_api: PushLogApi):
    if pushlog_api.key is None:
        return

    # gatewayデータを取得
    pushlog_api_call = PushlogApiCall(pushlog_api=pushlog_api)
    response_json = pushlog_api_call.gateways()
    if response_json is None:
        return
    
    # gatewayの登録処理
    for gateway_data in response_json:
        if Gateway.objects.filter(id=gateway_data['gatewayId']).exists():
            # 登録ずみなら更新
            Gateway.objects.filter(id=gateway_data['gatewayId']).update(
                name=gateway_data['gatewayName'],
                model=gateway_data['model'],
                is_activated=gateway_data['isActivated'],
                firmware_version=gateway_data['firmwareVersion'],
                pushlog_api=pushlog_api,
            )
        else:
            # 未登録なら新規作成
            gateway = Gateway.objects.create(
                id=gateway_data['gatewayId'],
                name=gateway_data['gatewayName'],
                model=gateway_data['model'],
                is_activated=gateway_data['isActivated'],
                firmware_version=gateway_data['firmwareVersion'],
                pushlog_api=pushlog_api,
            )
            # GatewayMasterを作成
            GatewayMaster.objects.create(gateway_id=gateway, gateway_type="PUSHLOG")


    # gatwwayごとにデバイスの処理
    gateway_id_list = list(map(lambda data: data['gatewayId'], response_json))
    for gateway_id in gateway_id_list:
        if pushlog_api_call.is_connected(gateway_id) == False:
            continue

        # gatewayに対応したデバイスの情報を取得
        response_json = pushlog_api_call.normal_triggers(gateway_id)
        #normal_triggers_res

        all_device_data = [
            device_data
            for normal_trigger_data in response_json
            for device_data in normal_trigger_data["devices"]
        ]

        # # 1000件ずつ分割して処理
        # BATCH_SIZE = 1000
        # device_data_iter = iter(all_device_data)
        # while True:
        #     batch = list(islice(device_data_iter, BATCH_SIZE))
        #     if not batch:
        #         break
        #     process_device_data(batch, pushlog_api.id, gateway_id)
        process_device_data(all_device_data, pushlog_api.id, gateway_id)

    # 時系列データの作成
    for gateway_id in gateway_id_list:
        logging.info(f'create_timeseries_data start: {gateway_id}')
        try:
            # GatewayMasterのlicense_limitが今日より過去の日付の場合はデータ作成しない
            gateway_master = GatewayMaster.objects.filter(gateway_id_id=gateway_id).first()
            if gateway_master is not None:
                if gateway_master.license_limit is not None and gateway_master.license_limit < datetime.date.today():
                    logging.info(f"license_limitが過去の日付です。データ作成をスキップします。")
                    continue
            create_timeseries_data(pushlog_api.id, gateway_id)
        except Exception as e:
            logging.error(f"create_timeseries_data error: {e}")
            raise e
        else:
            logging.info(f'create_timeseries_data end: {gateway_id}')

@receiver(pre_save, sender=PushLogApi)
def set_pushlog_api_key_updated_flag(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # 新規作成時
        if instance.key:
            instance._pushlog_api_key_updated = True
        return

    # 更新時にpushlog_api_keyが変更された場合
    if obj.key != instance.key and instance.key:
        instance._pushlog_api_key_updated = True

@receiver(post_save, sender=PushLogApi)
def handle_pushlog_api_key_updated(sender, instance, **kwargs):
    if hasattr(instance, '_pushlog_api_key_updated'):
        transaction.on_commit(lambda: start_update_push_log_thread(instance.id))

def start_update_push_log_thread(pushlog_api_id):
    t = Thread(target=update_push_log, args=(pushlog_api_id,))
    t.start()

# cron.pyから呼ばれる
# pushlog_apiごと（pushlog_api_keyごと）の処理
def update_push_log(pushlog_api_id=None):
    if pushlog_api_id is not None:
        # 指定されたPushlogAPIのみを対象とする
        target_pushlog_apis = PushLogApi.objects.filter(id=pushlog_api_id)
    else:
        target_pushlog_apis = PushLogApi.objects.all()

    # target_pushlog_apis = target_pushlog_apis.filter(company__batch_enabled=True)

    # Tableがない(migrateがまだの)状態では、Exceptionで落ちて、
    # appコンテナ自体が立ち上がらなくなるので、それを回避するための処理
    try:
        _ = target_pushlog_apis.exists()
    except:
        logging.info("ユーザが存在しません")
        return

    try:
        _ = target_pushlog_apis.exists()
    except:
        logging.info("PushLogApiが存在しません")
        return

    # 削除処理でのロックが解放されるのを待つ
    with lock_data:
        # ユーザ単位での並列処理
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for pushlog_api in target_pushlog_apis:
                futures.append(
                    executor.submit(
                        update_pushlog_api_data,
                        pushlog_api=pushlog_api,
                    )
                )
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                        print(e)
        # デアカウント用の時系列データ作成
        if pushlog_api_id is None:
            create_demo_timeseries_data()

# データ削除の処理
# 削除処理スレッドの定義
def thread_delete_data():
    # Queueにデータがある限り繰り返す
    while not delete_q.empty():
        with lock_data:  # ロックが解放されるのを待つ
            # Queueからアイテムを取り出す
            data:Data = delete_q.get()
            # dataを減算処理
            Data.sub_all_hierarchical_data(data)
        # 1秒間スリープ
        time.sleep(1)
    while not delete_q2.empty():
        with lock_data:  # ロックが解放されるのを待つ
            data:Data = delete_q2.get()
            # dataを削除
            data.delete()
        # 1秒間スリープ
        time.sleep(1)

# 削除処理スレッドの前準備
def pre_thread_delete_data(aware_dt, company_id):
    # 減算処理：Hourのデータを検索する
    data_list = [data for data in Data.objects.filter(get_data_at__lte=aware_dt, date_type='hour') if str(data.entity.company_id) == str(company_id)]
    for data in data_list:
        delete_q.put(data)
    # 削除処理：date_typeに関係なくデータを検索する
    for data in [data for data in Data.objects.filter(get_data_at__lte=aware_dt) if str(data.entity.company_id) == str(company_id)]:
        delete_q2.put(data)
    thread_del = threading.Thread(target=thread_delete_data)
    thread_del.start()
    

# データを格納してスレッドを呼び出す
def kick_delete_thread(date, time, company_id):
    dt = datetime.datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    aware_dt = tokyo_tz.localize(dt)

    threash_pre_delete = threading.Thread(target=pre_thread_delete_data, args=(aware_dt, company_id))
    threash_pre_delete.start()

    # # データの一覧を取得して表示する
    # # 減算処理：Hourのデータを検索する
    # data_list = [data for data in Data.objects.filter(get_data_at__lte=aware_dt, date_type='hour') if str(data.entity.company_id) == str(company_id)]
    # for data in data_list:
    #     delete_q.put(data)
    # # 削除処理：date_typeに関係なくデータを検索する
    # for data in [data for data in Data.objects.filter(get_data_at__lte=aware_dt) if str(data.entity.company_id) == str(company_id)]:
    #     delete_q2.put(data)

    # thread_del = threading.Thread(target=thread_delete_data)
    # thread_del.start()

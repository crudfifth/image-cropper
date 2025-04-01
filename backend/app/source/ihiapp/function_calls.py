import datetime
import logging
import requests
import traceback
import os
import environ
import time

from config.settings import BASE_DIR
from enum import Enum
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.cache import cache
from .constants import SENDER_EMAIL

from users.models import Company, User
from .models import Data, DataType, Device, Gateway, PushLogApi

# データ取得時のエラー
class UpdateError(Enum):
    DEMO = "demo"
    BAD_REQUEST = "400"
    UNAUTHORIZED = "401"
    NOT_FOUND = "404"
    TOO_MANY_REQUESTS = "429"
    TIMEOUT = "timeout_exception"
    UNKNOWN = "unknown_exception"
    DATA_IS_EMPTY = "data_is_empty"
    DATA_IS_INVALID = "data_is_invalid"
    UNIT_IS_NOT_SET = "unit_is_not_set"
    RHO_IS_NOT_SET = "rho_is_not_set"
    ENTITY_IS_NOT_SET = "entity_is_not_set"


PUSH_LOG_URL = "https://api.pushlog.jp/v3/gateways"

env = environ.Env()
env.read_env(BASE_DIR + '/.env')

class PushlogApiCall:
    def __init__(self, pushlog_api=None, pushlog_api_id=None):
        if pushlog_api is None and pushlog_api_id is None:
            logging.error(f'PushlogApiCallの初期化に失敗しました。: Noneが指定されています。')
            return

        try:
            if pushlog_api is not None:
                self.pushlog_api = pushlog_api
                self.pushlog_api_id = pushlog_api.id
            else:
                self.pushlog_api = PushLogApi.objects.filter(id=pushlog_api_id).first()
                self.pushlog_api_id = pushlog_api_id

            self.headers = {
                "X-Pushlog-API-Key" : self.pushlog_api.key,
            }
        except Exception as e:
            logging.error(f'PushlogApiCallの初期化に失敗しました。: {e}')

    # Gatewayのデータを取得する
    def gateways(self):
        api_name = 'gateways'
        url = PUSH_LOG_URL
        wait_seconds = 60*3
        response_json = self._call_function(api_name, url, wait_seconds=wait_seconds)
        return response_json

    # normal_triggersのデータを取得する
    def normal_triggers(self, gateway_id:str=None):
        api_name = 'normal_triggers'
        url = PUSH_LOG_URL + f"/{gateway_id}/config/normal_triggers"
        wait_seconds = 10
        response_json = self._call_function(api_name, url, gateway_id=gateway_id, wait_seconds=wait_seconds)
        return response_json

    # Gatewayの状況を確認する
    def status(self, gateway_id:str=None):
        api_name = 'status'
        url = PUSH_LOG_URL + f"/{gateway_id}/status"
        wait_seconds = 10
        return self._call_function(api_name, url, gateway_id=gateway_id, wait_seconds=wait_seconds)

    # Gatewayが接続状態かどうかを判定する
    def is_connected(self, gateway_id:str=None):
        response_json = self.status(gateway_id=gateway_id)
        if response_json is None:
            return False
        # 接続してない場合はlogging出力して処理を終える
        try:
            connected = response_json['connected']
            if connected == False:
                logging.info(f"Gatewayが接続されていません gateway: {gateway_id}")
                return False
        except:
            logging.info(f"要求されたGatewayのデータが空です gateway: {gateway_id}")
            return False
        return True


    # Historical Dataを取得する
    def historical(self, gateway_id:str=None, params=None):
        api_name = 'historical'
        url = PUSH_LOG_URL + f"/{gateway_id}/historical"
        wait_seconds = 60*3
        response_json = self._call_function(api_name, url, gateway_id=gateway_id, params=params, wait_seconds=wait_seconds)
        if response_json is None:
            return None

        # response_jsonが空の場合は、エラーとする
        if len(response_json) == 0:
            email_notification(err=UpdateError.DATA_IS_EMPTY, pushlog_api=self.pushlog_api, gateway_id=gateway_id, api_name=api_name)
            logging.info(f"要求されたGatewayのデータが空です gateway: {gateway_id}")
            return None

        return response_json

    def _call_function(self, api_name, url, gateway_id=None, params=None, wait_seconds=60):
        retry_count = 2
        # logging.info(f"try : api_name: {api_name}, url : {url}, gateway_id: {gateway_id}")
        while retry_count > 0:
            retry_count -= 1
            try:
                response = requests.get(url, headers=self.headers, params=params) if params is not None else requests.get(url, headers=self.headers)
                if response.status_code == 200 and response.json() is not None:
                    # json形式データを取得
                    return response.json()
                else:
                    msg = response.status_code
            except Exception as e:
                # msg = traceback.format_exc()
                msg = str(e)
                pass
            logging.info(f"wait {wait_seconds} seconds and retry {2-retry_count}:  pushlog: {self.pushlog_api_id}, api_name: {api_name} gateway_id: {gateway_id} error: {msg}")
            time.sleep(wait_seconds)

        try:
            response = requests.get(url, headers=self.headers, params=params) if params is not None else requests.get(url, headers=self.headers)

            if response.status_code != 200:
                # エラーである
                logging.error(f'{url} データの取得に失敗しました: {response}')
                try:
                    if response.status_code == 400:
                        email_notification(err=UpdateError.BAD_REQUEST, pushlog_api=self.pushlog_api, gateway_id=gateway_id, api_name=api_name)
                    elif response.status_code == 401:
                        email_notification(err=UpdateError.UNAUTHORIZED, pushlog_api=self.pushlog_api, gateway_id=gateway_id, api_name=api_name)
                    elif response.status_code == 404:
                        email_notification(err=UpdateError.NOT_FOUND, pushlog_api=self.pushlog_api, gateway_id=gateway_id, api_name=api_name)
                    elif response.status_code == 429:
                        email_notification(err=UpdateError.TOO_MANY_REQUESTS, pushlog_api=self.pushlog_api, gateway_id=gateway_id, api_name=api_name)
                except Exception as e:
                    logging.error(f'メール発報に失敗しました: {e}')
                return None
        except requests.exceptions.Timeout as e:
            # エラーである
            email_notification(err=UpdateError.TIMEOUT, pushlog_api=self.pushlog_api, gateway_id=gateway_id, api_name=api_name)
            logging.error(f'{url} データの取得に失敗しました: {e}')
            return None
        except Exception as e:
            # エラーである
            email_notification(err=UpdateError.UNKNOWN, pushlog_api=self.pushlog_api, gateway_id=gateway_id, api_name=api_name, additional_msg=f'{e}')
            logging.error(f'{url} データの取得に失敗しました: {e}')
            return None

        # json形式データを取得
        return response.json()


# DATA_IS_INVALIDでのメール発報
def email_notification_invalid(pushlog_api=None, pushlog_api_id=None, gateway_id:str=None,
                       device_name=None, data_source_name=None, api_name:str=None, additional_msg=None):
    return email_notification(err=UpdateError.DATA_IS_INVALID, pushlog_api=pushlog_api, pushlog_api_id=pushlog_api_id, gateway_id=gateway_id,
                       device_name=device_name, data_source_name=data_source_name, api_name=api_name, additional_msg=additional_msg)

# RHO_IS_NOT_SETでのメール発報
def email_notification_rho_not_set(pushlog_api=None, pushlog_api_id=None, gateway_id:str=None,
                       device_name=None, data_source_name=None, api_name:str=None, additional_msg=None):
    return email_notification(err=UpdateError.RHO_IS_NOT_SET, pushlog_api=pushlog_api, pushlog_api_id=pushlog_api_id, gateway_id=gateway_id,
                       device_name=device_name, data_source_name=data_source_name, api_name=api_name, additional_msg=additional_msg)

# DATA_IS_EMPTYでのメール発報
def email_notification_data_is_empty(pushlog_api=None, pushlog_api_id=None, gateway_id:str=None,
                          device_name=None, data_source_name=None, api_name:str=None):
    return email_notification(err=UpdateError.DATA_IS_EMPTY, pushlog_api=pushlog_api, pushlog_api_id=pushlog_api_id, gateway_id=gateway_id,
                       device_name=device_name, data_source_name=data_source_name, api_name=api_name)

# UNIT_IS_NOT_SETでのメール発報
def email_notification_unit_is_not_set(pushlog_api=None, pushlog_api_id=None, gateway_id:str=None,
                            device_name=None, data_source_name=None, api_name:str=None):
    return email_notification(err=UpdateError.UNIT_IS_NOT_SET, pushlog_api=pushlog_api, pushlog_api_id=pushlog_api_id, gateway_id=gateway_id,
                        device_name=device_name, data_source_name=data_source_name, api_name=api_name)

# ENTITY_IS_NOT_SETでのメール発報
def email_notification_entity_is_not_set(pushlog_api=None, pushlog_api_id=None, gateway_id:str=None,
                            device_name=None, data_source_name=None, api_name:str=None):
    return email_notification(err=UpdateError.ENTITY_IS_NOT_SET, pushlog_api=pushlog_api, pushlog_api_id=pushlog_api_id, gateway_id=gateway_id,
                        device_name=device_name, data_source_name=data_source_name, api_name=api_name)

# メール発報の処理
def email_notification(err=UpdateError.DEMO, pushlog_api=None, pushlog_api_id=None, gateway_id:str=None,
                       device_name=None, data_source_name=None, api_name:str=None, additional_msg=None):
    return
    if pushlog_api is None:
        if pushlog_api_id is not None:
            pushlog_api = PushLogApi.objects.filter(id=pushlog_api_id).first()
    else:
        pushlog_api_id = pushlog_api.id

    if not add_cache_data(err, pushlog_api_id, gateway_id, data_source_name):
        # 本日すでにエラーが発生している場合は、メールを送信しない
        return

    # 管理者にメールを送信する
    admin_mail = None  # 強制的にメール宛先を差し替える場合は、ここにメールアドレスを設定する

    # pushlog_api_idがNoneの場合は、デモ用のメールを送信する
    if pushlog_api is None:
        to_emails = [User.objects.filter(is_demo=True).first().email]
        bcc_emails = []
    else:
        # Userモデルからスーパーユーザーと'IHI管理者'グループのメールアドレスを取得し、集合に格納
        to_emails = [user.email for user in User.objects.filter(groups__name='IHI管理者')]
        bcc_emails = [user.email for user in User.objects.filter(is_superuser=True) if user.email not in to_emails]
        if to_emails == []:
            # IHI管理者がいない場合は、管理者（スーパーユーザー）をメール宛先にする
            to_emails = bcc_emails
            bcc_emails = []
        # もし、送信先が指定されていなければ、メール発報を中止する
        if to_emails == []:
            logging.info(f"メール発報を中止しました。送信先が指定されていません。")
            return

    # if pushlog_api is None:
    #     to_emails = User.objects.filter(is_demo=True).first().email
    # else:
    #     # 各企業の管理者に送信する場合
    #     company_id = pushlog_api.company_id
    #     user = Company.objects.filter(id=company_id).first().admin_user_id
    #     to_emails = user.email


    title = "【IHIカーボンクレジット開発】データ収集に失敗しました"
    if env('TYPE') != "live_server":
        title = "【開発環境】" + title
    default_action = "    システム管理者にお問合せください。\n"
    body = "データ収集に失敗しました。\n"

    # 強制的にメール宛先を差し替えたら、管理者メールアドレス一覧も内容に記載する
    if admin_mail is not None:
        body += "IHI管理者メールアドレス：" + ", ".join(to_emails) +"\n"
        body += "管理者メールアドレス：" + ", ".join(bcc_emails) +"\n\n"
        to_emails = [admin_mail]
        bcc_emails = []

    body += "発生日時：\n"
    body += f"    {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n\n"

    body += "呼び出し情報：\n"
    if pushlog_api_id is not None:
        pushlog_api_str = f"{pushlog_api_id}"
        pushlog_api_id_masked = pushlog_api_str[:4] + '*'*(len(pushlog_api_str)-8) + pushlog_api_str[-4:]
        body += f"    PushlogAPI ID: {pushlog_api_id_masked}\n"
    if gateway_id is not None:
        gateway_id_masked = gateway_id[:4] + '*'*(len(gateway_id)-8) + gateway_id[-4:]
        body += f"    Gateway ID: {gateway_id_masked}\n"
    if device_name is not None:
        body += f"    Device Name: {device_name}\n"
    if api_name is not None:
        body += f"    API Name: {api_name}\n"
    body += "\n"

    body += "エラー内容：\n"
    # APIのResponseでのHttpステータスコード
    if err == UpdateError.BAD_REQUEST:
        body += "    Httpステータスコード: 400\n"
        body += "    API呼び出しに失敗しました。\nPushLoagAPIキー、ゲートウェイIDを見直してください。\n"
    elif err == UpdateError.UNAUTHORIZED:
        body += "    Httpステータスコード: 401\n"
        body += "    サーバーの認証に失敗しました。\nPushLoagAPIキーを見直してください。\n"
    elif err == UpdateError.NOT_FOUND:
        body += "    Httpステータスコード: 404\n"
        body += "    呼び出し先が間違っています。\nGatewayIDを見直してください。\n"
    elif err == UpdateError.TOO_MANY_REQUESTS:
        body += "    Httpステータスコード: 429\n"
        body += "    API要求数が超過しています。\n" + default_action

    # APIのResponseでのエラー
    elif err == UpdateError.TIMEOUT:
        body += "    タイムアウトが発生しました。\n"
        body += "    サーバーが応答していません。ネットワーク遅延かサーバー遅延が考えられます。\n" + default_action
    elif err == UpdateError.UNKNOWN:
        body += "    システムで不明のエラーが発生しました。\n"
        if additional_msg is not None:
            body += f"    （{additional_msg}）\n" + default_action

    # データの不整合：デバイス/Gatewayに紐づく
    elif err == UpdateError.DATA_IS_EMPTY:
        body += "    受け取ったデータが空です。\n"
        if data_source_name is not None:
            body += f"    データ取得対象名（{data_source_name}）を見直してください。\n"
        else:
            body += f"    Gatewayを見直してください。\n"
    elif err == UpdateError.DATA_IS_INVALID:
        body += "    データが不正です。正しい数値データ以外を登録しようとしたようです。\n"
        if additional_msg is not None:
            body += f"    （{additional_msg}）\n" + default_action
        else:
            body += f"    データ取得対象（{data_source_name}）を見直してください。\n"

    # データの不備：デバイスに紐づく
    elif err == UpdateError.UNIT_IS_NOT_SET:
        body += f"    単位が設定されていません。\n"
        body += f"    データ取得対象（{data_source_name}）に単位を設定してください。\n"
    elif err == UpdateError.RHO_IS_NOT_SET:
        body += f"    燃料の比重が設定されていません。\n"
        body += f"    データ取得対象（{data_source_name}）に燃料の比重を設定してください。\n"
    elif err == UpdateError.ENTITY_IS_NOT_SET:
        body += f"    階層構造に正しく設定されていません。\n"
        body += f"    データ取得対象（{data_source_name}）の設定を見直してください。\n"
    send_email(to_emails, bcc_emails, title, body)


def send_email(to_emails, bcc_emails, title, body):
    # もし、送信先to_emailsが指定されていなければ、送信先にbcc_emailsを設定する
    if to_emails is None or len(to_emails) == 0:
        to_emails = bcc_emails
        bcc_emails = []

    # もし、送信先が指定されていなければ、メール発報を中止する
    if to_emails is None or len(to_emails) == 0:
        logging.info(f"メール発報を中止しました。送信先が指定されていません。")
        return

    message = Mail(
        from_email = SENDER_EMAIL,   # 'from_email@example.com',
        to_emails = to_emails,        # ['to@example.com']
        subject = title,              # 'Sending with SendGrid is Fun',
        plain_text_content = body     # 'and easy to do anywhere, even with Python'
    )
    for bcc_email in bcc_emails:
        message.add_bcc(bcc_email)

    try:
        SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
    except Exception as e:
        e_str = str(e)
        logging.info(f"メール発報でエラーが発生しました。：{e_str}")

# エラー情報をキャッシュに保存する
# すでに登録済みなら、Falseを返す -> 重複してメールを送信しない
# エラー情報のデータ構造
# {
#     '20210101': {
#         'pushlog_api_id': {
#             'error_list': [UpdateError.UNAUTHORIZED, UpdateError.BAD_REQUEST],
#             'gateway_id': {
#                 'error_list': [UpdateError.BAD_REQUEST, UpdateError.NOT_FOUND],
#                 'data_source_name': {
#                     'error_list': [UpdateError.DATA_IS_EMPTY, UpdateError.DATA_IS_INVALID],
#                 }
#             }
#         }
#     }
# }
def add_cache_data(err, pushlog_api_id=None, gateway_id=None, data_source_name=None):
    # 日付の文字列を取得する
    today_str = datetime.datetime.now().strftime('%Y%m%d')

    # キャッシュからデータを取得する
    # データがない場合は、空の辞書を返す
    # 今日の日付のデータを取得する。
    cache_data = cache.get('ihi-backend-err', {})
    today_data = cache_data.get(today_str, {})

    if pushlog_api_id != None:
        pushlog_api_id_data = today_data.get(pushlog_api_id, {})
    else:
        return True

    # データの追加
    # pushlog_api_id単位: pushlog_api_id != None and gateway_id == None and device_name == None
    if gateway_id == None:
        error_list = pushlog_api_id_data.get('error_list', [])
        if err in error_list:
            return False
        error_list.append(err)
        pushlog_api_id_data['error_list'] = error_list
    # gateway単位 : pushlog_api_id != None and gateway_id != None and device_name == None
    else:
        gateway_data = pushlog_api_id_data.get(gateway_id, {})
        if data_source_name == None:
            error_list = gateway_data.get('error_list', [])
            if err in error_list:
                return False
            error_list.append(err)
            gateway_data['error_list'] = error_list
            pushlog_api_id_data[gateway_id] = gateway_data
        # device単位: pushlog_api_id != None and gateway_id != None and device_name != None
        else:
            device_data = gateway_data.get(data_source_name, {})
            error_list = device_data.get('error_list', [])
            if err in error_list:
                return False
            error_list.append(err)
            device_data['error_list'] = error_list
            gateway_data[data_source_name] = device_data
            pushlog_api_id_data[gateway_id] = gateway_data

    today_data[pushlog_api_id] = pushlog_api_id_data

    # データをキャッシュに保存する
    # 今日より前のデータは不要なので、削除する
    CACHE_TIMEOUT = 60 * 60 * 24  # 24時間
    cache_data = {}
    cache_data[today_str] = today_data
    cache.set('ihi-backend-err', cache_data, timeout=CACHE_TIMEOUT)

    return True

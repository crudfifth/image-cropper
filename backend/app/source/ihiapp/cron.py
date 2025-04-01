import datetime
import logging
import time

import environ
from apscheduler.schedulers.background import BackgroundScheduler
from config.settings import BASE_DIR

from .function_update_data import update_push_log
from .function_update_data_minute import update_push_log_minute
from .function_lock_account import search_and_lock_accounts


def ihi_schedule():
   update_push_log()

# def ihi_schedule_minute():
#    update_push_log_minute()

def account_lock_schedule():
   search_and_lock_accounts()


job_defaults = {
   'coalesce': False,
   'max_instances': 5,
   # 'standalone' : True
}

# ここから始まる
# 開始時間を指定して、定期的に繰り返し実行する
# API呼び出しのタイミングを、00/30分にするための処理
# 起動時刻が必ずしも区切りの良い時刻だとは限らないから
def start():
   # 起動時のPushlogを更新：スケジューラでの実行とは別に、起動時にも実行する
   # スケジューラでの実行結果と同じ時刻の取得結果になる場合もあるが、内部で排他処理を行っているので、問題ない
#   update_push_log()

   # 実行間隔：30分間隔
   interval = 30
   # 開始時刻＝現在時刻を実行間隔に合わせて切り上げた時刻＋デバイス側での収集時間とのすり合わせ2分
   # start_dt = round_time_to_next_min(datetime.datetime.now(), interval) + datetime.timedelta(minutes=2)
   # live環境でなければ、開始時刻をランダムにずらす

   scheduler = BackgroundScheduler()
   scheduler.configure(job_defaults=job_defaults)

   env = environ.Env()
   env.read_env(BASE_DIR + '/.env')

   # UTCの15時(つまり日本時間の0時)に、長期間アクセスがないユーザーを探してロックする
   scheduler.add_job(account_lock_schedule, 'cron', hour=15)

   # スケジュールでpushlogの更新を行う
   if(env('TYPE') == "live_server"):
      print("----------------- Live Server -----------------")
      # 30分間隔で実行
      start_dt = round_time_to_next_min(datetime.datetime.now(), interval) + datetime.timedelta(minutes=2)
      scheduler.add_job(ihi_schedule, 'interval', minutes=interval, start_date=start_dt)

      # # 1分間隔で実行
      # scheduler.add_job(ihi_schedule_minute, 'interval', minutes=1)

   elif(env('TYPE') == "staging_server"):
      print("----------------- Staging Server -----------------")
      # 30分間隔で実行
      # スケジュールでの開始時間をランダムにずらす
      import random
      random_number = random.randint(0, 9)
      start_dt = round_time_to_next_min(datetime.datetime.now(), interval) + datetime.timedelta(minutes=2+3+random_number)
      scheduler.add_job(ihi_schedule, 'interval', minutes=interval, start_date=start_dt)

      # # 1分間隔で実行
      # scheduler.add_job(ihi_schedule_minute, 'interval', minutes=1)

   else:
      pass

   scheduler.start()


# 指定時刻を、インターバルでキリのいい時刻に繰り上げ
def round_time_to_next_min(dt, interval):
   minute = dt.minute
   delta = (minute + interval) // interval * interval - minute
   rounded_dt = dt + datetime.timedelta(minutes=delta)
   return rounded_dt.replace(second=0, microsecond=0)

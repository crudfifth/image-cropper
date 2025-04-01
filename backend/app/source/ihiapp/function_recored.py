
from .models import DataPerHour, DataPerDate, DataPerMonth, DataPerYear
from .models import DeviceDataPerHour, DeviceDataPerDate, DeviceDataPerMonth, DeviceDataPerYear
from .models import Device
from users.models import User
import datetime
import random


# 開始と終了の日付と時刻をdatetime.datetimeで指定して、DataPerHourのデータを作成する関数
def create_data_per_hour(start_date, end_date, user_id):
    # 開始日と終了日の間の日付を取得
    date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    # 開始日と終了日の間の日付を取得


    # 開始日と終了日の間の日付と時刻を取得
    for date in date_list:
        for hour in range(24):
            for minute in 0, 30:
                # DataPerHourのデータを作成
                # data_per_hourが存在する場合は保存しない
                if DataPerHour.objects.filter(year=date.year, month=date.month, date=date.day, hour=hour, minute=minute, user_id=User.objects.get(id=user_id)).exists():
                    pass
                else:
                    data_per_hour = DataPerHour(
                        year=date.year,
                        month=date.month,
                        date=date.day,
                        hour=hour,
                        minute=minute,
                        user_id=User.objects.get(id=user_id),
                        # 小数点でランダムな値を作成

                        electrical_value=random.uniform(0,10),
                        water_value=random.uniform(0,10),
                        fuel_value=random.uniform(0,10),
                    )
                    data_per_hour.save()


        # # DataPerDateのデータを作成
        # # data_per_dateが存在する場合は保存しない
        # if DataPerDate.objects.filter(year=date.year, month=date.month, date=date.day, user_id=User.objects.get(id=user_id)).exists():
        #     pass
        # else:
            
        #     data_per_date = DataPerDate(
        #         year=date.year,
        #         month=date.month,
        #         date=date.day,
        #         user_id=User.objects.get(id=user_id),

        #         electrical_value=random.uniform(0,1000),
        #         water_value=random.uniform(0,1000),
        #         fuel_value=random.uniform(0,1000),
        #     )
        #     data_per_date.save()

        # # DataPerMonthのデータを作成
        # # data_per_monthが存在する場合は保存しない
        # if DataPerMonth.objects.filter(year=date.year, month=date.month, user_id=User.objects.get(id=user_id)).exists():
        #     pass
        # else:
        #     data_per_month = DataPerMonth(
        #         year=date.year,
        #         month=date.month,
        #         user_id=User.objects.get(id=user_id),
        #         electrical_value=random.uniform(0,100000),
        #         water_value=random.uniform(0,100000),
        #         fuel_value=random.uniform(0,100000),
        #     )
        #     data_per_month.save()
        

        # # DataPerYearのデータを作成
        # # data_per_yearが存在する場合は保存しない
        # if DataPerYear.objects.filter(year=date.year, user_id=User.objects.get(id=user_id)).exists():
        #     pass
        # else:
        #     data_per_year = DataPerYear(
        #         year=date.year,
        #         user_id=User.objects.get(id=user_id),
        #         electrical_value=random.uniform(0,10000000),
        #         water_value=random.uniform(0,10000000),
        #         fuel_value=random.uniform(0,10000000),
        #     )
        #     data_per_year.save()

# 開始と終了の日付と時刻をdatetime.datetimeで指定して、DeviceDataPerHourのデータを作成する関数
def create_device_data_per_hour(start_date, end_date, user_id, device_id):
    # 開始日と終了日の間の日付を取得
    date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    # 開始日と終了日の間の日付を取得


    # 開始日と終了日の間の日付と時刻を取得
    for date in date_list:
        for hour in range(24):
            for minute in 0, 30:
                # DeviceDataPerHourのデータを作成
                # device_data_per_hourが存在する場合は保存しない
                if DeviceDataPerHour.objects.filter(year=date.year, month=date.month, date=date.day, hour=hour, minute=minute, user_id=User.objects.get(id=user_id), device_id=Device.objects.get(id=device_id)).exists():
                    pass
                else:
                    electrical_value = round(random.uniform(0,10), 2)
                    device_data_per_hour = DeviceDataPerHour(
                        year=date.year,
                        month=date.month,
                        date=date.day,
                        hour=hour,
                        minute=minute,
                        user_id=User.objects.get(id=user_id),
                        # 小数点でランダムな値を作成
                        electrical_value = electrical_value,
                        water_value = round(electrical_value * 0.1, 2),
                        fuel_value = round(electrical_value * 0.01, 2),
                        device_id=Device.objects.get(id=device_id),
                    )
                    device_data_per_hour.save()

def update_water_fuel_data():
    # filter = {
    #     'year': 2021,
    #     'month': 1,
    #     'date': 1,
    #     'hour': 0,
    #     'minute': 0,
    #     # 範囲指定
    #     'get_data_date' : 
    # }

    first_date = datetime.datetime(2023, 3, 12, 0, 0, 0)
    last_date = datetime.datetime(2023, 3, 17, 0, 0, 0)

    device_data_per_hour = DeviceDataPerHour.objects.filter(get_data_date__range=(first_date, last_date), user_id=User.objects.get(email='ihi@bizfreak.co.jp'))
    # for data in device_data_per_hour:
    #     print(data.get_data_date)
    for data in device_data_per_hour:
        data.water_value = round(data.electrical_value * 0.1, 2)
        data.fuel_value = round(data.electrical_value * 0.01, 2)
        data.save()
    print(device_data_per_hour)





# DataPerHourを全削除
def delete_all_data_per_hour():
    DataPerHour.objects.all().delete()
# DataPerDateを全削除
def delete_all_data_per_date():
    DataPerDate.objects.all().delete()
# DataPerMonthを全削除
def delete_all_data_per_month():
    DataPerMonth.objects.all().delete()
# DataPerYearを全削除
def delete_all_data_per_year():
    DataPerYear.objects.all().delete()
# DeviceDataPerHourを全削除
def delete_all_device_data_per_hour():
    DeviceDataPerHour.objects.all().delete()
# DeviceDataPerDateを全削除
def delete_all_device_data_per_date():
    DeviceDataPerDate.objects.all().delete()
# DeviceDataPerMonthを全削除
def delete_all_device_data_per_month():
    DeviceDataPerMonth.objects.all().delete()
# DeviceDataPerYearを全削除
def delete_all_device_data_per_year():
    DeviceDataPerYear.objects.all().delete()

def delete_all_data():
    delete_all_data_per_hour()
    delete_all_data_per_date()
    delete_all_data_per_month()
    delete_all_data_per_year()
    delete_all_device_data_per_hour()
    delete_all_device_data_per_date()
    delete_all_device_data_per_month()
    delete_all_device_data_per_year()



def create_record():
    # 開始日と終了日を指定して、DataPerHourのデータを作成
    start_date = datetime.datetime(2022, 1, 1, 0)
    end_date = datetime.datetime(2022, 12, 31, 23)
    device_list = Device.objects.all()
    for device in device_list:
        create_device_data_per_hour(start_date, end_date, User.objects.get(email='ihi@bizfreak.co.jp').id, device.id)





# if __name__ == '__main__':
#     # 開始日と終了日を指定して、DataPerHourのデータを作成
#     start_date = datetime.date(2021, 1, 1)
#     end_date = datetime.date(2021, 12, 31)
#     create_data_per_hour(start_date, end_date)

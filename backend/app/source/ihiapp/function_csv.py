import csv
import pandas as pd
from .models import DataPerHour, DataPerDate, DataPerMonth, DataPerYear
from .models import DeviceDataPerHour, DeviceDataPerDate, DeviceDataPerMonth, DeviceDataPerYear
from .models import Device
from users.models import User
import datetime

# Path: app/source/ihiapp/csv.py

# # csvファイルを読み込む
# csv_file = open("../data.csv", "r", encoding="utf-8", errors="", newline="" )
# f = csv.DictReader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

# for data in f:
#     print(data)
    

#     # print(data['e1'])


# csvのデータからDataPerDate, DataPerMonth, DataPerYearを作成する関数
def create_data(data):

    # 日単位のデバイスの合計値
    data_e1_sum_by_D = data['e1'].resample('D').sum()
    data_e2_sum_by_D = data['e2'].resample('D').sum()
    data_e3_sum_by_D = data['e3'].resample('D').sum()
    data_w1_sum_by_D = data['w1'].resample('D').sum()
    data_w2_sum_by_D = data['w2'].resample('D').sum()
    data_w3_sum_by_D = data['w3'].resample('D').sum()
    data_f1_sum_by_D = data['f1'].resample('D').sum()
    data_f2_sum_by_D = data['f2'].resample('D').sum()
    data_f3_sum_by_D = data['f3'].resample('D').sum()

    # 日単位のデバイスの合計値の合計
    data_e1_sum_by_D = data_e1_sum_by_D + data_e2_sum_by_D + data_e3_sum_by_D
    data_w1_sum_by_D = data_w1_sum_by_D + data_w2_sum_by_D + data_w3_sum_by_D
    data_f1_sum_by_D = data_f1_sum_by_D + data_f2_sum_by_D + data_f3_sum_by_D

    # DataPerDateにデータを保存
    for i in range(len(data_e1_sum_by_D)): 
        filter = {
                'user_id': User.objects.get(email='ihi@bizfreak.co.jp'),
                'year': data_e1_sum_by_D.index[i].year,
                'month': data_e1_sum_by_D.index[i].month,
                'date': data_e1_sum_by_D.index[i].day,
            }
        filter['electrical_value'] = round(data_e1_sum_by_D[i], 2)
        filter['water_value'] = round(data_w1_sum_by_D[i], 2)
        filter['fuel_value'] = round(data_f1_sum_by_D[i], 2)

        DataPerDate.objects.create(**filter)
    
    # 月単位のデバイスの合計値
    data_e1_sum_by_M = data['e1'].resample('M').sum()
    data_e2_sum_by_M = data['e2'].resample('M').sum()
    data_e3_sum_by_M = data['e3'].resample('M').sum()
    data_w1_sum_by_M = data['w1'].resample('M').sum()
    data_w2_sum_by_M = data['w2'].resample('M').sum()
    data_w3_sum_by_M = data['w3'].resample('M').sum()
    data_f1_sum_by_M = data['f1'].resample('M').sum()
    data_f2_sum_by_M = data['f2'].resample('M').sum()
    data_f3_sum_by_M = data['f3'].resample('M').sum()

    # 月単位のデバイスの合計値の合計
    data_e1_sum_by_M = data_e1_sum_by_M + data_e2_sum_by_M + data_e3_sum_by_M
    data_w1_sum_by_M = data_w1_sum_by_M + data_w2_sum_by_M + data_w3_sum_by_M
    data_f1_sum_by_M = data_f1_sum_by_M + data_f2_sum_by_M + data_f3_sum_by_M

    # DataPerMonthにデータを保存
    for i in range(len(data_e1_sum_by_M)):
        filter = {
                'user_id': User.objects.get(email='ihi@bizfreak.co.jp'),
                'year': data_e1_sum_by_M.index[i].year,
                'month': data_e1_sum_by_M.index[i].month,
            }
        filter['electrical_value'] = round(data_e1_sum_by_M[i], 2)
        filter['water_value'] = round(data_w1_sum_by_M[i], 2)
        filter['fuel_value'] = round(data_f1_sum_by_M[i], 2)

        DataPerMonth.objects.create(**filter)

    # 年単位のデバイスの合計値
    data_e1_sum_by_Y = data['e1'].resample('Y').sum()
    data_e2_sum_by_Y = data['e2'].resample('Y').sum()
    data_e3_sum_by_Y = data['e3'].resample('Y').sum()
    data_w1_sum_by_Y = data['w1'].resample('Y').sum()
    data_w2_sum_by_Y = data['w2'].resample('Y').sum()
    data_w3_sum_by_Y = data['w3'].resample('Y').sum()
    data_f1_sum_by_Y = data['f1'].resample('Y').sum()
    data_f2_sum_by_Y = data['f2'].resample('Y').sum()
    data_f3_sum_by_Y = data['f3'].resample('Y').sum()

    # 年単位のデバイスの合計値の合計
    data_e1_sum_by_Y = data_e1_sum_by_Y + data_e2_sum_by_Y + data_e3_sum_by_Y
    data_w1_sum_by_Y = data_w1_sum_by_Y + data_w2_sum_by_Y + data_w3_sum_by_Y
    data_f1_sum_by_Y = data_f1_sum_by_Y + data_f2_sum_by_Y + data_f3_sum_by_Y

    # DataPerYearにデータを保存
    for i in range(len(data_e1_sum_by_Y)):
        filter = {
                'user_id': User.objects.get(email='ihi@bizfreak.co.jp'),
                'year': data_e1_sum_by_Y.index[i].year,
            }
        filter['electrical_value'] = round(data_e1_sum_by_Y[i], 2)
        filter['water_value'] = round(data_w1_sum_by_Y[i], 2)
        filter['fuel_value'] = round(data_f1_sum_by_Y[i], 2)

        DataPerYear.objects.create(**filter)   






# csvのデータからDeviceDataPerDate, DeviceDataPerMonth, DeviceDataPerYearを作成する関数
def create_device_data(data):

    # 日単位のデバイスの合計値
    data_e1_sum_by_D = data['e1'].resample('D').sum()
    data_e2_sum_by_D = data['e2'].resample('D').sum()
    data_e3_sum_by_D = data['e3'].resample('D').sum()
    data_w1_sum_by_D = data['w1'].resample('D').sum()
    data_w2_sum_by_D = data['w2'].resample('D').sum()
    data_w3_sum_by_D = data['w3'].resample('D').sum()
    data_f1_sum_by_D = data['f1'].resample('D').sum()
    data_f2_sum_by_D = data['f2'].resample('D').sum()
    data_f3_sum_by_D = data['f3'].resample('D').sum()

    data_device_list = [data_e1_sum_by_D, data_e2_sum_by_D, data_e3_sum_by_D, data_w1_sum_by_D, data_w2_sum_by_D, data_w3_sum_by_D, data_f1_sum_by_D, data_f2_sum_by_D, data_f3_sum_by_D]

    for data_device in data_device_list:
        for i in range(len(data_device)):
            filter = {
                'user_id': User.objects.get(email='ihi@bizfreak.co.jp'),
                'year': data_device.index[i].year,
                'month': data_device.index[i].month,
                'date': data_device.index[i].day,
            }
            if data_device.name == 'e1':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='36556270-141b-4ea3-ae4a-162af45c7d5c')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'e2':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='a3420464-973a-4844-af49-c6fda89f1662')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'e3':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='b4186c17-c20a-4f17-9fc7-1bfa81764021')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'w1':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='9a93992f-3da2-4fb4-9934-69bfd82cc9cf')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'w2':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='74b58cc9-b099-48f0-91cd-b404ee8e482b')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'w3':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='675ec302-1409-4c76-a02f-717136b303a5')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'f1':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='1df3c8e4-1868-4b12-9f98-f7c06ec34acf')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'f2':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='36f58cd0-da80-44e3-9737-ba0aab04bc38')
                DeviceDataPerDate.objects.create(**filter)
            elif data_device.name == 'f3':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='1fb01311-4254-422a-95a4-86f80552d20c')
                DeviceDataPerDate.objects.create(**filter)
            

    # 月単位のデバイスの合計値の合計
    data_e1_sum_by_M = data['e1'].resample('M').sum()
    data_e2_sum_by_M = data['e2'].resample('M').sum()
    data_e3_sum_by_M = data['e3'].resample('M').sum()
    data_w1_sum_by_M = data['w1'].resample('M').sum()
    data_w2_sum_by_M = data['w2'].resample('M').sum()
    data_w3_sum_by_M = data['w3'].resample('M').sum()
    data_f1_sum_by_M = data['f1'].resample('M').sum()
    data_f2_sum_by_M = data['f2'].resample('M').sum()
    data_f3_sum_by_M = data['f3'].resample('M').sum()

    data_device_list = [data_e1_sum_by_M, data_e2_sum_by_M, data_e3_sum_by_M, data_w1_sum_by_M, data_w2_sum_by_M, data_w3_sum_by_M, data_f1_sum_by_M, data_f2_sum_by_M, data_f3_sum_by_M]

    for data_device in data_device_list:
        for i in range(len(data_device)):
            filter = {
                'user_id': User.objects.get(email='ihi@bizfreak.co.jp'),
                'year': data_device.index[i].year,
                'month': data_device.index[i].month,
            }
            if data_device.name == 'e1':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='36556270-141b-4ea3-ae4a-162af45c7d5c')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'e2':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='a3420464-973a-4844-af49-c6fda89f1662')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'e3':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='b4186c17-c20a-4f17-9fc7-1bfa81764021')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'w1':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='9a93992f-3da2-4fb4-9934-69bfd82cc9cf')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'w2':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='74b58cc9-b099-48f0-91cd-b404ee8e482b')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'w3':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='675ec302-1409-4c76-a02f-717136b303a5')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'f1':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='1df3c8e4-1868-4b12-9f98-f7c06ec34acf')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'f2':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='36f58cd0-da80-44e3-9737-ba0aab04bc38')
                DeviceDataPerMonth.objects.create(**filter)
            elif data_device.name == 'f3':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='1fb01311-4254-422a-95a4-86f80552d20c')
                DeviceDataPerMonth.objects.create(**filter)

    # 年単位のデバイスの合計値の合計
    data_e1_sum_by_Y = data['e1'].resample('Y').sum()
    data_e2_sum_by_Y = data['e2'].resample('Y').sum()
    data_e3_sum_by_Y = data['e3'].resample('Y').sum()
    data_w1_sum_by_Y = data['w1'].resample('Y').sum()
    data_w2_sum_by_Y = data['w2'].resample('Y').sum()
    data_w3_sum_by_Y = data['w3'].resample('Y').sum()
    data_f1_sum_by_Y = data['f1'].resample('Y').sum()
    data_f2_sum_by_Y = data['f2'].resample('Y').sum()
    data_f3_sum_by_Y = data['f3'].resample('Y').sum()

    data_device_list = [data_e1_sum_by_Y, data_e2_sum_by_Y, data_e3_sum_by_Y, data_w1_sum_by_Y, data_w2_sum_by_Y, data_w3_sum_by_Y, data_f1_sum_by_Y, data_f2_sum_by_Y, data_f3_sum_by_Y]
    
    for data_device in data_device_list:
        for i in range(len(data_device)):
            filter = {
                'user_id': User.objects.get(email='ihi@bizfreak.co.jp'),
                'year': data_device.index[i].year,
            }
            if data_device.name == 'e1':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='36556270-141b-4ea3-ae4a-162af45c7d5c')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'e2':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='a3420464-973a-4844-af49-c6fda89f1662')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'e3':
                filter['electrical_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='b4186c17-c20a-4f17-9fc7-1bfa81764021')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'w1':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='9a93992f-3da2-4fb4-9934-69bfd82cc9cf')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'w2':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='74b58cc9-b099-48f0-91cd-b404ee8e482b')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'w3':
                filter['water_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='675ec302-1409-4c76-a02f-717136b303a5')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'f1':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='1df3c8e4-1868-4b12-9f98-f7c06ec34acf')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'f2':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='36f58cd0-da80-44e3-9737-ba0aab04bc38')
                DeviceDataPerYear.objects.create(**filter)
            elif data_device.name == 'f3':
                filter['fuel_value'] = round(data_device[i], 2)
                filter['device_id'] = Device.objects.get(id='1fb01311-4254-422a-95a4-86f80552d20c')
                DeviceDataPerYear.objects.create(**filter)










def import_csv():
    data = pd.read_csv('./data.csv', encoding='utf-8', index_col='日時', parse_dates=True)
    # print(data)
    # print(data.index)

    # print(data['e1'])

    # print(len(data))
    # data_colums = data.columns.values

    print(data['e1'].sum())

    
    create_data(data)
    # create_device_data(data)


    


    # for date in date_list:
    #     # date_listの日付とdataの日付が一致するものをすべて取得
    #     data_per_date = data[data.index
    #     print(data_per_date)

    #     # print(date)


    # for i in range(len(data)):
    #     print(data.index[i], data['e1'][i])
    #     for column in data_colums:
    #         filter = {
    #             'user_id': User.objects.get(email='ihi@bizfreak.co.jp'),
    #             'year': data.index[i].year,
    #             'month': data.index[i].month,
    #             'date': data.index[i].day,
    #             'hour': data.index[i].hour,
    #             'minute': data.index[i].minute,
    #         }
    #         # もしcolumnにeが含まれていたら、電気の値を代入
    #         if 'e' in column:
    #             # もしcに1が含まれていたら
    #             if '1' in column:
    #                 filter['electrical_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='36556270-141b-4ea3-ae4a-162af45c7d5c')
    #                 DeviceDataPerHour.objects.create(**filter)
    #             elif '2' in column:
    #                 filter['electrical_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='a3420464-973a-4844-af49-c6fda89f1662')
    #                 DeviceDataPerHour.objects.create(**filter)
    #             elif '3' in column:
    #                 filter['electrical_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='b4186c17-c20a-4f17-9fc7-1bfa81764021')
    #                 DeviceDataPerHour.objects.create(**filter)
    #         if 'w' in column: 
    #             if '1' in column:
    #                 filter['water_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='9a93992f-3da2-4fb4-9934-69bfd82cc9cf')
    #                 DeviceDataPerHour.objects.create(**filter)
    #             elif '2' in column:
    #                 filter['water_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='74b58cc9-b099-48f0-91cd-b404ee8e482b')
    #                 DeviceDataPerHour.objects.create(**filter)
    #             elif '3' in column:
    #                 filter['water_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='675ec302-1409-4c76-a02f-717136b303a5')
    #                 DeviceDataPerHour.objects.create(**filter)
    #         if 'f' in column:
 
    #             if '1' in column:
    #                 filter['fuel_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='1df3c8e4-1868-4b12-9f98-f7c06ec34acf')
    #                 DeviceDataPerHour.objects.create(**filter)
    #             elif '2' in column:
    #                 filter['fuel_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='36f58cd0-da80-44e3-9737-ba0aab04bc38')
    #                 DeviceDataPerHour.objects.create(**filter)
    #             elif '3' in column:
    #                 filter['fuel_value'] = data[column][i]
    #                 filter['device_id'] = Device.objects.get(id='1fb01311-4254-422a-95a4-86f80552d20c')
    #                 DeviceDataPerHour.objects.create(**filter)



                
    # for data in data:
    #     print(data)
        # print(data['e1'])
        # DeviceDataPerHour.objects.create(get_data_date=data, 
        # if DeviceDataPerHour.objects.filter(get_data_date=data).exists():
        #     print('exist')
        # else:
        #     pass

    


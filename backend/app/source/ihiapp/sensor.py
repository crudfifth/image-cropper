from unicodedata import east_asian_width
from django.core.management.base import BaseCommand
import requests
import json
import csv
import copy
import urllib
import pickle
import os
import statistics
from .models import floorEnvironment
from .models import areaEnvironment
from .models import toilets
from .models import areaCongestion
from .models import floorEnvironmentTargets
from .models import areaEnvironmentTargets
from .models import areaCongestionTargets
from .models import toiletTargets
from .models import congestionCamera
from .models import congestionCameraTargets
from config.settings import BASE_DIR

BUILD_ID = "101"
POST_TOKEN_URL = "https://www.connected-pf.com/auth/realms/cnpf/protocol/openid-connect/token"
POST_TOKEN_URL_KENSYO = "https://kensyo.connected-pf.com/auth/realms/cnpf/protocol/openid-connect/token"
GRANT_TYPE_AUTHCODE = "password"
APIURL_GET_MASTER = "https://www.connected-pf.com/v1/service/link/master_info"
APIURL_GET_Environment = "https://www.connected-pf.com/v1/service/link/environment"
APIURL_GET_Thermopile = "https://www.connected-pf.com/v1/service/link/thermopile"
APIURL_GET_Human = "https://www.connected-pf.com/v1/service/link/congestion_human_sensor"
APIURL_POST_TOILET = "https://www.connected-pf.com/v1/service/facility/toilet_use"
APIURL_GET_CAMERA = "https://www-e6k3t3r9.nsc-dc.net/catalog_data/param"
camera_access_token = "OO7RDqywrMwQBbEc8SSlrtg182y3r2gJFVVa5NjDiucl3DeHj38aKUSxePAao8p5llnScDAqtSTd4DqLHS4JClFOok69j3DCY7drK3kCCzlHSIOAFTytCxOO2dPN39hzJ54PQp1CabJ2IRzlk3TMnMBkdB3eX1wFbup0fE0lEZnoIkRIWYB3q651tSL08IIlpInoPu40nQ5moHgh3V4p32PMvSNWtuPFge2O1KEWEkiOrGrWhnczZCNFltqOQcMS2IjVnpxymDWSbOAtAux7KomGWFNBmKoTsC1wvG8LngVYoguS4Q0MwtA5BIeJk4LG9FAz36aLFecgWyhMFVr4oDESkojbAKcq2upYJ31xaFM9xVP0K7Q2xi0kwAI67AYJD30jxWS3yjLpJEmHc8Ix8mlQM5YwQiPQHJA9z5uofQ0Pbm3aKeDnDLdwWxzoCKq9sITvBt1fCHZbhlwjtmgfuHKeNsOMfBUHMdH4gJX6ruG4fWCB34cKUDoWO48HHUbG3Uk6NIGNZbYcFbiIFdyHFB1rhoXQeK6UzWUp59IEgB76aErKjbu0rHr2cierruz41anmhTDfkJGxyN7hogzRfFxQmgxKqjkNh0GRA3z5NuL6N68aaug6lh8mJEUqT9WeFlKJCO7g4fsudAp0JXLvXibs8tvxFCxO9gN5rBQb6RIaV0hs01XOEg8o1pkFZvlm6hU4IByDARTnwm39zUmZJIfQBxELZBlFQEeBL2jmmES3ZN8tAbePxr2NOnCoIlWqHmj8QanWc6OF2TV4P7kATKyi03c214do2CBUok1iIPlsM2PcPhG4MYzIIPLXbU4xRupbQGpX11YwCycZUNTHJtKh5AJ2WN6rh4hHTMaVyZwLMAE2pM0xWj0LyszJqUgWocQ8ns2phPVxQ2FjpfC7DUoJRzGFfBafwuekGxstLrueCrEbVyN9qbPNnnzjpVohS0tprGsA2YkrJr0ncLbntTXBVFggNSbcKfKczS7YqFVorta0MEYAjA90ZAmssg33"
access_token = ""
REQUEST_SUCCESS = 200

def get_access_token():
    param = {
    'grant_type'    : GRANT_TYPE_AUTHCODE,              	# authorization_code
    'client_id'     : 'wow_client',			# クライアントID
    'client_secret' : '11111111-2222-3333-4444-555555555555',# クライアントシークレット                   	# 認可コード
    'username'      : 'wow_service',
    'password'      : 'wow_service_2021',
    }
    # print(param)

    # URLをエンコード
    params = urllib.parse.urlencode(param)

    # headerでコンテンツタイプを指定
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url=POST_TOKEN_URL, data=params, headers=headers, timeout=5)

    print("Response Code: " + str(response.status_code))
    # 取得に成功していれば出力
    if response.status_code == REQUEST_SUCCESS:
        token_data = json.loads(response.text)
        # print(token_data)
        f = open(BASE_DIR + "/ihiapp/access_token.txt", "w")
        f.write(token_data["access_token"])
        f.close()

        return token_data["access_token"]

# access_token = get_access_token()


def get_kensyo_access_token():
    param = {
    'grant_type'    : GRANT_TYPE_AUTHCODE,
    'client_id'     : 'wow_client',	
    'client_secret' : '11111111-2222-3333-4444-555555555555',
    'username'      : 'wow_service',
    'password'      : 'wow_service_2021',
    }
    # print(param)

    # URLをエンコード
    params = urllib.parse.urlencode(param)

    # headerでコンテンツタイプを指定
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url=POST_TOKEN_URL_KENSYO, data=params, headers=headers, verify=False, timeout=5)

    print("Response Code: " + str(response.status_code))
    # 取得に成功していれば出力
    if response.status_code == REQUEST_SUCCESS:
        token_data = json.loads(response.text)
        # print(token_data)
        f = open(BASE_DIR + "/ihiapp/access_token.txt", "w")
        f.write(token_data["access_token"])
        f.close()

        return token_data["access_token"]


def get_master():
    param = {
        "builId": BUILD_ID,
        }
    
    
    header = {
        "Authorization": "Bearer " + access_token,
        }

    response = requests.get(APIURL_GET_MASTER, params=param, headers=header)
    print("Response Code: " + str(response.status_code))
    # 取得に成功していれば出力
    if response.status_code == REQUEST_SUCCESS:
        response_data = json.loads(response.text)
        return response_data

# 指定したfloor_idで統合PFから取得、フロア環境を更新
def update_floor_environment(target):
    print("----- This is FLOOR ENVIRONMENT -----")
    f = open(BASE_DIR + "/ihiapp/access_token.txt")
    access_token = f.read()
    # print(access_token)
    f.close()

    param = {
        "builId": BUILD_ID,
        "floorId": target,
        # "areaId" : "101B001001"
        }
    header = {
        "Authorization": "Bearer " + access_token,
        }
    try:
        response = requests.get(APIURL_GET_Environment, params=param, headers=header, verify=False, timeout=5)
        print("Response Code: " + str(response.status_code))
        # 取得に成功していれば出力
        if response.status_code == REQUEST_SUCCESS:

            # 更新対象の取得
            floor_environment =""
            try:
                floor_environment = floorEnvironment.objects.get(floor_environment_target__id=target.id)
                print("更新対象:",floor_environment)
            except:
                print("更新対象:なし")

            # レスポンスをjson(list)に変換してdata部分を取得
            response_data = json.loads(response.text)["data"]

            # dataが空かどうか判定
            if response_data:
                print(target,"のレスポンスがあります")

                print("すべてのセンサ:", response_data)
                print("取得センサ数:",len(response_data))

                all_sensor_data_list = {       
                    "temperature" : [],
                    "humidity" : [],
                    "ambientLight" : [],
                    "soundNoise" : [],
                    "pressure" : [],
                    "etvoc" : [],
                    "eco2" : [],
                    "discomfort" : [],
                    "heatStroke" : [],
                    "seismic" : []
                }

                for each_response_data in response_data:
                    for environment_key in all_sensor_data_list:
                        try:
                            all_sensor_data_list[environment_key].append(each_response_data["data"][0][environment_key])
                        except:
                            pass
                print("全てのセンサー取得値", all_sensor_data_list)
                    
                for environment_key in all_sensor_data_list:
                    try:
                        all_sensor_data_list[environment_key] = statistics.mean(all_sensor_data_list[environment_key])
                        all_sensor_data_list[environment_key] = round(all_sensor_data_list[environment_key], 2)
                    except:
                        all_sensor_data_list[environment_key] = 0

                print("平均センサー取得値", all_sensor_data_list)


                # 取得対象がfloor_environmentに存在するか確認
                if floor_environment:
                    print(target,"はfloor_environmentに存在します")
                    # 更新
                    try: 
                        a = floor_environment
                        a.temperature = all_sensor_data_list["temperature"]
                        a.humidity = all_sensor_data_list["humidity"]
                        a.ambient_light = all_sensor_data_list["ambientLight"]
                        a.sound_noise = all_sensor_data_list["soundNoise"]
                        a.pressure = all_sensor_data_list["pressure"]
                        a.etvoc = all_sensor_data_list["etvoc"]
                        a.eco2 = all_sensor_data_list["eco2"]
                        a.discomfort = all_sensor_data_list["discomfort"]
                        a.heat_stroke = all_sensor_data_list["heatStroke"]
                        a.seismic = all_sensor_data_list["seismic"]
                        a.save()
                    except:
                        print(target,"の更新に失敗")
                elif not floor_environment:
                    print(target,"は存在しません")
                    # 新規作成
                    try:
                        a = floorEnvironment(
                            floor_environment_target = target,
                            floor_id = target,
                            temperature = all_sensor_data_list["temperature"],
                            humidity = all_sensor_data_list["humidity"],
                            ambient_light = all_sensor_data_list["ambientLight"],
                            sound_noise = all_sensor_data_list["soundNoise"],
                            pressure = all_sensor_data_list["pressure"],
                            etvoc = all_sensor_data_list["etvoc"],
                            eco2 = all_sensor_data_list["eco2"],
                            discomfort = all_sensor_data_list["discomfort"],
                            heat_stroke = all_sensor_data_list["heatStroke"],
                            seismic = all_sensor_data_list["seismic"],
                            )
                        a.save()
                    except:
                        print(target,"の新規作成に失敗")
                
            else:
                print(target,"のレスポンスは空です")
                if not floor_environment:
                    # 新規作成
                    try:
                        a = floorEnvironment(
                            floor_environment_target = target,
                            floor_id = target,
                            temperature = "0",
                            humidity = "0",
                            ambient_light = "0",
                            sound_noise = "0",
                            pressure = "0",
                            etvoc = "0",
                            eco2 = "0",
                            discomfort = "0",
                            heat_stroke = "0",
                            seismic = "0",
                            )
                        a.save()
                    except:
                        print(target,"の新規作成に失敗")
        return response.status_code
    except:
        print("error")



# 指定したarea_idで統合PFから取得、フロア環境を更新
def update_area_environment(target):
    print("----- This is AREA ENVIRONMENT -----")
    f = open(BASE_DIR + "/ihiapp/access_token.txt")
    access_token = f.read()
    # print(access_token)
    f.close()

    param = {
        "builId": BUILD_ID,
        "areaId" : target,
        }
    header = {
        "Authorization": "Bearer " + access_token,
        }
    try:
        response = requests.get(APIURL_GET_Environment, params=param, headers=header, verify=False, timeout=5)
        print("Response Code: " + str(response.status_code))
        # 取得に成功していれば出力
        if response.status_code == REQUEST_SUCCESS:

            # 更新対象の取得
            area_environment =""
            try:
                area_environment = areaEnvironment.objects.get(area_environment_target__id=target.id)
                print("更新対象:",area_environment)
            except:
                print("更新対象:なし")

            # レスポンスをjson(list)に変換してdata部分を取得
            response_data = json.loads(response.text)["data"]

            # dataが空かどうか判定
            if response_data:
                print(target,"のレスポンスがあります")

                print("すべてのセンサ:", response_data)
                print("取得センサ数:",len(response_data))

                all_sensor_data_list = {       
                    "temperature" : [],
                    "humidity" : [],
                    "ambientLight" : [],
                    "soundNoise" : [],
                    "pressure" : [],
                    "etvoc" : [],
                    "eco2" : [],
                    "discomfort" : [],
                    "heatStroke" : [],
                    "seismic" : []
                }

                for each_response_data in response_data:
                    for environment_key in all_sensor_data_list:
                        try:
                            all_sensor_data_list[environment_key].append(each_response_data["data"][0][environment_key])
                        except:
                            pass
                print("全てのセンサー取得値", all_sensor_data_list)
                    
                for environment_key in all_sensor_data_list:
                    try:
                        all_sensor_data_list[environment_key] = statistics.mean(all_sensor_data_list[environment_key])
                        all_sensor_data_list[environment_key] = round(all_sensor_data_list[environment_key], 2)
                    except:
                        all_sensor_data_list[environment_key] = 0

                print("平均センサー取得値", all_sensor_data_list)


                # 取得対象がarea_environmentに存在するか確認
                if area_environment:
                    print(target,"はarea_environmentに存在します")
                    # 更新
                    try: 
                        a = area_environment
                        a.temperature = all_sensor_data_list["temperature"]
                        a.humidity = all_sensor_data_list["humidity"]
                        a.ambient_light = all_sensor_data_list["ambientLight"]
                        a.sound_noise = all_sensor_data_list["soundNoise"]
                        a.pressure = all_sensor_data_list["pressure"]
                        a.etvoc = all_sensor_data_list["etvoc"]
                        a.eco2 = all_sensor_data_list["eco2"]
                        a.discomfort = all_sensor_data_list["discomfort"]
                        a.heat_stroke = all_sensor_data_list["heatStroke"]
                        a.seismic = all_sensor_data_list["seismic"]
                        a.save()
                    except:
                        print(target,"の更新に失敗")
                elif not area_environment:
                    print(target,"は存在しません")
                    # 新規作成
                    try:
                        a = areaEnvironment(
                            area_environment_target = target,
                            area_id = target,
                            temperature = all_sensor_data_list["temperature"],
                            humidity = all_sensor_data_list["humidity"],
                            ambient_light = all_sensor_data_list["ambientLight"],
                            sound_noise = all_sensor_data_list["soundNoise"],
                            pressure = all_sensor_data_list["pressure"],
                            etvoc = all_sensor_data_list["etvoc"],
                            eco2 = all_sensor_data_list["eco2"],
                            discomfort = all_sensor_data_list["discomfort"],
                            heat_stroke = all_sensor_data_list["heatStroke"],
                            seismic = all_sensor_data_list["seismic"],
                            )
                        a.save()
                    except:
                        print(target,"の新規作成に失敗")
                
            else:
                print(target,"のレスポンスは空です")
                if not area_environment:
                    # 新規作成
                    try:
                        a = areaEnvironment(
                            area_environment_target = target,
                            area_id = target,
                            temperature = "0",
                            humidity = "0",
                            ambient_light = "0",
                            sound_noise = "0",
                            pressure = "0",
                            etvoc = "0",
                            eco2 = "0",
                            discomfort = "0",
                            heat_stroke = "0",
                            seismic = "0",
                            )
                        a.save()
                    except:
                        print(target,"の新規作成に失敗")
        return response.status_code
    except:
        print("error")



# 指定したarea_idで統合PFから取得、フロア環境を更新
def update_area_congestion(target):
    print("----- This is AREA CONGESTION -----")
    f = open(BASE_DIR + "/ihiapp/access_token.txt")
    access_token = f.read()
    # print(access_token)
    f.close()
    
    header = {
        "Authorization": "Bearer " + access_token,
        }
    # サーモパイルセンサか着座センサかによって処理変更
    if (target.is_seating_sensor == False):
        param = {
        "builId": BUILD_ID,
        "areaId" : target,
        }
        try: 
            response = requests.get(APIURL_GET_Thermopile, params=param, headers=header, verify=False, timeout=5)
            print("Response Code: " + str(response.status_code))
            # 取得に成功していれば出力
            if response.status_code == REQUEST_SUCCESS:

                # 更新対象の取得
                area_congestion =""
                try:
                    area_congestion = areaCongestion.objects.get(area_congestion_target__id=target.id)
                    print("更新対象:",area_congestion)
                except:
                    print("更新対象:なし")

                # レスポンスをjson(list)に変換してdata部分を取得
                response_data = json.loads(response.text)["data"]

                # dataが空かどうか判定
                if response_data:
                    print(target,"のレスポンスがあります")

                    print("取得センサ数:",len(response_data[0]))
                    
                    human_counts = []
                    for each_response_data in response_data:
                        human_counts.append(each_response_data["countData"][0]["human_count"])
                    total_human_count = sum(human_counts)
                    print("全てのセンサー取得値", human_counts)
                    print("合計値", total_human_count)


                    # 取得対象がarea_congestionに存在するか確認
                    if area_congestion:
                        print(target,"はarea_congestionに存在します")
                        # 更新
                        try: 
                            a = area_congestion
                            a.human_count = total_human_count
                            a.degree_of_congestion = total_human_count / target.max_human
                            a.save()
                        except:
                            print(target,"の更新に失敗")
                    elif not area_congestion:
                        print(target,"は存在しません")
                        # 新規作成
                        try:
                            a = areaCongestion(
                                area_congestion_target = target,
                                area_id = target.area_id,
                                human_count = total_human_count,
                                degree_of_congestion = total_human_count / target.max_human,
                                )
                            a.save()
                        except:
                            print(target,"の新規作成に失敗")
                    
                else:
                    print(target,"のレスポンスは空です")
                    if not area_congestion:
                        # 新規作成
                        try:
                            a = areaCongestion(
                                area_congestion_target = target,
                                area_id = target.area_id,
                                human_count = 0,
                                degree_of_congestion = 0.0,
                                )
                            a.save()
                        except:
                            print(target,"の新規作成に失敗")
            return response.status_code
        except:
            print("error")
    else:
        print("----- Seating Sensor -----")
        param = {
        "builId": BUILD_ID,
        "areaId" : target,
        "userId" : "wow_client"
        }
        try: 
            response = requests.get(APIURL_GET_Human, params=param, headers=header, verify=False, timeout=5)
            print("Response Code: " + str(response.status_code))
            # 取得に成功していれば出力
            if response.status_code == REQUEST_SUCCESS:

                # 更新対象の取得
                area_congestion =""
                try:
                    area_congestion = areaCongestion.objects.get(area_congestion_target__id=target.id)
                    print("更新対象:",area_congestion)
                except:
                    print("更新対象:なし")

                # レスポンスをjson(list)に変換してdata部分を取得
                response_data = json.loads(response.text)["data"]

                # dataが空かどうか判定
                if response_data:
                    print(target,"のレスポンスがあります")

                    print("取得センサ数:",len(response_data))
                    
                    human_counts = []
                    for each_response_data in response_data:
                        if each_response_data["data"][0]["count"] == 0:
                            human_counts.append(0)
                        elif each_response_data["data"][0]["count"] >= 1:
                            human_counts.append(1)
                    total_human_count = sum(human_counts)
                    print("全てのセンサー取得値", human_counts)
                    print("合計値", total_human_count)


                    # 取得対象がarea_congestionに存在するか確認
                    if area_congestion:
                        print(target,"はarea_congestionに存在します")
                        # 更新
                        try: 
                            a = area_congestion
                            a.human_count = total_human_count
                            a.degree_of_congestion = total_human_count / target.max_human
                            a.save()
                        except:
                            print(target,"の更新に失敗")
                    elif not area_congestion:
                        print(target,"は存在しません")
                        # 新規作成
                        try:
                            a = areaCongestion(
                                area_congestion_target = target,
                                area_id = target.area_id,
                                human_count = total_human_count,
                                degree_of_congestion = total_human_count / target.max_human,
                                )
                            a.save()
                        except:
                            print(target,"の新規作成に失敗")
                    
                else:
                    print(target,"のレスポンスは空です")
                    if not area_congestion:
                        # 新規作成
                        try:
                            a = areaCongestion(
                                area_congestion_target = target,
                                area_id = target.area_id,
                                human_count = 0,
                                degree_of_congestion = 0.0,
                                )
                            a.save()
                        except:
                            print(target,"の新規作成に失敗")
            return response.status_code
        except:
            print("error")





def update_toilet(target, toilet_id):
    print("----- This is Toilet -----")
    f = open(BASE_DIR + "/ihiapp/access_token.txt")
    access_token = f.read()
    # print(access_token)
    f.close()
    toiletId_list = []
    toiletId_list.append(toilet_id)
    print(toiletId_list)
    param = {
        "builId": BUILD_ID,
        "toiletId_list" : toiletId_list,
        }
    headers = {
        "Content-Type": "application/json", 
        "Connection": "keep-alive",
        "Authorization": "Bearer " + access_token,
        }
    try:
        response = requests.post(url=APIURL_POST_TOILET, data=json.dumps(param), headers=headers, verify=False, timeout=5)
        print("Response Code: " + str(response.status_code))
        # 取得に成功していれば出力
        if response.status_code == REQUEST_SUCCESS:

            toilet =""
            try:
                toilet_list = toilets.objects.filter(toilet_target__id=target.id)
                toilet = toilet_list.get(toilet_id=toilet_id)
                print("更新対象:",toilet)
            except:
                print("更新対象:なし")

            response_data =  json.loads(response.text)
            # print(response_data)

            # dataが空かどうか判定
            if response_data["data_info"] != None :
                print(toilet,"のレスポンスがあります")

                sensor_data = response_data["data_info"]["toilet_list"][0]
                print("取得値:", sensor_data)


                # 取得対象がtoiletに存在するか確認
                if toilet:
                    print(toilet_id,"はtoiletに存在します")
                    # 更新
                    try: 
                        a = toilet
                        a.number_of_boxes = sensor_data["numberOfBoxes"]
                        a.number_of_occupied_boxes = sensor_data["status_info"]["numberOfOccupiedBoxes"]
                        a.toilet_nm = sensor_data["toiletNm"]
                        a.publishing = sensor_data["publishing"]
                        a.gender = sensor_data["gender"]
                        a.is_multi_purpose = sensor_data["isMultiPurpose"]
                        a.save()
                    except:
                        print(toilet_id,"の更新に失敗")
                elif not toilet:
                    print(toilet_id,"は存在しません")
                    # 新規作成
                    try:
                        a = toilets(
                            toilet_target = target,
                            floor_id = target.floor_id,
                            toilet_id = str(toilet_id),
                            number_of_boxes = sensor_data["numberOfBoxes"],
                            number_of_occupied_boxes = sensor_data["status_info"]["numberOfOccupiedBoxes"],
                            toilet_nm = sensor_data["toiletNm"],
                            publishing = sensor_data["publishing"],
                            gender = sensor_data["gender"],
                            is_multi_purpose = sensor_data["isMultiPurpose"],
                            )
                        a.save()
                    except:
                        print(target,"の新規作成に失敗")
                
            else:
                print(toilet_id,"のレスポンスは空です")
                if not toilet:
                    # 新規作成
                    try:
                        a = toilets(
                            toilet_target = target,
                            floor_id = target.floor_id,
                            toilet_id = str(toilet_id),
                            number_of_boxes = "0",
                            number_of_occupied_boxes = "0",
                            toilet_nm = "0",
                            publishing = "0",
                            gender = "0",
                            is_multi_purpose = "0",
                            )
                        a.save()
                    except:
                        print(toilet_id,"の新規作成に失敗")
        return response.status_code
    except:
        print("error")


def update_toilet_all(toiletId_list):
    print("----- This is Toilet -----")
    f = open(BASE_DIR + "/ihiapp/access_token.txt")
    access_token = f.read()
    # print(access_token)
    f.close()

    param = {
        "builId": BUILD_ID,
        "toiletId_list" : toiletId_list,
        }
    headers = {
        "Content-Type": "application/json", 
        "Connection": "keep-alive",
        "Authorization": "Bearer " + access_token,
        }
    try:
        response = requests.post(url=APIURL_POST_TOILET, data=json.dumps(param), headers=headers, verify=False, timeout=15)
        print("Response Code: " + str(response.status_code))
        # 取得に成功していれば出力
        if response.status_code == REQUEST_SUCCESS:

            response_data =  json.loads(response.text)

            # dataが空かどうか判定
            if response_data["data_info"] != None :
                # print(toilet,"のレスポンスがあります")
                sensor_data_list = response_data["data_info"]["toilet_list"]
                print("Number of sensor data:", len(sensor_data_list))

                # toildIdに紐づくトイレの各レスポンスデータをDictで紐付け
                sensor_data_dict = dict()
                for each_sensor_data in sensor_data_list:
                    sensor_data_dict[each_sensor_data["toiletId"]] = each_sensor_data
                # print(sensor_data_dict)


                toilet_targets = toiletTargets.objects.all()
                for target in toilet_targets:
                    for toilet_id in target.toilet_id_list:
                        if toilet_id in sensor_data_dict:

                            toilet =""
                            try:
                                toilet_list = toilets.objects.filter(toilet_target__id=target.id)
                                toilet = toilet_list.get(toilet_id=toilet_id)
                                print("更新対象:",toilet)
                            except:
                                print("更新対象:なし")
                            
                            # 取得対象がtoiletに存在するか確認
                            if toilet:
                                print(toilet_id,"はtoiletに存在します")
                                # 更新
                                try: 
                                    a = toilet
                                    a.number_of_boxes = sensor_data_dict[toilet_id]["numberOfBoxes"]
                                    a.number_of_occupied_boxes = sensor_data_dict[toilet_id]["status_info"]["numberOfOccupiedBoxes"]
                                    a.toilet_nm = sensor_data_dict[toilet_id]["toiletNm"]
                                    a.publishing = sensor_data_dict[toilet_id]["publishing"]
                                    a.gender = sensor_data_dict[toilet_id]["gender"]
                                    a.is_multi_purpose = sensor_data_dict[toilet_id]["isMultiPurpose"]
                                    a.save()
                                except:
                                    print(toilet_id,"の更新に失敗")
                            elif not toilet:
                                print(toilet_id,"は存在しません")
                                # 新規作成
                                try:
                                    a = toilets(
                                        toilet_target = target,
                                        floor_id = target.floor_id,
                                        toilet_id = str(toilet_id),
                                        number_of_boxes = sensor_data_dict[toilet_id]["numberOfBoxes"],
                                        number_of_occupied_boxes = sensor_data_dict[toilet_id]["status_info"]["numberOfOccupiedBoxes"],
                                        toilet_nm = sensor_data_dict[toilet_id]["toiletNm"],
                                        publishing = sensor_data_dict[toilet_id]["publishing"],
                                        gender = sensor_data_dict[toilet_id]["gender"],
                                        is_multi_purpose = sensor_data_dict[toilet_id]["isMultiPurpose"],
                                        )
                                    a.save()
                                except:
                                    print(target,"の新規作成に失敗")
                            
                        else:
                            print(toilet_id,"のレスポンスは空です")
                            if not toilet:
                                # 新規作成
                                try:
                                    a = toilets(
                                        toilet_target = target,
                                        floor_id = target.floor_id,
                                        toilet_id = str(toilet_id),
                                        number_of_boxes = "0",
                                        number_of_occupied_boxes = "0",
                                        toilet_nm = "0",
                                        publishing = "0",
                                        gender = "0",
                                        is_multi_purpose = "0",
                                        )
                                    a.save()
                                except:
                                    print(toilet_id,"の新規作成に失敗")
        return response.status_code
    except:
        print("error")

# 指定したfloor_idで統合PFから取得、フロア環境を更新
def update_camera(target):
    print("----- This is CAMERA -----")
    param = {
        "access_token": camera_access_token,
        "catalog_id" : "1640598771741ik0d4rglp27z",
        "resourceId" : target,
        "recent" : "true",
        }
    try:
        response = requests.get(APIURL_GET_CAMERA, params=param, timeout=5)
        print("Response Code: " + str(response.status_code))
        # 取得に成功していれば出力
        if response.status_code == REQUEST_SUCCESS:
            # レスポンスをjson(list)に変換してdata部分を取得

            # 更新対象の取得
            congestion_camera =""
            try:
                congestion_camera = congestionCamera.objects.get(congestion_camera_target__id=target.id)
                print("更新対象:",congestion_camera)
            except:
                print("更新対象:なし")
            print(target.id)

            response_data = json.loads(response.text)["data"]
            # dataが空かどうか判定
            if response_data:
                print(target,"のレスポンスがあります")

                print("取得カメラ:",response_data[0]["m2m"]["resourceId"])
                print("取得カメラ数:",len(response_data[0]["m2m"]['childResource']))
                sensor_data = response_data[0]["m2m"]["childResource"][0]
                # print("取得値:", sensor_data)


                # 取得対象リストがfloor_environmentに存在するか確認
                if congestion_camera:
                    print(target,"はcongestion_cameraに存在します")
                    # 更新
                    try: 
                        a = congestion_camera
                        a.image = sensor_data["image"]
                        a.save()
                    except:
                        print(target,"の更新に失敗")
                elif not congestion_camera:
                    print(target,"は存在しません")
                    # 新規作成
                    try:
                        a = congestionCamera(
                            congestion_camera_target = target,
                            resource_id = target,
                            floor_no = target.floor_no,
                            image = sensor_data["image"],
                            )
                        a.save()
                    except:
                        print(target,"の新規作成に失敗")
                
            else:
                print(target,"のレスポンスは空です")
                if not congestion_camera:
                    try:
                        a = congestionCamera(
                            congestion_camera_target = target,
                            resource_id = target,
                            floor_no = target.floor_no,
                            image = "0",
                            )
                        a.save()
                    except:
                        print(target,"の新規作成に失敗")
                
                
        return response.status_code
    except:
        print("error")



















def floor_environment(mode, value=None):
# update or create  floor_environment table
    if(mode == "all"):
        floor_environment_targets = floorEnvironmentTargets.objects.all()
        for target in floor_environment_targets:
            print("-----------------")
            print("取得対象",target)
            update_floor_environment(target)
    else: 
        floor_environment_targets = floorEnvironmentTargets.objects.get(floor_id = value)
        print("取得対象:",floor_environment_targets)
        update_floor_environment(floor_environment_targets)

def area_environment(mode, value=None):
# update or create  floor_environment table
    if(mode == "all"):
        area_environment_targets = areaEnvironmentTargets.objects.all()
        for target in area_environment_targets:
            print("-----------------")
            print("取得対象",target)
            update_area_environment(target)
    else: 
        area_environment_targets = areaEnvironmentTargets.objects.get(area_id = value)
        print("取得対象:",area_environment_targets)
        update_area_environment(area_environment_targets)


def area_congestion(mode, value=None):
# update or create  area_congestion table

    # # マスターから全エリアIDを取得(最大人数取得のため)
    # master = get_master()
    # master_areas = master["masterInfos"]["areas"]
    # master_area_ids = {}
    # print(len(master_areas))
    # for x in range(len(master_areas)):
    #     # print(x)
    #     # print(master_areas[x]['id'])
    #     master_area_ids[master_areas[x]['id']] = x
    # print(master_area_ids)

    if(mode == "all"):
        area_congestion_targets = areaCongestionTargets.objects.all()
        for target in area_congestion_targets:
            # # 取得対象のエリアがマスターに存在する場合は最大人数の更新
            # if target.area_id in master_area_ids:
            #     # print("id",master_area_ids[target.area_id])
            #     max_human = master_areas[master_area_ids[target.area_id]]['max']
            #     print("最大人数:", max_human)
            #     target.max_human = max_human
            #     target.save()
                
            print("-----------------")
            print("取得対象",target)
            update_area_congestion(target)
    else: 
        area_congestion_targets = areaCongestionTargets.objects.get(area_id = value)
        # if area_congestion_targets.area_id in master_area_ids:
        #     max_human = master_areas[master_area_ids[area_congestion_targets.area_id]]['max']
        #     print("最大人数:", max_human)
        #     area_congestion_targets.max_human = max_human
        #     area_congestion_targets.save()
                
        print("取得対象:",area_congestion_targets)
        update_area_congestion(area_congestion_targets)

def toilet(mode, value=None):
# update or create  floor_environment table
    # kensyo_access_token = get_kensyo_access_token()
    if(mode == "all"):
        toilet_targets = toiletTargets.objects.all()
        for target in toilet_targets:
            for toilet_id in target.toilet_id_list:
                print("-----------------")
                print("取得対象",toilet_id)
                update_toilet(target, toilet_id)

    elif(mode == "newall"):
        toilet_targets = toiletTargets.objects.all()
        toiletId_list = []
        for target in toilet_targets:
            for toilet_id in target.toilet_id_list:
                toiletId_list.append(toilet_id)
        update_toilet_all(toiletId_list)
        
    else: 
        toilet_targets = toiletTargets.objects.get(floor_id = value)
        for toilet_id in toilet_targets.toilet_id_list:
            print("取得対象:", toilet_id)
            update_toilet(toilet_targets, toilet_id)


def congestion_camera(mode, value=None):
    if(mode == "all"):
        congestion_cameera_targets = congestionCameraTargets.objects.all()
        for target in congestion_cameera_targets:
            print("-----------------")
            print("取得対象:",target)
            update_camera(target)
    else:
        congestion_cameera_targets = congestionCameraTargets.objects.get(resource_id = value)
        print("取得対象:",congestion_cameera_targets)
        update_camera(congestion_cameera_targets)


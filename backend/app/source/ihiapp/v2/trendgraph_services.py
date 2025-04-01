import datetime
import calendar
import logging

from sympy import parse_expr, symbols

from django.db.models import (F, OuterRef, Subquery)

from ..constants import (DATA_TYPE_ELECTRICITY)
from ..models import Data, ChannelAdapter, AnnualPlanValues, DailyEconomicActivityAmount

from .utils import get_graph_setting

def get_graph_data_seq_minutes(company_id, data_type, mode, year, month, date, hour, minute):
    """
    指定された日時から4時間分の時系列データを取得する。

    この関数は、指定された企業IDに基づいて、特定の日時から4時間後までの電力データを集計し、
    トレンドグラフに表示するためのデータを生成します。

    Parameters:
    - company_id (int): 時系列データを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード = intensity
    - year (int): 開始年。
    - month (int): 開始月。
    - date (int): 開始日。
    - hour (int): 開始時。
    - minute (int): 開始分。

    Returns:
    - list: 各グラフに対する時系列データのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 指定時刻から範囲を指定
    start_ymd_hm = datetime.datetime(int(year), int(month), int(date), int(hour), int(minute), 0)
    end_ymd_hm = start_ymd_hm + datetime.timedelta(hours=4)

    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    result_list_all = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            result_list = []
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE, get_data_at__date__gte=gateway_startdate).order_by('get_data_at')
            else:
                data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE).order_by('get_data_at')

            if start_ymd_hm is not None and end_ymd_hm is not None:
                data_per_minute = data_per_minute.filter(get_data_at__range=(start_ymd_hm, end_ymd_hm))

            aggregated_data = data_per_minute.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'get_data_at__second'
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            )

            result_list = list_chdate(aggregated_data, data_type, Data.DateType.MINUTE, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)

        result = {
            'no' : graph_adapter.channel_no,
            'name' : graph_adapter.channel_name,
            'data' : result_list
        }
        result_list_all.append(result)

    return result_list_all


def get_graph_data_seq_hours(company_id, data_type, mode, year, month, date, start, end):
    """
    指定された日付における、特定の時間範囲内の時系列データを取得する。

    この関数は、指定された企業IDに基づいて、特定の日付と時間範囲（開始時刻から終了時刻）における電力データを集計し、
    トレンドグラフに表示するためのデータを生成します。

    Parameters:
    - company_id (int): 時系列データを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード（例：'intensity'など）。
    - year (int): 対象年。
    - month (int): 対象月。
    - date (int): 対象日。
    - start (int): 集計を開始する時間。
    - end (int): 集計を終了する時間。

    Returns:
    - list: 各グラフに対する時系列データのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    result_list_all = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            result_list = []
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR, get_data_at__date__gte=gateway_startdate).order_by('get_data_at')
            else:
                data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR).order_by('get_data_at')

            if year is not None and month is not None and date is not None:
                data_per_hour = data_per_hour.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date)
                if start is not None and end is not None:
                    data_per_hour = data_per_hour.filter(get_data_at__time__range=(int(start), int(end)))

            aggregated_data = data_per_hour.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            )

            result_list = list_chdate(aggregated_data, data_type, Data.DateType.HOUR, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)

        result = {
            'no' : graph_adapter.channel_no,
            'name' : graph_adapter.channel_name,
            'data' : result_list
        }
        result_list_all.append(result)

    return result_list_all


def get_graph_data_seq_days(company_id, data_type, mode, year, month, start, end, week):
    """
    指定された期間（日単位）における時系列データを取得する。

    この関数は、指定された企業IDに基づいて、特定の年、月、週（オプション）、および日の範囲における電力データを集計し、
    トレンドグラフに表示するためのデータを生成します。

    Parameters:
    - company_id (int): 時系列データを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード（例：'intensity'など）。
    - year (int): 対象年。
    - month (int): 対象月。
    - start (int): 集計を開始する日。
    - end (int): 集計を終了する日。
    - week (int, optional): 対象週。指定すると、その週の範囲内でデータを集計します。Noneの場合は月全体が対象になります。

    Returns:
    - list: 各グラフに対する時系列データのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    result_list_all = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            result_list = []
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE, get_data_at__date__gte=gateway_startdate).order_by('get_data_at')
            else:
                data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE).order_by('get_data_at')

            if year is not None and month is not None:
                if week is None:
                    data_per_date = data_per_date.filter(get_data_at__year=year, get_data_at__month=month)
                else:
                    first_date, last_date = get_week_range(int(year), int(month), int(week))
                    data_per_date = data_per_date.filter(get_data_at__range=(first_date, last_date))
                if start is not None and end is not None:
                    data_per_date = data_per_date.filter(get_data_at__day__range=(int(start), int(end)))

            aggregated_data = data_per_date.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute',
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            )

            result_list = list_chdate(aggregated_data, data_type, Data.DateType.DATE, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)
        result = {
            'no' : graph_adapter.channel_no,
            'name' : graph_adapter.channel_name,
            'data' : result_list
        }
        result_list_all.append(result)

    return result_list_all


def get_graph_data_latest_minutes(company_id, data_type, mode, year, month, date, hour, minute):
    """
    指定された日時から4時間分の時系列データを取得しその最後の値を取り出す

    この関数は、指定された企業IDに基づいて、特定の日時から4時間後までの電力データのうち最後の値を取り出し、
    最新データ一覧に表示するためのデータを生成します。

    Parameters:
    - company_id (int): 時系列データを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード = intensity
    - year (int): 開始年。
    - month (int): 開始月。
    - date (int): 開始日。
    - hour (int): 開始時。
    - minute (int): 開始分。

    Returns:
    - list: 各グラフに対するデータのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 指定時刻から範囲を指定
    start_ymd_hm = datetime.datetime(int(year), int(month), int(date), int(hour), int(minute), 0)
    end_ymd_hm = start_ymd_hm + datetime.timedelta(hours=4)

    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    result_list_all = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            chdata = {
                'value': 0.0,
            }
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE, get_data_at__date__gte=gateway_startdate).order_by('-get_data_at')
            else:
                data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE).order_by('-get_data_at')

            if start_ymd_hm is not None and end_ymd_hm is not None:
                data_per_minute = data_per_minute.filter(get_data_at__range=(start_ymd_hm, end_ymd_hm))

            one_data = data_per_minute.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'get_data_at__second'
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            ).first()

            chdata = get_chdate(one_data, data_type, Data.DateType.MINUTE, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)

        result = {
            'no' : graph_adapter.channel_no,
            'name' : graph_adapter.channel_name,
            'data' : chdata
        }
        result_list_all.append(result)

    return result_list_all


def get_graph_data_latest_hours(company_id, data_type, mode, year, month, date, start, end):
    """
    指定された日付における、特定の時間範囲内の時系列データを取得しその最後の値を取り出す

    この関数は、指定された企業IDに基づいて、特定の日付と時間範囲（開始時刻から終了時刻）における電力データのうち最後の値を取り出し、
    最新データ一覧に表示するためのデータを生成します。

    Parameters:
    - company_id (int): トレンドグラフデータを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード（例：'intensity'など）。
    - year (int): 対象年。
    - month (int): 対象月。
    - date (int): 対象日。
    - start (int): 集計を開始する時間。
    - end (int): 集計を終了する時間。

    Returns:
    - list: 各グラフに対するデータのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    result_list_all = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            chdata = {
                'value': 0.0,
            }
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR, get_data_at__date__gte=gateway_startdate).order_by('-get_data_at')
            else:
                data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR).order_by('-get_data_at')

            if year is not None and month is not None and date is not None:
                data_per_hour = data_per_hour.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date)
                if start is not None and end is not None:
                    data_per_hour = data_per_hour.filter(get_data_at__time__range=(int(start), int(end)))

            one_data = data_per_hour.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            ).first()

            chdata = get_chdate(one_data, data_type, Data.DateType.HOUR, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)

        result = {
            'no' : graph_adapter.channel_no,
            'name' : graph_adapter.channel_name,
            'data' : chdata
        }
        result_list_all.append(result)

    return result_list_all


def get_graph_data_latest_days(company_id, data_type, mode, year, month, start, end, week):
    """
    指定された期間（日単位）における時系列データを取得しその最後の値を取り出す

    この関数は、指定された企業IDに基づいて、特定の年、月、週（オプション）、および日の範囲における電力データのうち最後の値を取り出し、
    最新データ一覧に表示するためのデータを生成します。

    Parameters:
    - company_id (int): トレンドグラフデータを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード（例：'intensity'など）。
    - year (int): 対象年。
    - month (int): 対象月。
    - start (int): 集計を開始する日。
    - end (int): 集計を終了する日。
    - week (int, optional): 対象週。指定すると、その週の範囲内でデータを集計します。Noneの場合は月全体が対象になります。

    Returns:
    - list: 各グラフに対するデータのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    result_list_all = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            chdata = {
                'value': 0.0,
            }
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE, get_data_at__date__gte=gateway_startdate).order_by('-get_data_at')
            else:
                data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE).order_by('-get_data_at')

            if year is not None and month is not None:
                if week is None:
                    data_per_date = data_per_date.filter(get_data_at__year=year, get_data_at__month=month)
                else:
                    first_date, last_date = get_week_range(int(year), int(month), int(week))
                    data_per_date = data_per_date.filter(get_data_at__range=(first_date, last_date))
                if start is not None and end is not None:
                    data_per_date = data_per_date.filter(get_data_at__day__range=(int(start), int(end)))

            one_data = data_per_date.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute',
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            ).first()

            chdata = get_chdate(one_data, data_type, Data.DateType.DATE, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)

        result = {
            'no' : graph_adapter.channel_no,
            'name' : graph_adapter.channel_name,
            'data' : chdata
        }
        result_list_all.append(result)

    return result_list_all


def get_graph_data_ranking_minutes(company_id, data_type, mode, top, year, month, date, hour, minute):
    """
    指定された日時から4時間分の時系列データを取得し、各Channel合計のランキングを求める。
    上位件数が指定されたら、上位 (top)件＋その他、で集計する

    この関数は、指定された企業IDに基づいて、特定の日時から4時間後までの電力データを集計し、
    円グラフに表示するためのデータを生成します。

    Parameters:
    - company_id (int): 時系列データを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード = intensity
    - top (int), optional: 上位 x 件＋その他
    - year (int): 開始年。
    - month (int): 開始月。
    - date (int): 開始日。
    - hour (int): 開始時。
    - minute (int): 開始分。

    Returns:
    - list: 各グラフに対する時系列データのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 指定時刻から範囲を指定
    start_ymd_hm = datetime.datetime(int(year), int(month), int(date), int(hour), int(minute), 0)
    end_ymd_hm = start_ymd_hm + datetime.timedelta(hours=4)

    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    chdata_list = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            sum_value = 0.0
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE, get_data_at__date__gte=gateway_startdate).order_by('get_data_at')
            else:
                data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE).order_by('get_data_at')

            if start_ymd_hm is not None and end_ymd_hm is not None:
                data_per_minute = data_per_minute.filter(get_data_at__range=(start_ymd_hm, end_ymd_hm))

            aggregated_data = data_per_minute.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'get_data_at__second'
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            )

            sum_value = sum_chdate(aggregated_data, data_type, Data.DateType.MINUTE, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)
        result = {
            'no': graph_adapter.channel_no,
            'name': graph_adapter.channel_name,
            'value': sum_value,
        }
        chdata_list.append(result)

    all_sum = sum([chdata['value'] for chdata in chdata_list])
    for chdata in chdata_list:
        chdata['percent'] = round(chdata['value'] / all_sum * 100, 2)
    chdata_list = sorted(chdata_list, key=lambda x: (-x['percent'], x['no']))

    if top is not None:
        top = int(top)
        if top >= 0 and top < len(chdata_list):
            sum_other = sum([chdata['value'] for chdata in chdata_list[top:]])
            chdata_list = chdata_list[:top]
            chdata_list.append({
                'no': 0,
                'name': 'その他合計',
                'value': round(sum_other, 12),
                'percent': round(sum_other / all_sum * 100, 2),
            })

    percent_delta = 100.0 - sum([chdata['percent'] for chdata in chdata_list])
    chdata_list[0]['percent'] += percent_delta

    return chdata_list


def get_graph_data_ranking_hours(company_id, data_type, mode, top, year, month, date, start, end):
    """
    指定された日付における、特定の時間範囲内の時系列データを取得し、各Channel合計のランキングを求める。
    上位件数が指定されたら、上位 (top)件＋その他、で集計する

    この関数は、指定された企業IDに基づいて、特定の日付と時間範囲（開始時刻から終了時刻）における電力データを集計し、
    円グラフに表示するためのデータを生成します。

    Parameters:
    - company_id (int): 時系列データを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード（例：'intensity'など）。
    - top (int), optional: 上位 x 件＋その他
    - year (int): 対象年。
    - month (int): 対象月。
    - date (int): 対象日。
    - start (int): 集計を開始する時間。
    - end (int): 集計を終了する時間。

    Returns:
    - list: 各グラフに対する時系列データのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    chdata_list = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            sum_value = 0.0
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR, get_data_at__date__gte=gateway_startdate).order_by('get_data_at')
            else:
                data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR).order_by('get_data_at')

            if year is not None and month is not None and date is not None:
                data_per_hour = data_per_hour.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date)
                if start is not None and end is not None:
                    data_per_hour = data_per_hour.filter(get_data_at__time__range=(int(start), int(end)))

            aggregated_data = data_per_hour.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            )

            sum_value = sum_chdate(aggregated_data, data_type, Data.DateType.HOUR, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)
        result = {
            'no': graph_adapter.channel_no,
            'name': graph_adapter.channel_name,
            'value': sum_value,
        }
        chdata_list.append(result)

    all_sum = sum([chdata['value'] for chdata in chdata_list])
    for chdata in chdata_list:
        chdata['percent'] = round(chdata['value'] / all_sum * 100, 2)
    chdata_list = sorted(chdata_list, key=lambda x: (-x['percent'], x['no']))

    if top is not None:
        top = int(top)
        if top >= 0 and top < len(chdata_list):
            sum_other = sum([chdata['value'] for chdata in chdata_list[top:]])
            chdata_list = chdata_list[:top]
            chdata_list.append({
                'no': 0,
                'name': 'その他合計',
                'value': round(sum_other, 12),
                'percent': round(sum_other / all_sum * 100, 2),
            })

    percent_delta = 1.0 - sum([chdata['percent'] for chdata in chdata_list])
    chdata_list[0]['percent'] += percent_delta

    return chdata_list


def get_graph_data_ranking_days(company_id, data_type, mode, top, year, month, start, end, week):
    """
    指定された期間（日単位）における時系列データを取得し、各Channel合計のランキングを求める。
    上位件数が指定されたら、上位 (top)件＋その他、で集計する

    この関数は、指定された企業IDに基づいて、特定の年、月、週（オプション）、および日の範囲における電力データを集計し、
    円グラフに表示するためのデータを生成します。

    Parameters:
    - company_id (int): 時系列データを取得したい企業のID。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - mode (str): データ集計のモード（例：'intensity'など）。
    - top (int), optional: 上位 x 件＋その他
    - year (int): 対象年。
    - month (int): 対象月。
    - start (int): 集計を開始する日。
    - end (int): 集計を終了する日。
    - week (int, optional): 対象週。指定すると、その週の範囲内でデータを集計します。Noneの場合は月全体が対象になります。

    Returns:
    - list: 各グラフに対する時系列データのリスト。グラフ番号順に格納されている。
        - 集計データには、電力使用量、CO2排出量、経済活動量に基づく計算結果が含まれます。
    """
    # 年間計画値->カーボンクレジット価格（円/t-CO2）
    annual_plan_values = AnnualPlanValues.objects.filter(company_id_id=company_id).first()
    co2_unit_price = annual_plan_values.carbon_credit_price if annual_plan_values else 0.0

    # 原単位（経済活動量）：economic_activity_amountを取得するためのSubquery
    # 各レコードの年月に依存する
    economic_activity_amount_query = DailyEconomicActivityAmount.objects.filter(
        company_id=company_id, 
        activity_date__year=OuterRef('get_data_at__year'), 
        activity_date__month=OuterRef('get_data_at__month')
    ).values('value')[:1]

    chdata_list = []
    graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id).order_by('channel_no')
    for graph_adapter in graph_adapters:
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            sum_value = 0.0
        else:
            # 計算式文字列、光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）、削減量係数
            equation_str = graph_setting['equation_str']
            electric_unit_price = graph_setting['electric_price']    
            electric_unit_co2 = graph_setting['co2_coefficient']
            reduction_coefficient = graph_setting['reduction_coefficient']

            entity_id = graph_setting['entity_id']

            # DeviceのGatewayの使用開始日を取得
            gateway_startdate = graph_setting['startdate']
            if gateway_startdate is not None:
                data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE, get_data_at__date__gte=gateway_startdate).order_by('get_data_at')
            else:
                data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE).order_by('get_data_at')

            if year is not None and month is not None:
                if week is None:
                    data_per_date = data_per_date.filter(get_data_at__year=year, get_data_at__month=month)
                else:
                    first_date, last_date = get_week_range(int(year), int(month), int(week))
                    data_per_date = data_per_date.filter(get_data_at__range=(first_date, last_date))
                if start is not None and end is not None:
                    data_per_date = data_per_date.filter(get_data_at__day__range=(int(start), int(end)))

            aggregated_data = data_per_date.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute',
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            )

            sum_value = sum_chdate(aggregated_data, data_type, Data.DateType.DATE, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)
        result = {
            'no': graph_adapter.channel_no,
            'name': graph_adapter.channel_name,
            'value': sum_value,
        }
        chdata_list.append(result)

    all_sum = sum([chdata['value'] for chdata in chdata_list])
    for chdata in chdata_list:
        chdata['percent'] = round(chdata['value'] / all_sum * 100, 2)
    chdata_list = sorted(chdata_list, key=lambda x: (-x['percent'], x['no']))

    if top is not None:
        top = int(top)
        if top >= 0 and top < len(chdata_list):
            sum_other = sum([chdata['value'] for chdata in chdata_list[top:]])
            chdata_list = chdata_list[:top]
            chdata_list.append({
                'no': 0,
                'name': 'その他合計',
                'value': round(sum_other, 12),
                'percent': round(sum_other / all_sum * 100, 2),
            })

    percent_delta = 1.0 - sum([chdata['percent'] for chdata in chdata_list])
    chdata_list[0]['percent'] += percent_delta

    return chdata_list




def get_week_range(year, month, week_index):
    """
    その月の週index(0始まり)からその週の開始日＝月曜日と終了日＝日曜日の日時を取得する。

    指定された年月と週のインデックスに基づいて、その週の開始日（月曜日）と終了日（日曜日）の日時を計算します。
    週のインデックスは0始まりで、月の最初の週が0となります。

    Parameters:
    - year (int): 年。
    - month (int): 月。
    - week_index (int): 週のインデックス（0始まり）。

    Returns:
    - tuple: 週の開始日時と終了日時を含むタプル。開始日時はその週の月曜日の0時0分0秒、終了日時はその週の日曜日の23時59分59秒。
    """
    # 月の初日を取得
    first_datetime = datetime.datetime(year, month, 1, 0, 0)

    # 月の初日が火曜以降の場合、前の月の月曜まで戻る
    start_datetime = first_datetime - datetime.timedelta(days=(first_datetime.weekday() - calendar.MONDAY))

    # 指定されたweek_indexの週の月曜日を取得
    start_datetime += datetime.timedelta(weeks=week_index)

    # 週の終わり（日曜日の23:59:59）を取得
    end_datetime = (start_datetime + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59))

    return start_datetime, end_datetime

def  list_chdate(data, data_type, date_type, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient):
    """
    集計データに基づいて最終的な結果を更新し、計算結果を辞書形式で返す。

    この関数は、集計されたデータに対して計算式を適用し、電力使用量、CO2排出量、経済活動量などの計算結果を生成します。
    計算結果は、指定された日付タイプ（分、時、日など）に応じたキーで辞書に格納されます。

    Parameters:
    - data (QuerySet): 集計されたデータのクエリセット。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - date_type (Data.DateType): 集計データの日付タイプ。
    - mode (str): データ集計のモード = intensity
    - equation_str (str): 電力使用量の計算に使用する式の文字列。
    - electric_unit_price (float): 電力単価（円/kWh）。
    - electric_unit_co2 (float): CO2排出係数（t-CO2/kWh）。
    - co2_unit_price (float): カーボンクレジット価格（円/t-CO2）。
    - reduction_coefficient (float): 削減量の計算に使用する係数。

    Returns:
    - dict: 計算結果を含む辞書。キーは日付タイプに応じた時間キー、値は計算結果の辞書。
    """
    return [get_chdate(item, data_type, date_type, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient) for item in data]


def  sum_chdate(data, data_type, date_type, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient):
    """
    集計データの合計を求める。

    Parameters:
    - data (QuerySet): 集計されたデータのクエリセット。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - date_type (Data.DateType): 集計データの日付タイプ。
    - mode (str): データ集計のモード = intensity
    - equation_str (str): 電力使用量の計算に使用する式の文字列。
    - electric_unit_price (float): 電力単価（円/kWh）。
    - electric_unit_co2 (float): CO2排出係数（t-CO2/kWh）。
    - co2_unit_price (float): カーボンクレジット価格（円/t-CO2）。
    - reduction_coefficient (float): 削減量の計算に使用する係数。

    Returns:
    - 値の合計値
    """
    return round(sum([get_chdate(item, data_type, date_type, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient)['value'] for item in data]), 12)


def  get_chdate(one_data, data_type, date_type, mode, equation_str, electric_unit_price, electric_unit_co2, co2_unit_price, reduction_coefficient):
    """
    データに基づいて最終的な結果を更新し、結果を辞書形式で返す。

    この関数は、集計されたデータに対して計算式を適用し、電力使用量、CO2排出量、経済活動量などの計算結果を生成します。
    計算結果は、指定された日付タイプ（分、時、日など）に応じたキーで辞書に格納されます。

    Parameters:
    - data (QuerySet): 集計されたデータのクエリセット。
    - data_type (str): データ種別 = electrical | utility_costs | co2emissions | carbon_credit | reduction_electrical | reduction_utility_costs | reduction_co2emissions
    - date_type (Data.DateType): 集計データの日付タイプ。
    - mode (str): データ集計のモード = intensity
    - equation_str (str): 電力使用量の計算に使用する式の文字列。
    - electric_unit_price (float): 電力単価（円/kWh）。
    - electric_unit_co2 (float): CO2排出係数（t-CO2/kWh）。
    - co2_unit_price (float): カーボンクレジット価格（円/t-CO2）。
    - reduction_coefficient (float): CO2削減量の計算に使用する係数。

    Returns:
    - dict: 計算結果を含む辞書。キーは日付タイプに応じた時間キー、値は計算結果の辞書。
    """
    if one_data is None:
        return None

    item_year = one_data['get_data_at__year']
    item_month = one_data['get_data_at__month']
    item_date = one_data['get_data_at__day']
    item_hour = one_data['get_data_at__hour']
    item_minute = one_data['get_data_at__minute']
    item_second = one_data['get_data_at__second'] if date_type == Data.DateType.MINUTE else 0

    # 1日の実績値：この段階で計算式を適用する.計算式には'x'が使われることになっている
    equation = parse_expr(equation_str)
    expr = symbols('x')
    electrical_value = float(equation.subs(expr, one_data['electrical_value'])) if one_data['electrical_value'] else 0.0
    if mode == "intensity":
        # 原単位（経済活動量）
        economic_activity_value = one_data['economic_activity_value']
        if economic_activity_value and economic_activity_value > 0.0:
            electrical_value = electrical_value / economic_activity_value

    value = electrical_value
    if data_type == "utility_costs":
        value = electrical_value * electric_unit_price
    elif data_type == "co2emissions":
        value = electrical_value * electric_unit_co2 * 1000     # 内部計算結果は t-CO2e, 出力単位は kg-CO2e
    elif data_type == "carbon_credit":
        value = electrical_value * electric_unit_co2 * co2_unit_price * reduction_coefficient

    elif data_type == "reduction_electrical":
        value = electrical_value * reduction_coefficient
    elif data_type == "reduction_utility_costs":
        value = electrical_value * electric_unit_price * reduction_coefficient
    elif data_type == "reduction_co2emissions":
        value = electrical_value * electric_unit_co2 * reduction_coefficient * 1000     # 内部計算結果は t-CO2e, 出力単位は kg-CO2e

    return {
        'year': item_year,
        'month': item_month,
        'date': item_date,
        'hour': item_hour,
        'minute': item_minute,
        'second': item_second,
        'value': round(value, 12),
    }

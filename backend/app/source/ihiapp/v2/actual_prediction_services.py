import calendar
import datetime
import pandas as pd

from django.utils import timezone
from dateutil.relativedelta import relativedelta
from sympy import symbols, parse_expr

from ..constants import DATA_TYPE_ELECTRICITY
from ..models import ( AnnualPlanValues, ChannelAdapter, Data, DataType )

from .utils import ( get_graph_setting )


def get_actual_values(company_id, data_type, channel_numbers):
    if data_type == 'electrical':
        actual_value = _get_actual_value_electrical(company_id, channel_numbers)
        target_value = _monthly_target_value_electrical(company_id)

    elif data_type == 'utility_costs':
        actual_value = _get_actual_value_utility_costs(company_id, channel_numbers)
        target_value = _monthly_target_value_utility_costs(company_id)

    elif data_type == 'co2emissions':
        actual_value = _get_actual_value_co2emissions(company_id, channel_numbers)
        target_value = _monthly_target_value_co2emissions(company_id)

    elif data_type == 'carbon_credit':
        actual_value = _get_actual_value_carbon_credit(company_id, channel_numbers)
        target_value = _monthly_target_value_carbon_credit(company_id)

    elif data_type == 'reduction_electrical':
        actual_value = _get_actual_value_reduction_electrical(company_id, channel_numbers)
        target_value = _monthly_target_value_reduction_electrical(company_id)

    elif data_type == 'reduction_utility_costs':
        actual_value = _get_actual_value_reduction_utility_costs(company_id, channel_numbers)
        target_value = _monthly_target_value_reduction_utility_costs(company_id)

    elif data_type == 'reduction_co2emissions':
        actual_value = _get_actual_value_reduction_co2emissions(company_id, channel_numbers)
        target_value = _monthly_target_value_reduction_co2emissions(company_id)

    else:       # 'electrical'
        actual_value = _get_actual_value_electrical(company_id, channel_numbers)
        target_value = _monthly_target_value_electrical(company_id)

    rate = actual_value / target_value if target_value != 0 else 0
    percent = round(rate * 100, 2)
    data = {
        'actual_value': actual_value,   # 実績値
        'target_value': target_value,   # 目標値
        'percent': percent              # 実績値/目標値
    }
    return data

def get_predicted_values(company_id, data_type):
    if data_type == 'electrical':
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_electrical(company_id)
        yearly_target_value = _yearly_target_value_electrical(company_id)

    elif data_type == 'utility_costs':
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_utility_costs(company_id)
        yearly_target_value = _yearly_target_value_utility_costs(company_id)

    elif data_type == 'co2emissions':
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_co2emissions(company_id)
        yearly_target_value = _yearly_target_value_co2emissions(company_id)

    elif data_type == 'carbon_credit':
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_carbon_credit(company_id)
        yearly_target_value = _yearly_target_value_carbon_credit(company_id)

    elif data_type == 'reduction_electrical':
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_reduction_electrical(company_id)
        yearly_target_value = _yearly_target_value_reduction_electrical(company_id)

    elif data_type == 'reduction_utility_costs':
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_reduction_utility_costs(company_id)
        yearly_target_value = _yearly_target_value_reduction_utility_costs(company_id)

    elif data_type == 'reduction_co2emissions':
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_reduction_co2emissions(company_id)
        yearly_target_value = _yearly_target_value_reduction_co2emissions(company_id)

    else:       # 'electrical'
        monthly_prediction_value, yearly_prediction_value = _get_predicted_value_electrical(company_id)
        yearly_target_value = _yearly_target_value_electrical(company_id)


    # 改善率＝目標値に対する予測値の割合
    yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_value if yearly_target_value != 0 else 0)
    percent = round(yearly_improvement_rate * 100, 2)
    data = {
        'monthly_prediction_value': monthly_prediction_value,   # 月間予測値
        'yearly_prediction_value': yearly_prediction_value,     # 年間予測値
        'yearly_target_value': yearly_target_value,             # 年間目標値
        'percent': percent                                      # 改善率（%）
    }
    return data



def _get_actual_value_electrical(company_id, channel_numbers):
    # graph情報の取得：指定番号のみを対象とする
    actual_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の実績値：電力量 kWh
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        value = _monthly_actual_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        actual_value += float(equation.subs(expr, value))
    return actual_value


def _get_actual_value_utility_costs(company_id, channel_numbers):
    # graph情報の取得：指定番号のみを対象とする
    actual_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の実績値：電力量 kWh
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        value = _monthly_actual_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        electric_price = graph_setting['electric_price']    # 円/kWh
        val = float(equation.subs(expr, value)) * float(electric_price)
        actual_value += val
    return actual_value


def _get_actual_value_co2emissions(company_id, channel_numbers):
    # graph情報の取得：指定番号のみを対象とする
    actual_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の実績値：電力量 kWh
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        value = _monthly_actual_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        co2_coefficient = graph_setting['co2_coefficient']  # t-CO₂/kWh
        val = float(equation.subs(expr, value)) * float(co2_coefficient)

        actual_value += val
    return actual_value


def _get_actual_value_carbon_credit(company_id, channel_numbers):
    # graph情報の取得：指定番号のみを対象とする
    actual_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の実績値：電力量 kWh
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        value = _monthly_actual_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        co2_coefficient = graph_setting['co2_coefficient']              # t-CO₂/kWh
        carbon_credit_price = _get_carbon_credit_price(company_id)      # 円/t-CO₂
        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数
        val = float(equation.subs(expr, value)) * float(co2_coefficient) * float(carbon_credit_price) * float(reduction_coefficient)

        actual_value += val
    return actual_value


def _get_actual_value_reduction_electrical(company_id, channel_numbers):
    # graph情報の取得：指定番号のみを対象とする
    actual_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の実績値：電力量 kWh
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        value = _monthly_actual_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数
        val = float(equation.subs(expr, value)) * float(reduction_coefficient)

        actual_value += val
    return actual_value


def _get_actual_value_reduction_utility_costs(company_id, channel_numbers):
    # graph情報の取得：指定番号のみを対象とする
    actual_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の実績値：電力量 kWh
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        value = _monthly_actual_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')
        
        electric_price = graph_setting['electric_price']                # 円/kWh
        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数
        val = float(equation.subs(expr, value)) * float(electric_price) * float(reduction_coefficient)

        actual_value += val
    return actual_value


def _get_actual_value_reduction_co2emissions(company_id, channel_numbers):
     # graph情報の取得：指定番号のみを対象とする
    actual_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の実績値：電力量 kWh
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        value = _monthly_actual_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')
        
        co2_coefficient = graph_setting['co2_coefficient']              # t-CO₂/kWh
        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数
        val = float(equation.subs(expr, value)) * float(co2_coefficient) * float(reduction_coefficient)

        actual_value += val
    return actual_value



def _get_predicted_value_electrical(company_id):
    # graph情報の取得
    monthly_prediction_value = 0.0
    yearly_prediction_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の予測値/年間予測値：電力量
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        monthly_value = _monthly_prediction_value_raw_electrical(entity_id, startdate)
        yearly_value = _yearly_prediction_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        monthly_prediction_value += float(equation.subs(expr, monthly_value))
        yearly_prediction_value += float(equation.subs(expr, yearly_value))
    return monthly_prediction_value, yearly_prediction_value


def _get_predicted_value_utility_costs(company_id):
    # graph情報の取得
    monthly_prediction_value = 0.0
    yearly_prediction_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の予測値/年間予測値：電力量
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        monthly_value = _monthly_prediction_value_raw_electrical(entity_id, startdate)
        yearly_value = _yearly_prediction_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        electric_price = graph_setting['electric_price']    # 円/kWh

        monthly_prediction_value += float(equation.subs(expr, monthly_value))*float(electric_price)
        yearly_prediction_value += float(equation.subs(expr, yearly_value))*float(electric_price)
    return monthly_prediction_value, yearly_prediction_value


def _get_predicted_value_co2emissions(company_id):
    # graph情報の取得
    monthly_prediction_value = 0.0
    yearly_prediction_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の予測値/年間予測値：電力量
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        monthly_value = _monthly_prediction_value_raw_electrical(entity_id, startdate)
        yearly_value = _yearly_prediction_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        co2_coefficient = graph_setting['co2_coefficient']  # t-CO₂/kWh

        monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(co2_coefficient)
        yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(co2_coefficient)
    return monthly_prediction_value, yearly_prediction_value


def _get_predicted_value_carbon_credit(company_id):
    # graph情報の取得
    monthly_prediction_value = 0.0
    yearly_prediction_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の予測値/年間予測値：電力量
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        monthly_value = _monthly_prediction_value_raw_electrical(entity_id, startdate)
        yearly_value = _yearly_prediction_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        co2_coefficient = graph_setting['co2_coefficient']              # t-CO₂/kWh
        carbon_credit_price = _get_carbon_credit_price(company_id)      # 円/t-CO₂
        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数

        monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(co2_coefficient) * float(carbon_credit_price) * float(reduction_coefficient)
        yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(co2_coefficient) * float(carbon_credit_price) * float(reduction_coefficient)
    return monthly_prediction_value, yearly_prediction_value


def _get_predicted_value_reduction_electrical(company_id):
    # graph情報の取得
    monthly_prediction_value = 0.0
    yearly_prediction_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の予測値/年間予測値：電力量
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        monthly_value = _monthly_prediction_value_raw_electrical(entity_id, startdate)
        yearly_value = _yearly_prediction_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数

        monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(reduction_coefficient)
        yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(reduction_coefficient)
    return monthly_prediction_value, yearly_prediction_value


def _get_predicted_value_reduction_utility_costs(company_id):
    # graph情報の取得
    monthly_prediction_value = 0.0
    yearly_prediction_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の予測値/年間予測値：電力量
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        monthly_value = _monthly_prediction_value_raw_electrical(entity_id, startdate)
        yearly_value = _yearly_prediction_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        electric_price = graph_setting['electric_price']                # 円/kWh
        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数

        monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(electric_price) * float(reduction_coefficient)
        yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(electric_price) * float(reduction_coefficient)
    return monthly_prediction_value, yearly_prediction_value


def _get_predicted_value_reduction_co2emissions(company_id):
    # graph情報の取得
    monthly_prediction_value = 0.0
    yearly_prediction_value = 0.0
    for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
        # graphごとの設定値
        graph_setting = get_graph_setting(graph_adapter)
        if graph_setting is None:
            continue

        # graphごとの月の予測値/年間予測値：電力量
        entity_id = graph_setting['entity_id']
        startdate = graph_setting['startdate']
        monthly_value = _monthly_prediction_value_raw_electrical(entity_id, startdate)
        yearly_value = _yearly_prediction_value_raw_electrical(entity_id, startdate)

        # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
        equation_str = graph_setting['equation_str']
        equation = parse_expr(equation_str)
        expr = symbols('x')

        co2_coefficient = graph_setting['co2_coefficient']              # t-CO₂/kWh
        reduction_coefficient = graph_setting['reduction_coefficient']  # 削減量係数

        monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(co2_coefficient) * float(reduction_coefficient)
        yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(co2_coefficient) * float(reduction_coefficient)
    return monthly_prediction_value, yearly_prediction_value


# 月の目標値：電力量
def _monthly_target_value_electrical(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.electric / 12 if not yearly_target_values is None else 0

# 月の目標値：光熱費
def _monthly_target_value_utility_costs(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.utility_cost / 12 if not yearly_target_values is None else 0

# 月の目標値：CO2排出量
def _monthly_target_value_co2emissions(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.co2_emissions / 12 if not yearly_target_values is None else 0

# 月の目標値：カーボンクレジット   
def _monthly_target_value_carbon_credit(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.carbon_credit / 12 if not yearly_target_values is None else 0

# 月の目標値：電力削減量
def _monthly_target_value_reduction_electrical(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.electric_reduce / 12 if not yearly_target_values is None else 0

# 月の目標値：光熱削減費
def _monthly_target_value_reduction_utility_costs(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.utility_cost_reduce / 12 if not yearly_target_values is None else 0

# 月の目標値：CO2削減量
def _monthly_target_value_reduction_co2emissions(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.co2_emissions_reduce / 12 if not yearly_target_values is None else 0


# 年の目標値：電力量
def _yearly_target_value_electrical(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.electric if not yearly_target_values is None else 0

# 年の目標値：光熱費
def _yearly_target_value_utility_costs(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.utility_cost if not yearly_target_values is None else 0

# 年の目標値：CO2排出量
def _yearly_target_value_co2emissions(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.co2_emissions if not yearly_target_values is None else 0

# 年の目標値：カーボンクレジット   
def _yearly_target_value_carbon_credit(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.carbon_credit if not yearly_target_values is None else 0

# 年の目標値：電力削減量
def _yearly_target_value_reduction_electrical(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.electric_reduce if not yearly_target_values is None else 0

# 年の目標値：光熱削減費
def _yearly_target_value_reduction_utility_costs(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.utility_cost_reduce if not yearly_target_values is None else 0

# 年の目標値：CO2削減量
def _yearly_target_value_reduction_co2emissions(company_id):
    yearly_target_values = _yearly_target(company_id)
    return yearly_target_values.co2_emissions_reduce if not yearly_target_values is None else 0

def _yearly_target(company_id):
    '''
    年の目標値を取得
    '''
    # 月の目標値は、年の目標値を12で割る
    # now = timezone.now()
    # year = now.year
    try:
        anual_plan_values = AnnualPlanValues.objects.get(company_id=company_id)
    except AnnualPlanValues.DoesNotExist:
        anual_plan_values = None            
    return anual_plan_values



# 円/t-CO₂
def _get_carbon_credit_price(company_id):
    annual_plan_values = AnnualPlanValues.objects.filter(company_id__id=company_id).first()
    if annual_plan_values is None:
        return 0.0
    return annual_plan_values.carbon_credit_price

# 月の実績値：電力量：取得した値
def _monthly_actual_value_raw_electrical(entity_id, startdate):
    '''
    月の電力量の実績値を計算
    '''
    # 本日の始まり時刻、昨日の最終時刻、月の始まり日
    now = timezone.now()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_yesterday = start_of_today - relativedelta(seconds=1)
    start_of_month = datetime.datetime(now.year, now.month, 1).date()

    # 既存データ：1日00:00:00〜昨日23:59:59までのデータ
    target_month_df = _get_df(start_of_month, end_of_yesterday, entity_id, startdate, Data.DateType.DATE)

    # 実績値を計算
    actual_electrical = _calc_cost_actual(target_month_df, DATA_TYPE_ELECTRICITY)
    return actual_electrical

# 月の予測値：電力量：取得時の生データでの計算
def _monthly_prediction_value_raw_electrical(entity_id, startdate):
    '''
    月の光熱費の予測値を計算
    '''
    # 今日、月初、月末、今日から月末までの残り日数（今日を含む）
    now = timezone.now()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_yesterday = start_of_today - relativedelta(seconds=1)
    startday_of_month = datetime.datetime(now.year, now.month, 1).date()
    _, endday_of_month = calendar.monthrange(now.year, now.month)
    remaining_days = (endday_of_month - now.day) + 1

    # 予測の元データ：14日前00:00:00〜昨日23:59:59までのデータ（14日分）
    WINDOW_SIZE = 14
    target_window_df = _get_df(start_of_today - datetime.timedelta(days=WINDOW_SIZE), end_of_yesterday, entity_id, startdate, Data.DateType.DATE)

    # 予測月の既存データ：1日00:00:00〜昨日23:59:59までのデータ
    target_month_df = _get_df(startday_of_month, end_of_yesterday, entity_id, startdate, Data.DateType.DATE)

    # 予測値を計算
    predicted_electrical = _calc_cost_prediction(target_window_df, target_month_df, remaining_days, DATA_TYPE_ELECTRICITY)
    return predicted_electrical

# 年の予測値：電力量：首都k時の生データでの計算
def _yearly_prediction_value_raw_electrical(entity_id, startdate):
    '''
    年の光熱費の予測値を計算
    '''
    now = timezone.now()
    start_of_thismonth = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
    end_of_lastmonth = start_of_thismonth - relativedelta(seconds=1)
    start_of_thisyear = datetime.datetime(now.year, 1, 1, 0, 0, 0)
    remaining_months = 12 - end_of_lastmonth.month

    # 予測の元データ：三ヶ月前〜先月までのデータ（三ヶ月分）
    WINDOW_SIZE = 3
    target_window_df = _get_df(start_of_thismonth - relativedelta(months=WINDOW_SIZE), end_of_lastmonth, entity_id, startdate, Data.DateType.MONTH)

    # 予測年の既存データ：1月1日〜先月までのデータ
    target_year_df = _get_df(start_of_thisyear, end_of_lastmonth, entity_id, startdate, Data.DateType.MONTH) 

    # 予測値を計算
    predicted_electrical = _calc_cost_prediction(target_window_df, target_year_df, remaining_months, DATA_TYPE_ELECTRICITY)
    return predicted_electrical

def _calc_cost_actual(target_period_df, type_name):
    '''
    実績値を計算
    @param target_period_df: 予測対象期間の既存データ
    @param type_name: データタイプ名 := DATA_TYPE_ELECTRICITY|DATA_TYPE_CO2
    @return: 実績値
    '''
    if (len(target_period_df) == 0):
        return 0.0

    type_id = DataType.objects.get(name=type_name).id

    # 対象月の既存データの合計値を計算
    data_month_df = target_period_df[target_period_df['data_type_id'] == type_id]
    target_value = _calc_sum(data_month_df)

    return target_value

def _calc_cost_prediction(target_window_df, target_period_df, remaining_count, type_name):
    '''
    各種の予測値を計算
    @param target_window_df: 予測の元データ（14日分/三ヶ月分）
    @param target_period_df: 予測期間の既存データ
    @param remaining_count: 今日から月末までの残り日数（今日を含む）／今月から年末までの残り月数（今月を含む）
    @param type_name: データタイプ名 := DATA_TYPE_ELECTRICITY|DATA_TYPE_CO2
    @return: 予測値
    '''
    if (len(target_window_df) == 0):
        return 0.0

    type_id = DataType.objects.get(name=type_name).id

    # 予測の元データの平均値を計算
    data_window_df = target_window_df[target_window_df['data_type_id'] == type_id]
    avg_value = _calc_avg(data_window_df)

    # 対象期間の既存データの合計値を計算
    if (len(target_period_df) == 0):
        target_value = 0.0
    else:
        data_period_df = target_period_df[target_period_df['data_type_id'] == type_id]
        target_value = _calc_sum(data_period_df)

    # 今月の光熱費の予測値を計算
    value_prediction = target_value + avg_value * remaining_count
    return value_prediction

def _get_df(start, end, entity_id, startdate, date_type):
    if startdate is not None:
        data = Data.objects.filter(get_data_at__range=[start, end], entity_id=entity_id, date_type=date_type, get_data_at__date__gte=startdate).order_by('get_data_at')
    else:
        data = Data.objects.filter(get_data_at__range=[start, end], entity_id=entity_id, date_type=date_type).order_by('get_data_at')

    df = pd.DataFrame.from_records(data.values())
    return df

def _calc_sum(data_df):
    return data_df["value"].fillna(0).sum() if len(data_df) > 0 else 0.0

def _calc_avg(data_df):
    return  data_df["value"].fillna(0).sum() / len(data_df) if len(data_df) > 0 else 0.0


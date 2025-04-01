from ..models import ChannelAdapter, GatewayStartdate

def get_graph_setting(graph_adapter:ChannelAdapter):
    """
    指定されたグラフアダプターに対する設定情報を取得する。

    この関数は、グラフアダプターに関連する設定情報（計算式、電力単価、CO2排出係数など）を取得します。
    取得した設定情報は、トレンドグラフデータの計算に使用されます。

    Parameters:
    - graph_adapter (ChannelAdapter): 設定情報を取得するグラフアダプターのインスタンス。

    Returns:
    - dict: グラフアダプターの設定情報を含む辞書。Noneが返される場合もある。
    """
    device = graph_adapter.device_number
    if device is None or device.entity is None:
        return None
    entity_id = device.entity.id

    # 計算式文字列の取得
    equation_str = graph_adapter.equation_str
    if equation_str is None or equation_str == '':
        equation_str ='(x)'         # 計算式が取得できなかった場合は、xをそのまま返す

    # 円/kWh
    electric_price = graph_adapter.utility_cost_price
    # t-CO₂/kWh
    co2_coefficient = graph_adapter.co2_emissions_current

    # 削減量の算出係数
    reduction_coefficient = 0.0
    if graph_adapter.is_co2_emissions_baseline:
        if graph_adapter.co2_emissions_baseline > 0.0:
            reduction_coefficient = 1.0 - (graph_adapter.co2_emissions_current / graph_adapter.co2_emissions_baseline)
    else:
        reduction_coefficient = graph_adapter.co2_emissions_improvement_rate

    # ゲートウェイの利用開始日
    gateway_id = device.gateway_id
    startdate_obj = GatewayStartdate.objects.filter(gateway_id=gateway_id).order_by('-updated_at').first()
    startdate = startdate_obj.started_at if startdate_obj else None

    result = {
        'entity_id': entity_id,
        'equation_str': equation_str,                   # (x)
        'electric_price': electric_price,               # 円/kWh
        'co2_coefficient': co2_coefficient,             # CO₂排出係数（t-CO₂/kWh）
        'reduction_coefficient': reduction_coefficient, # 削減量係数
        'startdate': startdate,                         # 利用開始日
    }
    return result


# comma区切りの数字列からChannel番号を切り出してリストにして返す
def get_channel_no_list(channel_numbers):
    # Channel番号の取得：エラーなら０を返す
    def _int_range16(value):
        try:
            val = int(value)
            return val if 1 <= val <= 16 else 0
        except:
            return 0

    if channel_numbers is not None:
        channel_numbers = [num for num in set(_int_range16(c) for c in channel_numbers.split(',')) if num != 0]

    if channel_numbers is None or len(channel_numbers) == 0:
        channel_numbers = [i for i in range(1, 17)]
    return channel_numbers


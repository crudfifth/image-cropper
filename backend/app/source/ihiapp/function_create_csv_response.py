import csv
import io
from collections import defaultdict
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.utils.encoding import escape_uri_path
from sympy import symbols, parse_expr
from users.models import Company

from .models import ChannelAdapter, Data, GatewayStartdate


def create_minutely_channel_csv_response(company_id, start_datetime, end_datetime):
    return create_channel_csv_response(company_id, start_datetime, end_datetime, Data.DateType.MINUTE, timedelta(minutes=1))

def create_hourly_channel_csv_response(company_id, start_datetime, end_datetime):
    return create_channel_csv_response(company_id, start_datetime, end_datetime, Data.DateType.HOUR, timedelta(minutes=30))

def create_daily_channel_csv_response(company_id, start_datetime, end_datetime):
    return create_channel_csv_response(company_id, start_datetime, end_datetime, Data.DateType.DATE, timedelta(days=1))

def create_channel_csv_response(company_id, start_datetime, end_datetime, date_type, export_interval):
    company = Company.objects.get(id=company_id)
    # チャンネルのエンティティを取得
    channels = ChannelAdapter.objects.filter(company_id__id=company_id).order_by('channel_no')
    max_channel_no = max(channels.values_list('channel_no', flat=True))
    channel_len = max_channel_no
    channel_names = [c.channel_name for c in channels]

    # エンティティに対して、そのデータが入っているINDEXのlistを求める
    # 同じデバイスを複数のチャンネル（グラフ）に設定する場合があるので、ちょっと複雑
    channel_entity2index_dict = defaultdict(list)
    channel_equation = []
    channel_startdate = []
    for channel in channels:
        channel_no = channel.channel_no
        # EntityからIndex (channel_no - 1) への参照
        if channel.device_number and channel.device_number.entity:
            entity = channel.device_number.entity
            channel_entity2index_dict[entity].append(channel_no-1)

        # 計算式文字列の取得
        equation_str = channel.equation_str
        if equation_str is None or equation_str == '':
            equation_str ='(x)'         # 計算式が取得できなかった場合は、xをそのまま返す
        equation = parse_expr(equation_str)
        channel_equation.append(equation)

        # 利用開始日：Gatewayごとに設定されるので、CHごとに確認が必要
        startdate = None
        if channel.device_number:
            gateway_id = channel.device_number.gateway_id
            startdate_obj = GatewayStartdate.objects.filter(gateway_id=gateway_id).order_by('-updated_at').first()
            if startdate_obj is not None:
                startdate = startdate_obj.started_at
        channel_startdate.append(startdate)

    channel_entities = channel_entity2index_dict.keys()

    # チャンネルに紐付くCO2以外のdate_typeのデータを取得
    data = Data.objects.filter(
        get_data_at__range=(start_datetime, end_datetime),
        entity__company_id=company_id,
        date_type=date_type,
        entity__in=channel_entities
    ).exclude(data_type__name="CO2").select_related('entity', 'data_type')

    sio = io.StringIO()
    writer = csv.writer(sio)
    writer.writerow(['日時'] + channel_names)
    # 日時をキーとし、Dataオブジェクトのリストを値とする辞書を作成
    data_dict = defaultdict(list)
    for d in data:
        key = d.get_data_at.replace(second=0, microsecond=0)
        if date_type == Data.DateType.DATE:
            get_data_at_jst = d.get_data_at.astimezone(timezone.get_current_timezone())
            key = get_data_at_jst.replace(hour=0, minute=0, second=0, microsecond=0)
        data_dict[str(key)].append(d)

    # start_datetime から end_datetime までexport_intervalごとのデータをCSVに書き込む
    current_datetime = start_datetime
    while current_datetime <= end_datetime:
        current_datetime_jst = current_datetime.astimezone(timezone.get_current_timezone())
        current_date = current_datetime_jst.date()

        row = [float(0) for _ in range(channel_len)]
        data_key = str(current_datetime.replace(second=0, microsecond=0))
        if date_type == Data.DateType.DATE:
            data_key = str(current_datetime_jst.replace(hour=0, minute=0, second=0, microsecond=0))
        data_list = data_dict.get(data_key, [])

        for d in data_list:
            for index in channel_entity2index_dict[d.entity]:
                if channel_startdate[index] is not None and current_date < channel_startdate[index]:
                    continue
                equation = channel_equation[index]
                expr = symbols('x')
                row[index] = float(equation.subs(expr, round(float(d.value), 12)))

        datetime_str = current_datetime_jst.strftime('%Y/%m/%d') if date_type == Data.DateType.DATE else current_datetime_jst.strftime('%Y/%m/%d %-H:%M')
        row = [datetime_str] + row
        writer.writerow(row)
        current_datetime += export_interval

    response = HttpResponse(content_type='text/csv')
    interval_text = '1日' if date_type == Data.DateType.DATE else '30分' if date_type == Data.DateType.HOUR else '1分'
    csv_file_name = escape_uri_path(f"{company.name}_{interval_text}周期データ.csv")
    response['Content-Disposition'] = f'attachment; filename="{csv_file_name}"'
    response.write(sio.getvalue().encode('utf_8_sig'))
    return response
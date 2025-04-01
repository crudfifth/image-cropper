# coding: utf-8
from datetime import datetime
from django.db.models import Q
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from ..models import (AnnualPlanValues, CarbonFootprint, ChannelAdapter,
                     DailyEconomicActivityAmount, DataPerDate,
                     ChannelDataPerHour, ChannelDataPerDate,
                     ChannelDataPerMinute, 
                     Device,
                     EconomicActivityType, EconomicActivityUnit,
                     Gateway, GatewayRegistration, 
                     GatewayStartdate, 
                    #  GraphData,
                     CsvUploadHistory)



# class _DataSerializer(serializers.Serializer):
#     year = serializers.IntegerField()
#     month = serializers.IntegerField()
#     date = serializers.IntegerField()
#     hour = serializers.IntegerField()
#     minute = serializers.IntegerField()
#     second = serializers.IntegerField()
#     value = serializers.FloatField()

# class _GraphDataSerializer(serializers.ListSerializer):
#     def to_representation(self, obj):
#         serializer = _DataSerializer()
#         return [{item['graph_no']:[serializer.to_representation(v) for v in item['data']] for item in obj}]

#     @property
#     def data(self):
#         return ReturnDict(super().data[0], serializer=self)

class GraphDataSerializer(serializers.ModelSerializer):
    # class Meta:
    #     list_serializer_class = _GraphDataSerializer
    #     model = GraphData
    #     fields = '__all__'

    def to_representation(self, instance):
        return instance



class ChannelAdapterSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(source='company_id.id')
    gateway_id = serializers.CharField(source='device_number.gateway_id.id', allow_null=True)
    device_no = serializers.IntegerField(source='device_number.device_number', allow_null=True)
    graph_no = serializers.IntegerField(source='channel_no')    # フィールド名をgraph_noに変更
    graph_name = serializers.CharField(source='channel_name')   # フィールド名をgraph_nameに変更

    class Meta:
        model = ChannelAdapter
        fields = [
            # 'id', 
            'company_id', 
            # 'entity_id', 
            'graph_no', 
            'graph_name', 
            'gateway_id', 
            'device_no', 
            'equation_str', 
            'utility_cost_price', 
            'co2_emissions_current', 
            'co2_emissions_baseline', 
            'co2_emissions_improvement_rate', 
            'is_co2_emissions_baseline',
        ]

    def update(self, instance, validated_data):
        device_data = validated_data.pop('device_number', None)
        if device_data:
            gateway = device_data.get('gateway_id', None)
            if gateway:
                gateway_id = gateway.get('id')
            device_no = device_data.get('device_number', None)
            if gateway_id and device_no:
                device = Device.objects.get(gateway_id_id=gateway_id, device_number=device_no)
                if device:
                    # graph_adapterのdevice_numberを更新する
                    instance.device_number = device
        for attr, value in validated_data.items():
            # Class定義では「channel_name」になっているので、ここではそう指定しないと正常に動作しない
            if attr in ["channel_name", "equation_str", "utility_cost_price", "co2_emissions_current", "co2_emissions_baseline", "co2_emissions_improvement_rate", "is_co2_emissions_baseline"]:
                setattr(instance, attr, value)
        instance.save()
        return instance

# チャンネル設定で使うGatewayの一覧の取得するためのシリアライザー
class ChannelAdapterGatewaySerializer(serializers.ModelSerializer):
    devices = serializers.SerializerMethodField()  # SerializerMethodFieldを使用
    name = serializers.SerializerMethodField()
    enable_devices = serializers.SerializerMethodField()
    device_names = serializers.SerializerMethodField()
    gateway_id = serializers.CharField(source='id')  # フィールド名をgateway_idに変更

    class Meta:
        model = Gateway
        fields = [
            'gateway_id',
            'name',
            'devices',          # 廃止する
            'enable_devices',   # 廃止する
            'device_names'      # enableなdata_source_nameを返す
        ]

    def get_devices(self, obj):
        gateway_id = obj.id
        return Device.objects.filter(gateway_id=gateway_id).values_list('device_number', flat=True).order_by('device_number')

    def get_name(self, obj):
        gateway_id = obj.id
        gateway_name = GatewayRegistration.objects.filter(gateway_master__gateway_id__id=gateway_id).values_list('alt_name', flat=True).first()
        if gateway_name:
            return gateway_name
        return Gateway.objects.filter(id=gateway_id).values_list('name', flat=True).first()

    def get_enable_devices(self, obj):
        gateway_id = obj.id
        return Device.objects.filter(gateway_id=gateway_id,enable_data_collection=True).values_list('device_number', flat=True).order_by('device_number')

    def get_device_names(self, obj):
        gateway_id = obj.id
        # return Device.objects.filter(gateway_id=gateway_id,enable_data_collection=True).values_list('device_number', 'data_source_name').order_by('device_number')
        return Device.objects.filter(
            Q(enable_data_collection=True) | Q(input_source=Device.InputSource.CSV),
            gateway_id=gateway_id
        ).values_list('device_number', 'data_source_name').order_by('device_number')

class GatewayStartdateSerializer(serializers.ModelSerializer):
    started_at = serializers.SerializerMethodField()
    class Meta:
        model = GatewayStartdate
        fields = [
            'gateway_id', 
            'started_at', 
        ]

    def get_started_at(self, obj):
        if isinstance(obj.started_at, datetime):
            return obj.started_at.date()
        return obj.started_at

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in ["started_at"]:
                setattr(instance, attr, value)
        instance.save()
        return instance


class AnnualPlanValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualPlanValues
        fields = [
            'utility_cost',
            'utility_cost_reduce',
            'electric', 
            'electric_reduce', 
            'co2_emissions', 
            'co2_emissions_reduce', 
            'carbon_credit', 
            'carbon_credit_price', 
        ]

class RegisteredUserCountSerializer(serializers.Serializer):
    user_limit = serializers.IntegerField()
    user_count = serializers.IntegerField()
    active_user_count = serializers.IntegerField()

class RegisteredGatewayCountSerializer(serializers.Serializer):
    gateway_limit = serializers.IntegerField()
    gateway_count = serializers.IntegerField()
    operations_count = serializers.IntegerField()

class GatewayRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatewayRegistration
        fields = ['type', 'name', 'id', 'license_limit', 'license_type', 'signal_level', 'connected', 'updated_at']

    type = serializers.CharField()              # 種別：'PUSHLOG'
    name = serializers.CharField()              # ゲートウェイ名
    id = serializers.CharField()                # ゲートウェイID
    license_limit = serializers.DateField()     # 利用可能期限
    license_type = serializers.CharField()      # ライセンス種別
    signal_level = serializers.IntegerField()   # LTE-M電波状態:0:未接続、電波状態を1:弱い~4:強いで表す
    connected = serializers.BooleanField()      # 接続状態
    updated_at = serializers.DateTimeField()    # 最終データ取得時間

class CarbonFootprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonFootprint
        fields = [
            'id',
            'process_name',
            'channel_name',
            'start_date',
            'end_date',
            'electric_value',
            'co2_emissions',
            'scope_no'
        ]

class CarbonFootprintKgSerializer(serializers.ModelSerializer):
    co2_emissions = serializers.FloatField()

    class Meta:
        model = CarbonFootprint
        fields = [
            'id',
            'process_name',
            'channel_name',
            'start_date',
            'end_date',
            'electric_value',
            'co2_emissions',
            'scope_no'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['co2_emissions'] = instance.co2_emissions * 1000  # t-CO2e to kg-CO2e for output
        return ret

class CarbonFootprintChannelSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    value = serializers.FloatField()

class CarbonFootprintScopeSerializer(serializers.ModelSerializer):
    ghg_emmision = serializers.FloatField()
    scope1 = serializers.FloatField()
    scope2 = serializers.FloatField()
    scope3 = serializers.FloatField()


class EconomicActivityTypeSerializer(serializers.ModelSerializer):
    latest_value = serializers.SerializerMethodField()
    latest_date = serializers.SerializerMethodField()
    company_id = serializers.UUIDField(write_only=True)

    def get_latest_value(self, obj):
        latest_amount = DailyEconomicActivityAmount.objects.filter(activity_type_id=obj).order_by('-activity_date').first()
        if latest_amount:
            return latest_amount.value
        else:
            return None

    def get_latest_date(self, obj):
        latest_amount = DailyEconomicActivityAmount.objects.filter(activity_type_id=obj).order_by('-activity_date').first()
        if latest_amount:
            return latest_amount.activity_date
        else:
            return None

    class Meta:
        model = EconomicActivityType
        exclude = ['user_id']


class _DataPerMinuteSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    date = serializers.IntegerField()
    hour = serializers.IntegerField()
    minute = serializers.IntegerField()
    second = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.FloatField()
    co2_value = serializers.FloatField()
    co2_price = serializers.FloatField()
    electrical_value_reduction = serializers.FloatField()
    electrical_price_reduction = serializers.FloatField()
    co2_value_reduction = serializers.FloatField()
    co2_price_reduction = serializers.FloatField()

class _ChannelDataPerMinuteSerializer(serializers.ListSerializer):
    def to_representation(self, obj):
        dataperminuteserializer = _DataPerMinuteSerializer()
        return [{item['graph_no']:[dataperminuteserializer.to_representation(v) for v in item['data']] for item in obj}]

    @property
    def data(self):
        return ReturnDict(super().data[0], serializer=self)

class ChannelDataPerMinuteSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = _ChannelDataPerMinuteSerializer
        model = ChannelDataPerMinute
        fields = '__all__'

class _DataPerHourSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    date = serializers.IntegerField()
    hour = serializers.IntegerField()
    minute = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.FloatField()
    co2_value = serializers.FloatField()
    co2_price = serializers.FloatField()
    electrical_value_reduction = serializers.FloatField()
    electrical_price_reduction = serializers.FloatField()
    co2_value_reduction = serializers.FloatField()
    co2_price_reduction = serializers.FloatField()

class _ChannelDataPerHourSerializer(serializers.ListSerializer):
    def to_representation(self, obj):
        dataperhourserializer = _DataPerHourSerializer()
        return [{item['graph_no']:[dataperhourserializer.to_representation(v) for v in item['data']] for item in obj}]

    @property
    def data(self):
        return ReturnDict(super().data[0], serializer=self)

class ChannelDataPerHourSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = _ChannelDataPerHourSerializer
        model = ChannelDataPerHour
        fields = '__all__'

class DataPerDateSerializer(serializers.ModelSerializer):
    fuel_unit = serializers.CharField()

    class Meta:
        model = DataPerDate
        fields = (
        'year',
        'month',
        'date',
        'electrical_value',
        'electrical_price',
        'water_value',
        'water_price',
        'fuel_value',
        'fuel_price',
        'co2_value',
        'co2_price',
        'fuel_unit'
        )


class _DataPerDateSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    date = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.FloatField()
    co2_value = serializers.FloatField()
    co2_price = serializers.FloatField()
    electrical_value_reduction = serializers.FloatField()
    electrical_price_reduction = serializers.FloatField()
    co2_value_reduction = serializers.FloatField()
    co2_price_reduction = serializers.FloatField()

class _ChannelDataPerDateSerializer(serializers.ListSerializer):
    def to_representation(self, obj):
        dataperdateserializer = _DataPerDateSerializer()
        return [{item['graph_no']:[dataperdateserializer.to_representation(v) for v in item['data']] for item in obj}]

    @property
    def data(self):
        return ReturnDict(super().data[0], serializer=self)

class ChannelDataPerDateSerializer(serializers.ModelSerializer):
    inner_model = DataPerDateSerializer(read_only=True)

    class Meta:
        list_serializer_class = _ChannelDataPerDateSerializer
        model = ChannelDataPerDate
        fields = '__all__'


class DailyEconomicActivityAmountSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = DailyEconomicActivityAmount
        fields = ['company_id', 'value', 'activity_date']

class EconomicActivityUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicActivityUnit
        fields = ['id', 'name']



class CsvUploadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvUploadHistory
        fields = ['id', 'company', 'file_name', 'size_bytes', 'uploaded_at']
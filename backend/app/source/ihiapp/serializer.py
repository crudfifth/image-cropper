# coding: utf-8
from datetime import datetime
from django.db.models import Q
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict
from users.models import CompanyUser, User
from users.serializer import CompanySerializer, UserSerializer

from .models import (AnnualPlanValues, CarbonFootprint, ChannelAdapter,
                     DailyEconomicActivityAmount, DataPerDate, DataPerHour,
                     ChannelDataPerHour, ChannelDataPerDate, DataPerMonth,
                     DataPerMinute, ChannelDataPerMinute, 
                     DataPerMonth, DataPerYear, DataStructure, Device,
                     DeviceDataPerDate, DeviceDataPerHour, DeviceDataPerMonth,
                     DeviceDataPerYear, DeviceType, DeviceUnitPrice,
                     EconomicActivityType, EconomicActivityUnit, Entity,
                     EnvironmentalType, Gateway, GatewayRegistration, 
                     GatewayStartdate, JCreditApplication,
                     LiquidType, MDevice, MonthlyCostTarget, Unit,
                     UnitPriceHistory, UserEntityPermission, CsvUploadHistory)
import logging


# 廃止予定：ここから
# グラフ情報の取得
class ChannelAdapterNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelAdapter
        exclude = (
            'id',
            # 'entity_id',
            # 'company_id',
            'created_at',
            'updated_at'
        )
# 廃止予定：ここまで

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


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)



class EnvirontmentalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalType
        exclude = (
            'created_at',
            'updated_at'
        )

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        exclude = (
            'created_at',
            'updated_at'
        )

class LiquidTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidType
        exclude = (
            'created_at',
            'updated_at'
        )

class MDeviceSerializer(serializers.ModelSerializer):
    device_type = DeviceTypeSerializer(source="device_type_id")
    environmental_type = EnvirontmentalTypeSerializer(source="environmental_type_id")

    class Meta:
        model = MDevice
        exclude = (
            'device_type_id',
            'environmental_type_id',
            'created_at',
            'updated_at'
        )


class UnitSerializer(serializers.ModelSerializer):
    environmental_type = EnvirontmentalTypeSerializer(source="environmental_type_id")

    class Meta:
        model = Unit
        exclude = (
            'environmental_type_id',
            'created_at',
            'updated_at'
        )


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

class DeviceUnitPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceUnitPrice
        exclude = (
            'created_at',
            'updated_at'
        )

class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields = '__all__'

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'company']

    def validate_company(self, value):
        company_user = CompanyUser.objects.filter(user=self.context['request'].user, company=value).first()
        if company_user is None:
            raise serializers.ValidationError("対象企業に所属していません")
        return value

class DeviceSerializer(serializers.ModelSerializer):
    m_device = MDeviceSerializer(source="m_device_id", required=False)
    device_type = DeviceTypeSerializer(source="device_type_id", required=False)
    unit = UnitSerializer(source="unit_id", required=False)
    device_unit_price = DeviceUnitPriceSerializer(source="device_unit_price_id", required=False)
    input_source = serializers.CharField(source="get_input_source_display", required=False)
    device_unit_price = serializers.SerializerMethodField()
    gateway = GatewaySerializer(source="gateway_id", required=False)
    economic_activity_type = EconomicActivityTypeSerializer(source="economic_activity_type_id")
    liquid_type = LiquidTypeSerializer(source="liquid_type_id", required=False)
    entity = EntitySerializer(read_only=True)
    entity_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Device
        exclude = (
            'updated_at',
        )

    def get_device_unit_price(self, obj):
        try:
            device_unit_price = DeviceUnitPrice.objects.get(device=obj)
            return DeviceUnitPriceSerializer(device_unit_price).data
        except DeviceUnitPrice.DoesNotExist:
            return None

# IHI様２次開発要求仕様に合わせ、PFとの連携用に一部のFieldを返すSerializerを作成
class AllDeviceSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(source="unit_id", required=False)

    class Meta:
        model = Device
        fields = (
        'id',
        'data_source_name',
        'name',
        'unit',
        )


class DataPerMinuteSerializer(serializers.ModelSerializer):
    fuel_unit = serializers.CharField()

    class Meta:
        model = DataPerMinute
        fields = (
        'year',
        'month',
        'date',
        'hour',
        'minute',
        'second',
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

class DataPerHourSerializer(serializers.ModelSerializer):
    fuel_unit = serializers.CharField()

    class Meta:
        model = DataPerHour
        fields = (
        'year',
        'month',
        'date',
        'hour',
        'minute',
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

class ChannelDataReductionPerDateSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    date = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.FloatField()
    co2_value = serializers.FloatField()
    co2_price = serializers.FloatField()

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



class DataPerMonthSerializer(serializers.ModelSerializer):
    fuel_unit = serializers.CharField()

    class Meta:
        model = DataPerMonth
        fields = (
        'year',
        'month',
        # 'id',
        # 'user_id',
        'electrical_value',
        'electrical_price',
        'water_value',
        'water_price',
        'fuel_value',
        'fuel_price',
        'co2_value',
        'co2_price',
        # 'utility_costs',
        # 'energy_saving_value',
        # 'renewal_energy_value',
        # 'get_data_date',
        'fuel_unit'
        )


class DataPerYearSerializer(serializers.ModelSerializer):
    fuel_unit = serializers.CharField()

    class Meta:
        model = DataPerYear
        fields = (
        'year',
        # 'id',
        # 'user_id',
        'electrical_value',
        'electrical_price',
        'water_value',
        'water_price',
        'fuel_value',
        'fuel_price',
        'co2_value',
        'co2_price',
        # 'utility_costs',
        # 'energy_saving_value',
        # 'renewal_energy_value',
        # 'get_data_date',
        'fuel_unit'
        )



class DeviceDataPerHourSerializer(serializers.ModelSerializer):
    # device_id = DeviceSerializer(read_only=True)
    class Meta:
        model = DeviceDataPerHour
        fields = (
        'year',
        'month',
        'date',
        'hour',
        'minute',
        # 'id',
        # 'user_id',
        'electrical_value',
        'electrical_price',
        'water_value',
        'water_price',
        'fuel_value',
        'fuel_price',
        'co2_value',
        'co2_price',
        'utility_costs',
        'get_data_date',
        'device_id',
        )

class DeviceDataPerDateSerializer(serializers.ModelSerializer):
    device_id = DeviceSerializer(read_only=True)

    class Meta:
        model = DeviceDataPerDate
        fields = (
        'year',
        'month',
        'date',
        # 'id',
        # 'user_id',
        'electrical_value',
        'electrical_price',
        'water_value',
        'water_price',
        'fuel_value',
        'fuel_price',
        'co2_value',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'get_data_date',
        'device_id',
        )

class DeviceDataPerMonthSerializer(serializers.ModelSerializer):
    device_id = DeviceSerializer(read_only=True)

    class Meta:
        model = DeviceDataPerMonth
        fields = (
        'year',
        'month',
        # 'id',
        # 'user_id',
        'electrical_value',
        'electrical_price',
        'water_value',
        'water_price',
        'fuel_value',
        'fuel_price',
        'co2_value',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'get_data_date',
        'device_id',
        )


class DeviceDataPerYearSerializer(serializers.ModelSerializer):
    device_id = DeviceSerializer(read_only=True)

    class Meta:
        model = DeviceDataPerYear
        fields = (
        'year',
        # 'id',
        # 'user_id',
        'electrical_value',
        'electrical_price',
        'water_value',
        'water_price',
        'fuel_value',
        'fuel_price',
        'co2_value',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'get_data_date',
        'device_id',
        )


# Jクレジット申請のシリアライザー
class JCreditApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JCreditApplication
        fields = (
        "application_date",
        "member_name",
        "member_postal_code",
        "member_address",
        "member_phone_number",
        "installation_postal_code",
        "installation_address",
        "keidanren_carbon_neutral_participation",
        "energy_conservation_law_specified_business_number",
        "global_warming_countermeasures_specified_emitter_code",
        "base_manufacturer_name",
        "base_model",
        "base_quantity",
        "base_output",
        "base_unit_heat_gen_of_fossil_fuel_in_base_boiler",
        "base_efficiency_percentage",
        "base_efficiency_of_standard_equipment_percentage",
        "base_fuel_type",
        "base_legal_service_life_years",
        "base_installation_date",
        "base_operation_end_date",
        "base_years_of_operation",
        "updated_manufacturer_name",
        "updated_model",
        "updated_quantity",
        "updated_unique_number",
        "updated_output",
        "updated_unit_heat_gen_of_fossil_fuel_in_base_boiler",
        "updated_efficiency_percentage",
        "updated_fuel_type",
        "eval_investment_recovery_years",
        "eval_total_investment_amount",
        "eval_subsidy_amount",
        "eval_net_investment_amount",
        "eval_running_cost_before_implementation",
        "eval_running_cost_after_implementation",
        "eval_baseline_fuel_unit_price_per_month",
        "eval_post_implementation_fuel_unit_price_per_month",
        "eval_existing_maintenance_cost_per_year",
        "eval_post_implementation_maintenance_cost_per_year",
        "eval_documentation",
        "eval_subsidy_name",
        "eval_granting_organization_of_subsidy",
        "eval_domestically_implemented_in_japan",
        "operating_start_date",
        "certify_start_date",
        "certify_end_date",
        "requirement_implemented_in_japan",
        "requirement_project_execution_date",
        "requirement_certification_start_date",
        "requirement_equipment_efficiency_higher_than_standard",
        "requirement_additivity",
        "unit_heat_gen_of_fossil_fuels_in_base_boiler",
        "co2_per_unit_heat_ge_fuels_in_base_boiler",
        "unit_heat_gen_of_fuel_used_in_boiler_after_project_exec",
        "co2_per_unit_heat_ge_fuels_used_in_boiler_after_exec",
        "monitoring_period_in_months",
        "monitoring_measurement_value_of_fuel_consumption",
        "monitoring_classification",
        "monitoring_measurement_error_rate_in_c",
        "monitoring_final_value",
        )

class MonthlyCostTargetSerializer(serializers.ModelSerializer):
    target_type = serializers.ChoiceField(choices=MonthlyCostTarget.TargetType.choices)

    def validate_target_value(self, value):
        if value < 0:
            raise serializers.ValidationError("目標値は0以上である必要があります。")
        return value

    class Meta:
        model = MonthlyCostTarget
        exclude = (
            'user_id',
            'created_at',
            'updated_at'
        )

class DailyEconomicActivityAmountSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = DailyEconomicActivityAmount
        fields = ['company_id', 'value', 'activity_date']

class EconomicActivityUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicActivityUnit
        fields = ['id', 'name']

class DataStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataStructure
        fields = ['id', 'ancestor', 'descendant', 'depth', 'is_root']

    ancestor = EntitySerializer()
    descendant = EntitySerializer()
    is_root = serializers.SerializerMethodField()

    def get_is_root(self, obj):
        return obj.ancestor == obj.descendant and obj.ancestor.company.root_entity == obj.ancestor

class EntitiesDataPerHourSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    date = serializers.IntegerField()
    hour = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.IntegerField()
    water_value = serializers.FloatField()
    water_price = serializers.IntegerField()
    fuel_value = serializers.FloatField()
    fuel_price = serializers.IntegerField()
    co2_value = serializers.FloatField()
    co2_price = serializers.IntegerField()
    get_data_date = serializers.DateTimeField()
    entity_id = serializers.UUIDField()
    fuel_unit = serializers.CharField()

class EntitiesDataPerDateSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    date = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.IntegerField()
    water_value = serializers.FloatField()
    water_price = serializers.IntegerField()
    fuel_value = serializers.FloatField()
    fuel_price = serializers.IntegerField()
    co2_value = serializers.FloatField()
    co2_price = serializers.IntegerField()
    get_data_date = serializers.DateTimeField()
    entity_id = serializers.UUIDField()
    fuel_unit = serializers.CharField()

class EntitiesDataPerMonthSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.IntegerField()
    water_value = serializers.FloatField()
    water_price = serializers.IntegerField()
    fuel_value = serializers.FloatField()
    fuel_price = serializers.IntegerField()
    co2_value = serializers.FloatField()
    co2_price = serializers.IntegerField()
    get_data_date = serializers.DateTimeField()
    entity_id = serializers.UUIDField()
    fuel_unit = serializers.CharField()

class EntitiesDataPerYearSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    electrical_value = serializers.FloatField()
    electrical_price = serializers.IntegerField()
    water_value = serializers.FloatField()
    water_price = serializers.IntegerField()
    fuel_value = serializers.FloatField()
    fuel_price = serializers.IntegerField()
    co2_value = serializers.FloatField()
    co2_price = serializers.IntegerField()
    get_data_date = serializers.DateTimeField()
    entity_id = serializers.UUIDField()
    fuel_unit = serializers.CharField()

class UnitPriceHistorySerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = UnitPriceHistory
        fields = ['id', 'name', 'field', 'company', 'company_id', 'before', 'after', 'created_at']

class UserEntityPermissionSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user', queryset=User.objects.all(), write_only=True)
    entity_id = serializers.PrimaryKeyRelatedField(
        source='entity', queryset=Entity.objects.all(), write_only=True)

    user = UserSerializer(read_only=True)
    entity = EntitySerializer(read_only=True)

    class Meta:
        model = UserEntityPermission
        fields = ['id', 'user', 'entity', 'user_id', 'entity_id']

class CsvUploadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvUploadHistory
        fields = ['id', 'company', 'file_name', 'size_bytes', 'uploaded_at']
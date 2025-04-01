import hashlib
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import FileResponse, HttpResponseRedirect
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .function_create_csv_response import create_minutely_channel_csv_response
from .function_jcredit_excel import generate_excel
from .models import (AnnualPlanValues, CarbonFootprint, ChannelAdapter,
                     Co2EmissionsFactor,
                     DailyEconomicActivityAmount, Data, DataPerDate,
                     DataPerHour, DataPerMonth, DataPerYear, DataStructure,
                     DataType, Device, DeviceDataPerDate, DeviceDataPerHour,
                     DeviceDataPerMonth, DeviceDataPerYear, DeviceUnitPrice,
                     EconomicActivityType, EconomicActivityUnit, Entity,
                     EnvironmentalType, Gateway, GatewayMaster,
                     GatewayRegistration, GatewayStartdate, 
                     JCreditApplication,
                     LiquidType, MonthlyCostTarget, PushLogApi,
                     RegisteredLimit, Unit,
                     UnitPriceHistory, UserEntityPermission, CsvUploadHistory)
from users.models import User
from django.urls import reverse
# Register your models here.




# admin.site.unregister(User)
# admin.site.unregister(Group)
admin.site.site_title = 'IHI 可視化PF'
admin.site.site_header = 'IHI 可視化PF'
admin.site.index_title = 'メニュー'


@admin.register(DataPerHour)
class DataPerHourAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'pushlog_api'
        )
        list_editable = (
        'water_value',
        'fuel_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        ['get_data_date', DateRangeFilter],
        )
        ordering = ('-get_data_date',)
        readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs', )



@admin.register(DataPerDate)
class DataPerDateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'pushlog_api'
        )
        list_editable = (
        'water_value',
        'fuel_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        ['get_data_date', DateRangeFilter],
        )
        ordering = ('-get_data_date',)
        readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs')



@admin.register(DataPerMonth)
class DataPerMonthAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'pushlog_api'
        )

        list_editable = (
        'water_value',
        'fuel_value',
        'energy_saving_value',
        'renewal_energy_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        ['get_data_date', DateRangeFilter],
        )
        ordering = ('-get_data_date',)
        # readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs')

@admin.register(DataPerYear)
class DataPerYearAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'pushlog_api'
        )

        list_editable = (
        'water_value',
        'fuel_value',
        'energy_saving_value',
        'renewal_energy_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        ['get_data_date', DateRangeFilter],
        )
        ordering = ('-get_data_date',)
        readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs')


@admin.register(DeviceDataPerHour)
class DeviceDataPerHourAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'device_id',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'get_data_date',
        'pushlog_api'
        )
        list_editable = (
        'water_value',
        'fuel_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        'device_id',
        ['get_data_date', DateRangeFilter]
        )
        ordering = ('-get_data_date',)
        readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs')

@admin.register(DeviceDataPerDate)
class DeviceDataPerDateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'device_id',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'pushlog_api'
        )
        list_editable = (
        'water_value',
        'fuel_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        'device_id',
        ['get_data_date', DateRangeFilter]
        )
        ordering = ('-get_data_date',)
        readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs')

@admin.register(DeviceDataPerMonth)
class DeviceDataPerMonthAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'device_id',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'pushlog_api'
        )

        list_editable = (
        'water_value',
        'fuel_value',
        'energy_saving_value',
        'renewal_energy_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        'device_id',
        ['get_data_date', DateRangeFilter]
        )
        ordering = ('-get_data_date',)
        readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs')

@admin.register(DeviceDataPerYear)
class DeviceDataPerYearAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'get_data_date',
        'device_id',
        'electrical_value',
        'water_value',
        'fuel_value',
        'co2_value',
        'electrical_price',
        'water_price',
        'fuel_price',
        'co2_price',
        'utility_costs',
        'energy_saving_value',
        'renewal_energy_value',
        'pushlog_api'
        )

        list_editable = (
        # 'electrical_value',
        'water_value',
        'fuel_value',
        # 'co2_value',
        # 'co2_price',
        # 'user_id',
        'energy_saving_value',
        'renewal_energy_value',
        )

        search_fields = (
        'id',
        )
        list_filter = (
        'device_id',
        ['get_data_date', DateRangeFilter]
        )
        ordering = ('-get_data_date',)
        readonly_fields = ('electrical_price','water_price','fuel_price','co2_price','created_at', 'utility_costs')



@admin.register(EnvironmentalType)
class EnvironmentalTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'name',
        'id',
        'created_at',
        )
        search_fields = (
        'name',
        'created_at',
        )

def fetch_pushlog_data_action(modeladmin, request, queryset):
       if queryset.count() != 1:
           modeladmin.message_user(request, "1つのデバイスを選択してください", level='ERROR')
           return
       device = queryset.first()
       return HttpResponseRedirect(reverse('fetch_pushlog_data', args=[device.id]))

fetch_pushlog_data_action.short_description = "PushLog APIからデータを取得する"

@admin.register(Device)
class DeviceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
        'name',
        'data_source_name',
        'pushlog_api',
        # 'device_number',
        'unit_id',
        'economic_activity_type_id',
        'enable_data_collection',
        'id',
        'pushlog_unique_id',
        'is_instantaneous',

        'gateway_id',
        'created_at',
        )
        search_fields = (
        'created_at',
        )
        list_filter = (
        'pushlog_api',
        'gateway_id',
        )
        actions = [fetch_pushlog_data_action]


# @admin.register(MDevice)
# class MDeviceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
#     list_display = (
#         "name",
#         "device_number",
#         "created_at",
#     )
#     search_fields = (
#         "name",
#         "device_number"
#         "created_at",
#     )


# @admin.register(DeviceType)
# class DeviceTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
#         list_display = (
#         'name',
#         'id',
#         'created_at',
#         )
#         search_fields = (
#         'name',
#         'created_at',
#         )


@admin.register(JCreditApplication)
class JCregitRegisterationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
        list_display = (
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
        search_fields = (
        'application_date',
        'member_name',
        'member_postal_code',
        'member_address',
        'created_at',
        )

        # エクセルダウンロード
        def generate_and_download_excel(self, request, queryset):
                file_path = generate_excel()
                response = FileResponse(open(file_path, 'rb'))
                response['Content-Disposition'] = 'attachment; filename="download_j_credit.xlsx"'  # ダウンロード時のファイル名を設定
                return response

        generate_and_download_excel.short_description = "エクセル出力(選択状態に依らず全件出力)"

        # 指定行のうち、１つ目の行を100こ複製する
        def copy_100row(self, request, queryset):
                for i in range(100):
                        row = queryset[0]
                        row.pk = None
                        row.save()
        copy_100row.short_description = "指定行を100回コピー"

        actions = [generate_and_download_excel, copy_100row]


@admin.register(DeviceUnitPrice)
class DeviceUnitPriceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "electric_unit_price",
        "water_unit_price",
        "fuel_unit_price",
        "co2_unit_price",
        "electric_unit_co2",
        "water_unit_co2",
        "fuel_unit_co2",
        "created_at",
        "updated_at",
    )

@admin.register(MonthlyCostTarget)
class MonthlyCostTargetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "year",
        "month",
        "target_type",
        "target_value",
        "target_price",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "company",
        "year",
        "month",
        "target_type",
)

@admin.register(Gateway)
class GatewayAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "model",
        "is_activated",
        "firmware_version",
        "pushlog_api",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "pushlog_api",
    )

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "environmental_type_id",
        "created_at",
        "updated_at",
    )

@admin.register(EconomicActivityType)
class EconomicActivityTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "company",
    )

@admin.register(DailyEconomicActivityAmount)
class DailyEconomicActivityAmountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "value",
        "activity_date",
        "created_at",
        "updated_at",
    )

@admin.register(EconomicActivityUnit)
class EconomicActivityUnitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
        "updated_at",
    )

class PushLogApiAdminForm(forms.ModelForm):
    class Meta:
        model = PushLogApi
        fields = '__all__'

    def clean_key(self):
        key = self.cleaned_data.get('key')
        if key:
            pepper = settings.ENCRYPTION_KEY
            hashed_key = hashlib.sha256((key + pepper).encode()).hexdigest()

            if PushLogApi.objects.filter(hashed_key=hashed_key).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('登録済みのAPIキーです')

        return key

@admin.register(PushLogApi)
class PushLogApiAdmin(admin.ModelAdmin):
    form = PushLogApiAdminForm
    list_display = (
        "id",
        # "company",
        "created_at",
        "updated_at",
    )
    readonly_fields = ('hashed_key',)

@admin.register(LiquidType)
class LiquidTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "created_at",
        "updated_at",
    )


def export_to_csv(modeladmin, request, queryset):
    company_id = request.GET.get('entity__company__id__exact')
    if request.GET.get('get_data_at__range__gte_0') and request.GET.get('get_data_at__range__gte_1'):
        start_datetime_str = request.GET.get('get_data_at__range__gte_0') + ' ' + request.GET.get('get_data_at__range__gte_1')
    else:
        raise Exception('開始日時を指定してください。')

    if request.GET.get('get_data_at__range__lte_0') and request.GET.get('get_data_at__range__lte_1'):
        end_datetime_str = request.GET.get('get_data_at__range__lte_0') + ' ' + request.GET.get('get_data_at__range__lte_1')
    else:
        raise Exception('終了日時を指定してください。')
    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S').replace(second=0, microsecond=0).astimezone(timezone.utc)
    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S').replace(second=0, microsecond=0).astimezone(timezone.utc)

    return create_minutely_channel_csv_response(company_id, start_datetime, end_datetime)

export_to_csv.short_description = "指定期間の1分周期のデータをCSVとしてエクスポート"


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_type",
        "value_formatted",
        "price_formatted",
        "data_type",
        "entity",
        "get_data_at"
    )
    list_filter = (
        "entity__company",
        ('get_data_at', DateTimeRangeFilter),
        'data_type',
        "date_type",
        "entity",
    )
    actions = [export_to_csv]

    def value_formatted(self, obj):
        return round(obj.value, 10) if obj.value is not None else None
    value_formatted.short_description = f"{Data._meta.get_field('value').verbose_name}" # '値'

    def price_formatted(self, obj):
        return round(obj.price, 10) if obj.price is not None else None
    price_formatted.short_description = f"{Data._meta.get_field('price').verbose_name}" # '金額'

    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'export_to_csv':
            if request.GET.get('entity__company__id__exact') is None:
                self.message_user(request, "右側メニューで企業を選択してください。", level=messages.ERROR)
                return HttpResponseRedirect(request.get_full_path())
            if not request.GET.get('get_data_at__range__gte_0') or not request.GET.get('get_data_at__range__gte_1') \
                    or not request.GET.get('get_data_at__range__lte_0') or not request.GET.get('get_data_at__range__lte_1'):
                self.message_user(request, "右側メニューで取得日時の開始と終了を指定してください。", level=messages.ERROR)
                return HttpResponseRedirect(request.get_full_path())
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Data.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(u.id)})
                request.POST = post
        return super(DataAdmin, self).changelist_view(request, extra_context)

@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "company",
    )
    list_filter = (
        "company",
    )

@admin.register(DataStructure)
class DataStructureAdmin(admin.ModelAdmin):
    list_display = (
        "ancestor",
        "descendant",
        "depth",
    )
    list_filter = (
        "ancestor__company",
    )

# 単価変更履歴
@admin.register(UnitPriceHistory)
class UnitPriceHistoryAdmin(admin.ModelAdmin):
    # 一覧表示の項目
    list_display = (
        "name",
        "company",
        "display_before",
        "display_after",
        "created_at",
        "display_id",
    )
    # 編集画面で書き込み禁止項目
    readonly_fields = ('created_at',)
    # 初期状態は、最新の日時順に表示
    ordering = ('-created_at',)
    # 絞り込みをさせる項目
    list_filter = ('name', 'company', 'created_at',)
    # 一覧表示でソートさせない＆見出しは元のまま
    def display_before(self, obj):
        return obj.before
    display_before.short_description = f"{UnitPriceHistory._meta.get_field('before').verbose_name}" # '変更前の値'
    def display_after(self, obj):
        return obj.after
    display_after.short_description = f"{UnitPriceHistory._meta.get_field('after').verbose_name}"   # '変更後の値'
    def display_id(self, obj):
        return obj.id
    display_id.short_description = f"{UnitPriceHistory._meta.get_field('id').verbose_name}"

@admin.register(UserEntityPermission)
class UserEntityPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "entity",
    )
    list_filter = (
        "user",
        "entity",
    )

@admin.register(ChannelAdapter)
class ChannelAdapterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_id",
        # "entity_id",

        "graph_no",
        "graph_name",

        "device_number",

        "equation_str",
        "utility_cost_price",
        "co2_emissions_current",
        "co2_emissions_baseline",
        "co2_emissions_improvement_rate",
        "is_co2_emissions_baseline",
        
        "created_at",
        "updated_at",
    )
    def graph_no(self, obj):
        return obj.channel_no
    graph_no.short_description = f"{ChannelAdapter._meta.get_field('channel_no').verbose_name}"
    def graph_name(self, obj):
        return obj.channel_name
    graph_name.short_description = f"{ChannelAdapter._meta.get_field('channel_name').verbose_name}"

@admin.register(GatewayStartdate)
class GatewayStartdateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_id",
        "gateway_id",
        "display_started_at",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "company_id",
        "gateway_id",
    )
    def display_started_at(self, obj):
        if isinstance(obj.started_at, datetime):
            return obj.started_at.date()
        return obj.started_at
    display_started_at.short_description = f"{GatewayStartdate._meta.get_field('started_at').verbose_name}"

@admin.register(AnnualPlanValues)
class AnnualPlanValuesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_id",
        "utility_cost", 
        "utility_cost_reduce", 
        "electric", 
        "electric_reduce", 
        "co2_emissions", 
        "co2_emissions_reduce", 
        "carbon_credit", 
        "carbon_credit_price", 
        "created_at",
        "updated_at",
    )

@admin.register(RegisteredLimit)
class RegisteredLimitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_id",
        "user_limit",
        "user_active",
        "gateway_limit",
        "gateway_active",
        "created_at",
        "updated_at",
    )
    def user_active(self, obj):
        company_id = obj.company_id.id
        try:
            user_count = User.objects.filter(company_id_id=company_id).count()
        except:
            user_count = 0
        try:
            active_user_count = User.objects.filter(company_id_id=company_id, is_active=True, is_locked=False).count()
        except:
            active_user_count = 0
        return f"{user_count} / {active_user_count}"
    user_active.short_description = "登録数 / アクティブ数"

    def gateway_active(self, obj):
        company_id = obj.company_id.id
        # 登録数
        try:
            gateway_count = GatewayRegistration.objects.filter(company_id=company_id).count()
        except:
            gateway_count = 0

        # 稼働数：API呼び出しを行なってconnectを確認する。Exceptionが発生したら０になる
        operations_count = 0
        try:
            # operations_count = ChannelAdapter.objects.filter(company_id=company_id).count()
            # operations_count = Device.objects.filter(channeladapter__company_id=company_id).values('gateway_id').distinct().count()
            gateway_registrations = GatewayRegistration.objects.filter(company_id=company_id)

            for instance in gateway_registrations:
                gateway_master = instance.gateway_master
                if gateway_master and gateway_master.connected:
                    operations_count += 1
        except:
            pass
        return f"{gateway_count} / {operations_count}"
    gateway_active.short_description = "登録数 / 稼働数"

@admin.register(GatewayMaster)
class GatewayMasterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gateway_type",
        "gateway_id",
        "license_type",
        "license_limit",
        "created_at",
        "updated_at",
    )

@admin.register(GatewayRegistration)
class GatewayRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_id",
        "alt_name",
        "gateway_master",
        "created_at",
        "updated_at",
    )

@admin.register(CarbonFootprint)
class CarbonFootprintAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'company_id', 
        'process_name', 
        'channel_name', 
        'start_date', 
        'end_date', 
        'electric_value', 
        'co2_emissions', 
        'scope_no'
    )

@admin.register(Co2EmissionsFactor)
class Co2EmissionsFactorsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'no',
        'name',
        'factor',
    )

@admin.register(CsvUploadHistory)
class CsvUploadHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'company_id',
        'file_name',
        'uploaded_at',
    )
    list_filter = (
        'company_id',
    )
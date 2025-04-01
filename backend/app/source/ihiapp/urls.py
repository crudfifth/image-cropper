# coding: utf-8

import imp

from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

from .views import (AnnualPlanValuesView,
                    CarbonFootprintViewSet, CarbonFootprintChannelViewSet,
                    CarbonFootprintKgViewSet, CarbonFootprintScopeViewSet,
                    ChannelAdapterGatewayViewSet, ChannelAdapterNameView,
                    ChannelAdapterViewSet, ChDataPerDateViewSet,
                    ChDataPerHourViewSet, ChDataPerMinuteViewSet,
                    ChReductionDataPerDateViewSet,
                    Co2EmissionsFactorsViewSet, CSVUploadView,
                    DailyEconomicActivityAmountViewSet, DataPerDateViewSet,
                    DataPerHourViewSet, DataPerMonthViewSet,
                    DataPerYearViewSet, DeviceAllListViewSet,
                    DeviceDataPerDateViewSet, DeviceDataPerHourViewSet,
                    DeviceDataPerMonthViewSet, DeviceDataPerYearViewSet,
                    DeviceDataViewSet, DeviceDetailViewSet, DeviceListViewSet,
                    DeviceTypeListView, DeviceUnitPriceListView,
                    DeviceUnitPriceUpdateDestroyView,
                    EconomicActivityAmountUpdateView,
                    EconomicActivityTypeViewSet, EconomicActivityUnitViewSet,
                    EntitiesDataPerDateViewSet, EntitiesDataPerHourViewSet,
                    EntitiesDataPerMonthViewSet, EntitiesDataPerYearViewSet,
                    GatewayDetailView, GatewayListView, 
                    GatewayRegistrationViewSet, GatewayStartdateView,
                    JCreditApplicationViewSet, LatestUnitPriceView,
                    LiquidTypeListView, MDeviceViewSet,
                    MinutelyDataCSVDownload, MonthlyCostPredictionView,
                    MonthlyCostTargetDetailUpdateAPIView,
                    MonthlyCostTargetListAPIView, 
                    PredictionCarbonCreditViewSet, PredictionCO2EmissionsViewSet,
                    PredictionReductionCO2EmissionsViewSet, PredictionReductionElectricalViewSet,
                    PredictionReductionUtilityCostsViewSet, 
                    PredictionElectricalViewSet, PredictionUtilityCostsViewSet,
                    ReductionCO2EmissionsViewSet, ReductionElectricalViewSet,
                    ReductionUtilityCostsViewSet,
                    RegisteredGatewayCountView, RegisteredUserCountView, 
                    UnitDetailView, UnitListView,
                    UnitPriceHistoryView, ValuesCarbonCreditViewSet,
                    ValuesCO2EmissionsViewSet, ValuesElectricalViewSet,
                    ValuesUtilityCostsViewSet, YearlyCostPredictionView, CsvUploadHistoryListView,
                    HourlyDataCSVDownloadView, DailyDataCSVDownloadView,
                    fetch_pushlog_data)



schema_view = get_schema_view(title='Addressess API',
                              url='https://192.168.132.129/api/',
                              renderer_classes=[JSONOpenAPIRenderer]
                              )


# ルーターのインスタンスを生成
# TODO:廃止予定：ここから
router_devices = routers.DefaultRouter(trailing_slash=False)
router_jcredit = routers.DefaultRouter(trailing_slash=False)
router_mdevices = routers.DefaultRouter()
# TODO:廃止予定：ここまで
router_data = routers.DefaultRouter(trailing_slash=False)
router_chdata = routers.DefaultRouter(trailing_slash=False)
router_economic_activity_types = routers.DefaultRouter()
router_economic_activity_amounts = routers.DefaultRouter()
router_economic_activity_units = routers.DefaultRouter()
router_entities = routers.DefaultRouter(trailing_slash=False)

# ルーターにURLを登録
# TODO:廃止予定：ここから
router_devices.register(r'hours', DeviceDataPerHourViewSet, basename='DeviceDataPerHour')
router_devices.register(r'dates', DeviceDataPerDateViewSet, basename='DeviceDataPerDate')
router_devices.register(r'months', DeviceDataPerMonthViewSet, basename='DeviceDataPerMonth')
router_devices.register(r'years', DeviceDataPerYearViewSet, basename='DeviceDataPerYear')
router_devices.register(r'list', DeviceListViewSet, basename='DeviceList')              # ←【注意！】このAPIだけは、Techでは使っている！
router_devices.register(r'all-list', DeviceAllListViewSet, basename='DeviceAllList')    # IHI様２次開発要求仕様向け
router_devices.register(r'', DeviceDetailViewSet, basename='DeviceDetail')
router_jcredit.register(r'application', JCreditApplicationViewSet, basename='JCreditApplication')
router_mdevices.register('', MDeviceViewSet)
# TODO:廃止予定：ここまで

router_data.register(r'hours', DataPerHourViewSet, basename='DataPerHour')
router_data.register(r'dates', DataPerDateViewSet, basename='DataPerDate')
router_data.register(r'months', DataPerMonthViewSet, basename='DataPerMonth')
router_data.register(r'years', DataPerYearViewSet, basename='DataPerYear')
router_data.register(r'', DeviceDataViewSet, basename='DeviceData')
router_chdata.register(r'minutes', ChDataPerMinuteViewSet, basename='DataPerMinute')
router_chdata.register(r'hours', ChDataPerHourViewSet, basename='DataPerHour')
router_chdata.register(r'dates', ChDataPerDateViewSet, basename='DataPerDate')
router_economic_activity_types.register(r'', EconomicActivityTypeViewSet, basename='EconomicActivityType')
router_economic_activity_amounts.register(r'', DailyEconomicActivityAmountViewSet, basename='DailyEconomicActivityAmount')
router_economic_activity_units.register(r'', EconomicActivityUnitViewSet, basename='EconomicActivityUnit')
router_entities.register(r'hours', EntitiesDataPerHourViewSet, basename='EntitiesDataPerHour')
router_entities.register(r'dates', EntitiesDataPerDateViewSet, basename='EntitiesDataPerDate')
router_entities.register(r'months', EntitiesDataPerMonthViewSet, basename='EntitiesDataPerMonth')
router_entities.register(r'years', EntitiesDataPerYearViewSet, basename='EntitiesDataPerYear')

urlpatterns = [
    # TODO:廃止予定：ここから
    path('channel/', ChannelAdapterNameView.as_view(), name='channel-adapter-info'),
    path('channel_adapters/', ChannelAdapterViewSet.as_view({'get': 'list'})),   # , 'post': 'create'
    path('channel_adapters/<str:company_id>/<int:graph_no>/', ChannelAdapterViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('channel_adapters_gateway/', ChannelAdapterGatewayViewSet.as_view({'get': 'list'})),   # , 'post': 'create'
    path('channel_data/', include(router_chdata.urls)),
    path('device/', include(router_devices.urls)),
    path('mdevices/', include(router_mdevices.urls)),
    path('jcredit/', include(router_jcredit.urls)),
    # TODO:廃止予定：ここまで

    # 常時データ表示領域（右の年月日指定に依存しない）：電力量、光熱費、CO2排出量、カーボンクレジット料 X 実績値、予測値
    path('values_electrical/<str:company_id>/', ValuesElectricalViewSet.as_view({'get': 'retrieve'})),
    path('values_utility_costs/<str:company_id>/', ValuesUtilityCostsViewSet.as_view({'get': 'retrieve'})),
    path('values_co2emissions/<str:company_id>/', ValuesCO2EmissionsViewSet.as_view({'get': 'retrieve'})),
    path('values_carbon_credit/<str:company_id>/', ValuesCarbonCreditViewSet.as_view({'get': 'retrieve'})),
    path('reduction_electrical/<str:company_id>/', ReductionElectricalViewSet.as_view({'get': 'retrieve'})),
    path('reduction_utility_costs/<str:company_id>/', ReductionUtilityCostsViewSet.as_view({'get': 'retrieve'})),
    path('reduction_co2emissions/<str:company_id>/', ReductionCO2EmissionsViewSet.as_view({'get': 'retrieve'})),

    path('prediction_electrical/<str:company_id>/', PredictionElectricalViewSet.as_view({'get': 'retrieve'})),
    path('prediction_utility_costs/<str:company_id>/', PredictionUtilityCostsViewSet.as_view({'get': 'retrieve'})),
    path('prediction_co2emissions/<str:company_id>/', PredictionCO2EmissionsViewSet.as_view({'get': 'retrieve'})),
    path('prediction_carbon_credit/<str:company_id>/', PredictionCarbonCreditViewSet.as_view({'get': 'retrieve'})),
    path('prediction_reduction_electrical/<str:company_id>/', PredictionReductionElectricalViewSet.as_view({'get': 'retrieve'})),
    path('prediction_reduction_utility_costs/<str:company_id>/', PredictionReductionUtilityCostsViewSet.as_view({'get': 'retrieve'})),
    path('prediction_reduction_co2emissions/<str:company_id>/', PredictionReductionCO2EmissionsViewSet.as_view({'get': 'retrieve'})),

    # カーボンフットプリント画面
    path('carbon_footprint_kg/<str:company_id>/', CarbonFootprintKgViewSet.as_view({'post': 'create'})),
    path('carbon_footprint/<str:company_id>/', CarbonFootprintViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('carbon_footprint/<str:company_id>/<str:id>/', CarbonFootprintViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('carbon_footprint_channel/<str:company_id>/', CarbonFootprintChannelViewSet.as_view({'get': 'list'})),
    path('carbon_footprint_scope/<str:company_id>/', CarbonFootprintScopeViewSet.as_view({'get': 'retrieve'})),

    # 登録数（ユーザー、ゲートウェイ：登録上限数、登録数、稼働数）
    path('registered_user_count/<str:company_id>/', RegisteredUserCountView.as_view()),
    path('registered_gateway_count/<str:company_id>/', RegisteredGatewayCountView.as_view()),

    # ゲートウェイ追加画面
    path('gateway_registration/', GatewayRegistrationViewSet.as_view({'get': 'list'})),
    path('gateway_registration/<str:company_id>/<str:gateway_id>/', GatewayRegistrationViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'post': 'create'})),

    # ユーザー設定画面：年間計画値
    path('annual_plan_values/<str:company_id>/', AnnualPlanValuesView.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'post': 'create'})),
    # ユーザー設定画面：ゲートウェイ利用開始日
    path('gateway_startdate/<str:company_id>/<int:gateway_id>/', GatewayStartdateView.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'post': 'create'})),

    path('graph_adapters/', ChannelAdapterViewSet.as_view({'get': 'list'})),
    path('graph_adapters/<str:company_id>/<int:graph_no>/', ChannelAdapterViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('graph_adapters_gateway/', ChannelAdapterGatewayViewSet.as_view({'get': 'list'})),

    # トレンドグラフ：グラフごとのデータ
    path('graph_data/', include(router_chdata.urls)),
    # トレンドグラフ（日、電力削減量・光熱削減費・CO2削減量）
    path('graph_data_date_reduction/', ChReductionDataPerDateViewSet.as_view({'get': 'list'})),

    # 表示画面：CO2排出量係数の一覧テーブル
    path('co2emissions_factors/', Co2EmissionsFactorsViewSet.as_view({'get': 'list'})),

    path('data/', include(router_data.urls)),
    path('data/predictions/monthly', MonthlyCostPredictionView.as_view(), name='MonthlyCostPrediction'),
    path('data/predictions/yearly', YearlyCostPredictionView.as_view(), name='YearlyCostPrediction'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('monthly_cost_targets/', MonthlyCostTargetListAPIView.as_view(), name='MonthlyCostTargetsList'),
    path('monthly_cost_targets/<str:company_id>/<int:year>/<int:month>/<str:target_type>/', MonthlyCostTargetDetailUpdateAPIView.as_view(), name='MonthlyCostTargetsDetailUpdate'),
    path('gateways/', GatewayListView.as_view(), name='GatewayList'),
    path('gateways/<str:id>/', GatewayDetailView.as_view(), name='GatewayDetail'),
    path('units/', UnitListView.as_view(), name='gateway-list'),
    path('units/<str:id>/', UnitDetailView.as_view(), name='UnitDetail'),
    path('device_types/', DeviceTypeListView.as_view(), name='DeviceTypeList'),
    path('liquid_types/', LiquidTypeListView.as_view(), name='LiquidTypeList'),
    path('device_unit_prices/', DeviceUnitPriceListView.as_view(), name='DeviceUnitPriceList'),
    path('device_unit_prices/<int:id>/', DeviceUnitPriceUpdateDestroyView.as_view(), name='DeviceUnitPriceUpdate'),
    path('economic_activity_types/', include(router_economic_activity_types.urls)),
    path('companies/<uuid:company_id>/economic_activity_amounts/<str:date>/', EconomicActivityAmountUpdateView.as_view(), name='EconomicActivityAmountUpdate'),
    path('economic_activity_amounts/', include(router_economic_activity_amounts.urls)),
    path('economic_activity_units/', include(router_economic_activity_units.urls)),

    path('entities/<uuid:entity_id>/', include(router_entities.urls)),

    path('unit_price_history/', UnitPriceHistoryView.as_view(), name='UnitPriceHistoryList'),
    path('latest_unit_price/', LatestUnitPriceView.as_view(), name='LatestUnitPrice'),
    path('companies/<uuid:company_id>/minute-data/csv/', MinutelyDataCSVDownload.as_view(), name='MinutelydataCSVDownload'),
    path('companies/<uuid:company_id>/hour-data/csv/', HourlyDataCSVDownloadView.as_view(), name='HourlydataCSVDownload'),
    path('companies/<uuid:company_id>/date-data/csv/', DailyDataCSVDownloadView.as_view(), name='HourlydataCSVDownload'),
    path('companies/<uuid:company_id>/upload-csv/', CSVUploadView.as_view(), name='upload_csv'),
    path('companies/<uuid:company_id>/csv-upload-histories/', CsvUploadHistoryListView.as_view(), name='csv-upload-history'),

    # fetch_pushlog_dataにて、device_idを受け取るため、re_pathを使用
    re_path(r'^fetch_pushlog_data/(?P<device_id>[0-9a-f-]+)/$', fetch_pushlog_data, name='fetch_pushlog_data'),
]
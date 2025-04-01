# coding: utf-8

from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

from .views import (ActualValuesViewSet,
                    AnnualPlanValuesView,
                    CarbonFootprintViewSet, CarbonFootprintChannelViewSet,
                    CarbonFootprintKgViewSet, CarbonFootprintScopeViewSet,
                    ChannelAdapterGatewayViewSet, 
                    ChannelAdapterViewSet,
                    Co2EmissionsFactorsViewSet, CSVUploadView,
                    DailyEconomicActivityAmountViewSet, 
                    EconomicActivityAmountUpdateView,
                    EconomicActivityTypeViewSet, EconomicActivityUnitViewSet,
                    GatewayRegistrationViewSet, GatewayStartdateView,
                    GraphDataSeqViewSet, GraphDataLatestViewSet, GraphDataRankingViewSet,
                    MinutelyDataCSVDownload, PredictedValuesViewSet,
                    RegisteredGatewayCountView, RegisteredUserCountView, 
                    CsvUploadHistoryListView,
                    HourlyDataCSVDownloadView, DailyDataCSVDownloadView)


schema_view = get_schema_view(title='Addressess API',
                              url='https://192.168.132.129/api/',
                              renderer_classes=[JSONOpenAPIRenderer]
                              )


# ルーターのインスタンスを生成
router_economic_activity_types = routers.DefaultRouter()
router_economic_activity_amounts = routers.DefaultRouter()
router_economic_activity_units = routers.DefaultRouter()

# ルーターにURLを登録
router_economic_activity_types.register(r'', EconomicActivityTypeViewSet, basename='EconomicActivityType')
router_economic_activity_amounts.register(r'', DailyEconomicActivityAmountViewSet, basename='DailyEconomicActivityAmount')
router_economic_activity_units.register(r'', EconomicActivityUnitViewSet, basename='EconomicActivityUnit')

urlpatterns = [
    # トレンドグラフ
    # 時系列データ：棒グラフ/折れ線グラフ
    path('graph_data_seq/', GraphDataSeqViewSet.as_view({'get': 'list'}), name='graph_data_seq'),
    # 最新値一覧：データ一覧
    path('graph_data_latest/', GraphDataLatestViewSet.as_view({'get': 'list'}), name='graph_list'),
    # 上位ランキング：円グラフ
    path('graph_data_ranking/', GraphDataRankingViewSet.as_view({'get': 'list'}), name='graph_circle'),

    ## CSVダウンロード
    path('companies/<uuid:company_id>/minute-data/csv/', MinutelyDataCSVDownload.as_view(), name='MinutelydataCSVDownload'),
    path('companies/<uuid:company_id>/hour-data/csv/', HourlyDataCSVDownloadView.as_view(), name='HourlydataCSVDownload'),
    path('companies/<uuid:company_id>/date-data/csv/', DailyDataCSVDownloadView.as_view(), name='HourlydataCSVDownload'),

    # 常時データ表示領域（グラフの年月日指定に依存しない）
    ### 実績値
    path('actual_values/', ActualValuesViewSet.as_view({'get': 'retrieve'})),
    ### 予測値
    path('predicted_values/', PredictedValuesViewSet.as_view({'get': 'retrieve'})),

    # カーボンフットプリント画面
    path('carbon_footprint_kg/<str:company_id>/', CarbonFootprintKgViewSet.as_view({'post': 'create'})),
    path('carbon_footprint/<str:company_id>/', CarbonFootprintViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('carbon_footprint/<str:company_id>/<str:id>/', CarbonFootprintViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('carbon_footprint_channel/<str:company_id>/', CarbonFootprintChannelViewSet.as_view({'get': 'list'})),
    path('carbon_footprint_scope/<str:company_id>/', CarbonFootprintScopeViewSet.as_view({'get': 'retrieve'})),

    # 表示設定画面
    ## 年間計画値
    path('annual_plan_values/<str:company_id>/', AnnualPlanValuesView.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'post': 'create'})),
    ## トレンドグラフ表示設定
    path('graph_adapters/', ChannelAdapterViewSet.as_view({'get': 'list'})),
    path('graph_adapters/<str:company_id>/<int:graph_no>/', ChannelAdapterViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('graph_adapters_gateway/', ChannelAdapterGatewayViewSet.as_view({'get': 'list'})),
    ## CO2排出量係数の一覧テーブル
    path('co2emissions_factors/', Co2EmissionsFactorsViewSet.as_view({'get': 'list'})),

    # ゲートウェイ設定画面
    path('gateway_registration/', GatewayRegistrationViewSet.as_view({'get': 'list'})),
    path('gateway_registration/<str:company_id>/<str:gateway_id>/', GatewayRegistrationViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'post': 'create'})),
    ## 利用開始日
    path('gateway_startdate/<str:company_id>/<int:gateway_id>/', GatewayStartdateView.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'post': 'create'})),
    ## 登録上限数、登録数、稼働数
    path('registered_gateway_count/<str:company_id>/', RegisteredGatewayCountView.as_view()),

    # ユーザー設定画面
    ## 登録上限数、登録数、稼働数
    path('registered_user_count/<str:company_id>/', RegisteredUserCountView.as_view()),

    # CSVアップロード
    path('companies/<uuid:company_id>/upload-csv/', CSVUploadView.as_view(), name='upload_csv'),
    path('companies/<uuid:company_id>/csv-upload-histories/', CsvUploadHistoryListView.as_view(), name='csv-upload-history'),

    #
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('economic_activity_types/', include(router_economic_activity_types.urls)),
    path('companies/<uuid:company_id>/economic_activity_amounts/<str:date>/', EconomicActivityAmountUpdateView.as_view(), name='EconomicActivityAmountUpdate'),
    path('economic_activity_amounts/', include(router_economic_activity_amounts.urls)),
    path('economic_activity_units/', include(router_economic_activity_units.urls)),

]
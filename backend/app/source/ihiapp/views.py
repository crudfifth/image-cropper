import calendar
import csv
import datetime
import io
import logging
import math
import os
import statistics
import uuid
from calendar import monthrange, isleap
from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from sympy import symbols, parse_expr
from .constants import SENDER_EMAIL
# Create your views here.
import django_filters
import pandas as pd
from config.settings import FRONTEND_URL
from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.db.models import (Case, Exists, ExpressionWrapper, F, FloatField, Func, Max,
                              OuterRef, Subquery, Sum, Value, When)
from django.db.models.functions import Cast, Coalesce
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter, OpenApiRequest,
                                   extend_schema, extend_schema_view)
from rest_framework import (filters, generics, mixins, permissions, status,
                            views, viewsets)
from rest_framework.exceptions import NotFound, APIException, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVRenderer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from users.models import CompanyUser, User

from .constants import (DATA_TYPE_CO2, DATA_TYPE_ELECTRICITY, DATA_TYPE_FUEL,
                        DATA_TYPE_WATER)
from .function_calls import PushlogApiCall
from .function_create_csv_response import create_minutely_channel_csv_response, create_hourly_channel_csv_response, create_daily_channel_csv_response
from .models import (AnnualPlanValues, CarbonFootprint,
                     ChannelAdapter, Co2EmissionsFactor, Company, 
                     DailyEconomicActivityAmount,
                     Data, DataStructure, DataType, Device, DeviceDataPerDate,
                     DeviceDataPerHour, DeviceDataPerMonth, DeviceDataPerYear,
                     DeviceType, DeviceUnitPrice, EconomicActivityType,
                     EconomicActivityUnit, Entity, Gateway,
                     GatewayMaster, GatewayRegistration, GatewayStartdate,
                     JCreditApplication,
                     LiquidType, MDevice, MonthlyCostTarget, PushLogApi,
                     RegisteredLimit, Unit,
                     UnitPriceHistory, UserEntityPermission, CsvUploadHistory)
from .serializer import (AllDeviceSerializer, AnnualPlanValuesSerializer,
                         CarbonFootprintSerializer, 
                         CarbonFootprintKgSerializer,
                         CarbonFootprintChannelSerializer,
                         CarbonFootprintScopeSerializer,
                         ChannelAdapterGatewaySerializer,
                         ChannelAdapterNameSerializer,
                         ChannelAdapterSerializer,
                         ChannelDataPerDateSerializer,
                         ChannelDataPerHourSerializer,
                         ChannelDataPerMinuteSerializer,
                         ChannelDataReductionPerDateSerializer,
                         DailyEconomicActivityAmountSerializer,
                         DataPerDateSerializer, DataPerHourSerializer,
                         DataPerMonthSerializer, DataPerYearSerializer,
                         DataStructureSerializer, DeviceDataPerDateSerializer,
                         DeviceDataPerHourSerializer,
                         DeviceDataPerMonthSerializer,
                         DeviceDataPerYearSerializer, DeviceSerializer,
                         DeviceTypeSerializer, DeviceUnitPriceSerializer,
                         EconomicActivityTypeSerializer,
                         EconomicActivityUnitSerializer,
                         EntitiesDataPerDateSerializer,
                         EntitiesDataPerHourSerializer,
                         EntitiesDataPerMonthSerializer,
                         EntitiesDataPerYearSerializer, EntitySerializer,
                         GatewaySerializer, GatewayRegistrationSerializer,
                         GatewayStartdateSerializer,
                         JCreditApplicationSerializer,
                         LiquidTypeSerializer, MDeviceSerializer,
                         MonthlyCostTargetSerializer,
                         RegisteredGatewayCountSerializer,
                         RegisteredUserCountSerializer,
                         UnitPriceHistorySerializer, UnitSerializer,
                         UserEntityPermissionSerializer, CsvUploadHistorySerializer)
from datetime import timedelta
from .forms import FetchDataForm
from .function_update_data import get_unix_time, create_instantaneous_timeseries_data, create_cumulative_timeseries_data, round_time_to_next_min, round_time_to_prev_min, INTERVAL_MINUTES, BUFFER_MINUTES
from django.contrib import messages
import threading

# 小数点第2位で丸める
class Round2(Func):
    function = 'ROUND'
    template = '%(function)s((CAST(%(expressions)s AS FLOAT))::numeric, 2)'

    @property
    def output_field(self):
        return FloatField()

# ユーザ権限の確認
# 「管理」できるユーザの判定
def is_user_manager(company_id, user_id, group):
    # ユーザ管理者
    if Company.objects.filter(id=company_id, admin_user_id=user_id).exists():
        return True
    # 企業に所属していて、管理権限を持っている
    if User.objects.filter(id=user_id, company_id_id=company_id).exists() or CompanyUser.objects.filter(user_id=user_id, company_id=company_id).exists():
        if group.filter(name__in=['ユーザー管理者', '管理権限']).exists():
            return True
    return False

# 「閲覧」できるユーザの判定
def is_user_viewer(company_id, user_id, group):
    # ユーザ管理者
    if Company.objects.filter(id=company_id, admin_user_id=user_id).exists():
        return True
    # 企業に所属していて、管理権限or閲覧権限を持っている
    if User.objects.filter(id=user_id, company_id_id=company_id).exists() or CompanyUser.objects.filter(user_id=user_id, company_id=company_id).exists():
        if group.filter(name__in=['ユーザー管理者', '管理権限', '閲覧権限']).exists():
            return True
    return False 

# 一般ユーザ
def is_user_normal(company_id, user_id):
    # 企業に所属している
    if User.objects.filter(id=user_id, company_id_id=company_id).exists() or CompanyUser.objects.filter(user_id=user_id, company_id=company_id).exists():
        return True
    return False 


# 廃止予定：ここから
# グラフ情報の取得
class ChannelAdapterNameView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        company_id = request.query_params.get("company_id", None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        graph_no = request.query_params.get("graph_no", None)
        if graph_no is None or company_id is None:
            raise Http404
        channel = ChannelAdapter.objects.filter(channel_no=graph_no, company_id_id=company_id).first()
        if channel is None:
            return Response({})
        serializer = ChannelAdapterNameSerializer(channel)

        return Response(serializer.data)
# 廃止予定：ここまで

# グラフ情報の管理
@extend_schema_view(
    list=extend_schema(
        description="GET api/v1/graph_adapters?company_id=<str:company_id>",
        responses={200: ChannelAdapterSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=str,
                location=OpenApiParameter.QUERY,
                description='UUID of the company',
                required=True,
            ),
        ],
        examples=[
            OpenApiExample(
                'Example 1',
                value=[
                    {
                        'company_id': '123e4567-e89b-12d3-a456-426614174000',
                        'graph_no': 1,
                        'graph_name': 'Graph 1',
                        'gateway_id': '590533333377616',
                        'device_no': 1,
                        'equation_str': "(x)*100",
                        'utility_cost_price': 0.2,
                        'co2_emissions_current': 0.5,
                        'co2_emissions_baseline': 0.5,
                        'co2_emissions_improvement_rate': 0.0,
                        'is_co2_emissions_baseline': True,
                    },
                ],
                summary='',
                description='',
            ),
        ],
    ),
    retrieve=extend_schema(
        description="GET api/v1/graph_adapters/<str:company_id>/<int:graph_no>/",
        responses={200: ChannelAdapterSerializer},
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=str,
                location=OpenApiParameter.PATH,
                description='UUID of the company',
                required=True,
            ),
            OpenApiParameter(
                name='graph_no',
                type=str,
                location=OpenApiParameter.PATH,
                description='No of the graph',
                required=True,
            ),
        ],
        examples=[
            OpenApiExample(
                'Example 1',
                value={
                    'company_id': '123e4567-e89b-12d3-a456-426614174000',
                    'graph_no': 1,
                    'graph_name': 'Graph 1',
                    'gateway_id': '590554295456018',
                    'device_no': 1,
                    'equation_str': '(x)*200',
                    'utility_cost_price': 0.5,
                    'co2_emissions_current': 0.5,
                    'co2_emissions_baseline': 0.0,
                    'co2_emissions_improvement_rate': 0.5,
                    'is_co2_emissions_baseline': False,
                },
                summary='',
                description='',
            ),
        ],
    ),
    partial_update=extend_schema(
        description="PATCH api/v1/graph_adapters/<str:company_id>/<int:graph_no>/",
        request=ChannelAdapterSerializer,
        responses={200: ChannelAdapterSerializer},
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=str,
                location=OpenApiParameter.PATH,
                description='UUID of the company',
                required=True,
            ),
            OpenApiParameter(
                name='graph_no',
                type=str,
                location=OpenApiParameter.PATH,
                description='No of the graph',
                required=True,
            ),
        ],
        examples=[
            OpenApiExample(
                'Example 1',
                value={
                    'company_id': '123e4567-e89b-12d3-a456-426614174000',
                    'graph_no': 1,
                    'graph_name': 'Graph 1',
                    'gateway_id': '590554295456018',
                    'device_no': 1,
                    'equation_str': '(x)*200',
                    'utility_cost_price': 0.5,
                    'co2_emissions_current': 0.5,
                    'co2_emissions_baseline': 0.0,
                    'co2_emissions_improvement_rate': 0.5,
                    'is_co2_emissions_baseline': False,
                },
                summary='A simple example',
                description='This is a simple example of a partial update request. Provide the changes as a JSON object in the request body.',
            ),
        ],
    ),
    destroy=extend_schema(
        description="DELETE api/v1/graph_adapters/<str:company_id>/<int:graph_no>/",
        responses={204: None},
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=str,
                location=OpenApiParameter.PATH,
                description='UUID of the company',
                required=True,
            ),
            OpenApiParameter(
                name='graph_no',
                type=str,
                location=OpenApiParameter.PATH,
                description='No of the graph',
                required=True,
            ),
        ],
        examples=[
            OpenApiExample(
                'Example 1',
                value=None,
                summary='A simple example',
                description='This is a simple example of a destroy request',
            ),
        ],
    ),
)
class ChannelAdapterViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ChannelAdapterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        company_id = self.kwargs.get('company_id')
        graph_no = self.kwargs.get('graph_no')
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        return ChannelAdapter.objects.get(company_id=company_id, channel_no=graph_no)

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        return ChannelAdapter.objects.filter(company_id=company_id).order_by('channel_no')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # ここで、削除する代わりに各フィールドをNoneに設定します。
        # デバイスをNoneにする際に、デバイス側のentityをNoneにする
        device = instance.device_number
        if device is not None:
            device.entity = None
            device.save()
        instance.device_number  = None
        # 他のフィールドはNoneにするだけで良い
        instance.channel_name  = ""
        instance.equation_str  = ""
        instance.utility_cost_price  = 0
        instance.co2_emissions_current  = 0
        instance.co2_emissions_baseline  = 0
        instance.co2_emissions_improvement_rate  = 0
        instance.is_co2_emissions_baseline = True       # これはデフォルト値

        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# チャンネル設定で使うGatewayの一覧の取得
@extend_schema_view(
    list=extend_schema(
        description='ユーザー設定画面で選択肢として使うGatewayの一覧を取得',
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=str,
                location=OpenApiParameter.QUERY,
                description='UUID of the company',
                required=True,
            ),
        ],
        examples=[
            OpenApiExample(
                'Example 1',
                value={
                    'gateway_id': 590229332981823,
                    'name': '電力量監視',
                    'devices': [1, 2, 3],
                    'enable_devices': [1, 2],
                    'device_names': [(1, 'デバイス 1'), (2, 'デバイス 2')]
                },
                summary='',
                description='「devices」「enable_devices」は廃止予定',
            ),
        ],
    ),
)
class ChannelAdapterGatewayViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ChannelAdapterGatewaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id

        # GatewayRegistrationから指定したcompany_idに紐づくものgateway_id一覧を取得し、そのgateway_idを持つGatewayの一覧を取得
        gateway_ids = GatewayRegistration.objects.filter(company_id_id=company_id).values_list('gateway_master__gateway_id_id', flat=True)
        return Gateway.objects.filter(id__in=gateway_ids)

# Gatewayの開始日:retrieve, update
@extend_schema_view(
    retrieve=extend_schema(
        summary="Retrieve a Gateway Startdate",
        description="Retrieves the start date of a Gateway for a specific company",
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the company",
                required=True
            ),
            OpenApiParameter(
                name="gateway_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID of the gateway",
                required=True
            ),
        ],
        responses={200: GatewayStartdateSerializer},
        examples=[
            OpenApiExample(
                "Example 1",
                value={
                    "gateway_id": "590554295456018",
                    "started_at": "2022-01-01",
                },
                summary="A simple example",
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Update a Gateway Startdate",
        description="Updates the start date of a Gateway for a specific company",
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the company",
                required=True
            ),
            OpenApiParameter(
                name="gateway_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID of the gateway",
                required=True
            ),
        ],
        request={
            "type": OpenApiTypes.OBJECT,
            "properties": {
                "started_at": {
                    "type": OpenApiTypes.DATE,
                    "description": "The start date of the gateway",
                },
            },
            "required": ["started_at"],
        },
        responses={200: GatewayStartdateSerializer},
        examples=[
            OpenApiExample(
                "Example 1",
                value={
                    "gateway_id": "590554295456018",
                    "started_at": "2022-01-01",
                },
                summary="A simple example",
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Delete a Gateway Startdate",
        description="Deletes the start date of a Gateway for a specific company",
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the company",
                required=True
            ),
            OpenApiParameter(
                name="gateway_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID of the gateway",
                required=True
            ),
        ],
        responses={204: None}
    ),
    create=extend_schema(
        summary="Create a Gateway Startdate",
        description="Creates the start date of a Gateway for a specific company",
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                description="UUID of the company",
                required=True,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name="gateway_id",
                type=str,
                description="ID of the gateway",
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        request={
            "type": OpenApiTypes.OBJECT,
            "properties": {
                "started_at": {
                    "type": OpenApiTypes.DATE,
                    "description": "The start date of the gateway",
                },
            },
            "required": ["started_at"],
        },
        responses={201: GatewayStartdateSerializer},
        examples=[
            OpenApiExample(
                "Example 1",
                value={
                    "gateway_id": "590554295456018",
                    "started_at": "2022-01-01",
                },
                summary="A simple example",
            ),
        ],
    )
)
class GatewayStartdateView(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GatewayStartdateSerializer

    def get_object(self):
        company_id = self.kwargs.get('company_id')
        gateway_id = self.kwargs.get('gateway_id')
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        return GatewayStartdate.objects.filter(company_id=company_id, gateway_id_id=gateway_id).order_by('-updated_at').first()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except GatewayStartdate.DoesNotExist:
            raise NotFound('The specified GatewayStartdate does not exist')
        try:
            serializer = self.get_serializer(instance)
        except Exception as e:
            raise APIException(str(e))
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        company_id=kwargs.get('company_id')
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        gateway_id = kwargs.get('gateway_id')
        started_at = request.data.get('started_at')
        try:
            datetime.datetime.strptime(started_at, '%Y-%m-%d')
        except ValueError:
            return Response({'status': 'Invalid date format for started_at. Expected format: YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        company = Company.objects.get(id=company_id)
        if not Gateway.objects.filter(id=gateway_id).exists():
            return Response({'status': 'Gateway object not found'}, status=status.HTTP_404_NOT_FOUND)

        if not GatewayStartdate.objects.filter(gateway_id_id=gateway_id).exists():
            # create a new GatewayStartdate object
            gateway = Gateway.objects.get(id=gateway_id)
            gateway_startdate = GatewayStartdate.objects.create(company_id=company, gateway_id=gateway, started_at=started_at)
            serializer = self.get_serializer(gateway_startdate)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Update the existing GatewayStartdate object
            gateway_startdate = GatewayStartdate.objects.get(company_id_id=company_id, gateway_id_id=gateway_id)
            gateway_startdate.started_at = started_at
            gateway_startdate.save()
            serializer = self.get_serializer(gateway_startdate)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except GatewayStartdate.DoesNotExist:
            return Response({'status': 'The specified GatewayStartdate does not exist'}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# 年間計画値
@extend_schema_view(
    create=extend_schema(
        summary="Create a new AnnualPlanValues",
        description="Creates a new AnnualPlanValues and returns the created object",
        request=AnnualPlanValuesSerializer,
        responses={status.HTTP_201_CREATED: AnnualPlanValuesSerializer},
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                description="UUID of the company",
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        examples=[
            {
                "summary": "Example 1",
                "value": {
                    "utility_cost": 1000.0,
                    "electric": 200.0,
                    "electric_reduce": 50.0,
                    "co2_emissions": 300.0,
                    "co2_emissions_reduce": 100.0,
                    "carbon_credit": 400.0,
                    "carbon_credit_price": 5000.0
                }
            }
        ]
    ),
    retrieve=extend_schema(
        summary="Retrieve an AnnualPlanValues",
        description="Retrieves the details of an existing AnnualPlanValues",
        responses={status.HTTP_200_OK: AnnualPlanValuesSerializer},
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                description="UUID of the company",
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        examples=[
            {
                "summary": "Example 1",
                "value": {
                    "utility_cost": 1000.0,
                    "electric": 200.0,
                    "electric_reduce": 50.0,
                    "co2_emissions": 300.0,
                    "co2_emissions_reduce": 100.0,
                    "carbon_credit": 400.0,
                    "carbon_credit_price": 5000.0
                }
            }
        ]
    ),
    partial_update=extend_schema(
        summary="Update an AnnualPlanValues",
        description="Updates an existing AnnualPlanValues and returns the updated object",
        request=AnnualPlanValuesSerializer,
        responses={status.HTTP_200_OK: AnnualPlanValuesSerializer},
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                description="UUID of the company",
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
        examples=[
            {
                "summary": "Example 1",
                "value": {
                    "utility_cost": 1500.0,
                    "electric": 250.0,
                    "electric_reduce": 75.0,
                    "co2_emissions": 350.0,
                    "co2_emissions_reduce": 150.0,
                    "carbon_credit": 450.0,
                    "carbon_credit_price": 5500.0
                }
            }
        ]
    ),
    destroy=extend_schema(
        summary="Delete an AnnualPlanValues",
        description="Deletes an existing AnnualPlanValues",
        responses={status.HTTP_204_NO_CONTENT: None},
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=str,
                description="UUID of the company",
                required=True,
                location=OpenApiParameter.PATH
            ),
        ],
    ),
)
class AnnualPlanValuesView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnnualPlanValuesSerializer

    def get_object(self):
        company_id = self.kwargs.get('company_id')
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        return AnnualPlanValues.objects.get(company_id_id=company_id)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except AnnualPlanValues.DoesNotExist:
            raise NotFound('The specified AnnualPlanValues does not exist')
        # except Exception as e:
        #     raise APIException(str(e))
        try:
            serializer = self.get_serializer(instance)
        except Exception as e:
            raise APIException(str(e))
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except AnnualPlanValues.DoesNotExist:
            raise NotFound('The specified AnnualPlanValues does not exist')
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError({'detail': str(e)})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except AnnualPlanValues.DoesNotExist:
            raise NotFound('The specified AnnualPlanValues does not exist')
        try:
            instance.delete()
        except Exception as e:
            raise ValidationError({'detail': str(e)})
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id')
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        company = Company.objects.get(id=company_id)
        utility_cost = request.data.get('utility_cost', 0.0)
        utility_cost_reduce = request.data.get('utility_cost_reduce', 0.0)
        electric = request.data.get('electric', 0.0)
        electric_reduce = request.data.get('electric_reduce', 0.0)
        co2_emissions = request.data.get('co2_emissions', 0.0)
        co2_emissions_reduce = request.data.get('co2_emissions_reduce', 0.0)
        carbon_credit = request.data.get('carbon_credit', 0.0)
        carbon_credit_price = request.data.get('carbon_credit_price', 0.0)

        if AnnualPlanValues.objects.filter(company_id=company).exists():
            return Response({'detail': 'AnnualPlanValues with this company_id already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # create a new AnnualPlanValuesView object
        annual_plan_values = AnnualPlanValues.objects.create(
            company_id=company,
            utility_cost=utility_cost,
            utility_cost_reduce=utility_cost_reduce,
            electric=electric, electric_reduce=electric_reduce,
            co2_emissions=co2_emissions, co2_emissions_reduce=co2_emissions_reduce,
            carbon_credit=carbon_credit, carbon_credit_price=carbon_credit_price)

        serializer = self.get_serializer(annual_plan_values)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ユーザの登録数（登録上限数、登録数、稼働数）
@extend_schema(
    parameters=[
        OpenApiParameter(
            name="company_id",
            description="UUID of the company",
            required=True,
            type=str,
            location=OpenApiParameter.PATH
        ),
    ],
    responses={
        status.HTTP_200_OK: OpenApiExample(
            "Example response",
            value={
                'user_limit': 3,
                'user_count': 2,
                'active_user_count': 1,
            },
            summary="Example of a successful response",
        ),
        status.HTTP_403_FORBIDDEN: "Permission Denied",
    },
    description="Retrieve the user limit, total user count, and active user count for a specific company.",
)
class RegisteredUserCountView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RegisteredUserCountSerializer

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        company = Company.objects.filter(id=company_id).first()
        user_id = self.request.user.id
        group = self.request.user.groups.all()
        if company is None or not is_user_viewer(company_id, user_id, group):
            raise PermissionDenied()

        try:
            user_limit = RegisteredLimit.objects.get(company_id=company_id).user_limit
        except:
            user_limit = 0
        try:
            user_count = CompanyUser.objects.filter(company_id=company_id).count()
        except:
            user_count = 0
        try:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            active_user_count = CompanyUser.objects.filter(
                company_id=company_id,
                user__is_active=True,
                user__is_locked=False,
                user__last_login__gt=thirty_days_ago
            ).count()
        except:
            active_user_count = 0

        return Response({
            'user_limit': user_limit,
            'user_count': user_count,
            'active_user_count': active_user_count,
        })

# ゲートウェイの登録数（登録上限数、登録数、稼働数）
@extend_schema(
    parameters=[
        OpenApiParameter(
            name="company_id",
            description="UUID of the company",
            required=True,
            type=str,
            location=OpenApiParameter.PATH
        ),
    ],
    responses={
        status.HTTP_200_OK: OpenApiExample(
            "Example response",
            value={
                'gateway_limit': 3,
                'gateway_count': 2,
                'operations_count': 15,
            },
            summary="Example of a successful response",
        ),
        status.HTTP_403_FORBIDDEN: "Permission Denied",
    },
    description="Retrieve the gateway limit, total gateway count, and operations count for a specific company.",
)
class RegisteredGatewayCountView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RegisteredGatewayCountSerializer

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        company = Company.objects.filter(id=company_id).first()
        user_id = self.request.user.id
        group = self.request.user.groups.all()

        # if company is None or not self.is_user_viewer1(company_id):
        if company is None or not is_user_viewer(company_id, user_id, group):
            raise PermissionDenied()

        # 登録上限数
        try:
            gateway_limit = RegisteredLimit.objects.get(company_id=company_id).gateway_limit
        except:
            gateway_limit = 0

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
                if not gateway_master:
                    raise NotFound("GatewayMaster not found")
                if gateway_master.connected:
                    operations_count += 1
        except:
            pass

        return Response({
            'gateway_limit': gateway_limit,
            'gateway_count': gateway_count,
            'operations_count': operations_count,
        })


# ゲートウェイ設定画面
# ユーザー管理者のみがアクセス可能、ユーザー管理者＝company_idのadmin_user_idとリクエストユーザーが一致
class GatewayRegistrationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = GatewayRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        company_id = self.kwargs.get('company_id')
        gateway_id = self.kwargs.get('gateway_id')
        user_id = self.request.user.id
        group = self.request.user.groups.all()
        if company_id is not None:
            if not is_user_manager(company_id, user_id, group):
                raise PermissionDenied()
        else:
            raise Http404

        # GatewayRegistrationから指定したcompany_idに紐づくものを取得し、そのGatewayMasterに紐づくGatewayがgateway_idに一致するものを取得
        gateway_registration = GatewayRegistration.objects.get(company_id_id=company_id, gateway_master__gateway_id=gateway_id)

        if not gateway_registration:
            raise Http404
        return gateway_registration

    def get_object_view(self):
        company_id = self.kwargs.get('company_id')
        gateway_id = self.kwargs.get('gateway_id')
        user_id = self.request.user.id
        group = self.request.user.groups.all()
        if company_id is not None:
            if not is_user_viewer(company_id, user_id, group):
                raise PermissionDenied()
        else:
            raise Http404

        # GatewayRegistrationから指定したcompany_idに紐づくものを取得し、そのGatewayMasterに紐づくGatewayがgateway_idに一致するものを取得
        gateway_registration = GatewayRegistration.objects.get(company_id_id=company_id, gateway_master__gateway_id=gateway_id)

        if not gateway_registration:
            raise Http404
        return gateway_registration

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        user_id = self.request.user.id
        group = self.request.user.groups.all()
        if company_id is not None:
            if not is_user_viewer(company_id, user_id, group):
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        return GatewayRegistration.objects.filter(company_id=company_id).order_by('gateway_master__gateway_id_id').order_by('created_at')

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object_view()
        except Http404:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        gateway_master = instance.gateway_master
        if not gateway_master:
            raise NotFound("GatewayMaster not found")
        gateway = gateway_master.gateway_id
        if not gateway:
            raise NotFound("Gateway not found")
        pushlogapi = gateway.pushlog_api
        if not pushlogapi:
            raise NotFound("PushlogApi not found")
        pushlogapi_call = PushlogApiCall(pushlogapi)
        status_json = pushlogapi_call.status(gateway_id=gateway.id)
        if not status_json:
            raise APIException("Failed to get status from PushlogApiCall")
        gateway_name = instance.alt_name if instance.alt_name else gateway.name
        result = {
            'type': gateway_master.gateway_type,                # 種別：'PUSHLOG'
            'name': gateway_name,                               # ゲートウェイ名
            'id': gateway.id,                                   # ゲートウェイID
            'license_limit': gateway_master.license_limit,      # 利用可能期限
            'license_type': gateway_master.license_type,        # ライセンス種別
            'signal_level': status_json.get('signalLevel', 0),  # LTE-M電波状態:0:未接続、電波状態を1:弱い~4:強いで表す
            'connected': status_json.get('connected', False),   # 接続状態
            'updated_at': status_json.get('updatedAt', None)    # 最終データ取得時間
        }
        gateway_master.connected = result['connected']
        gateway_master.save()

        serializer = self.get_serializer(result)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            gateway_registration = self.get_object()
        except Http404:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # GatewayMasterのgatewayに紐づいたDeviceのentityのCompanyをクリアする
            gateway_master = gateway_registration.gateway_master
            gateway = gateway_master.gateway_id
            if gateway:
                # gateway_idに紐づいたDeviceを取得
                devices = Device.objects.filter(gateway_id=gateway)
                for device in devices:
                    if device and device.entity:
                        # EntityのCompanyをNone
                        device.entity.company = None
                        device.entity.save()
                # gatewayに紐付いたdeviceと紐付いているChannleAdapterのdevice_numberをクリアする
                channel_adapters = ChannelAdapter.objects.filter(device_number__gateway_id=gateway)
                for channel_adapter in channel_adapters:
                    channel_adapter.device_number = None
                    channel_adapter.save()

            # gateway_id に紐づいたGatewayStartdate を削除する
            for gateway_startdate in GatewayStartdate.objects.filter(gateway_id_id=gateway.id):
                gateway_startdate.delete()

            # instance = self.get_object()
            instance = gateway_registration
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        company_id = self.kwargs.get('company_id')
        user_id = self.request.user.id
        group = self.request.user.groups.all()
        if company_id is not None:
            if not is_user_manager(company_id, user_id, group):
                raise PermissionDenied()
        else:
            raise Http404
        company = Company.objects.get(id=company_id)

        gateway_id = self.kwargs.get('gateway_id')
        gateway_name = request.data.get('gateway_name')

        # GatewayMasterに紐づいたGatewayのidがgateway_idと一致するか確認
        try:
            gateway_master = GatewayMaster.objects.get(gateway_id_id=gateway_id)
        except GatewayMaster.DoesNotExist:
            raise ValidationError('GatewayMaster with the provided gateway_id does not exist', code='ID_invalid')

        # GatewayMasterにライセンス情報が記載されていない
        if gateway_master.license_type is None or gateway_master.license_limit is None:
            raise ValidationError('GatewayMaster is not configured', code='GatewayMaster_not_configured')

        # GatewayRegistrationが既に存在するとエラー
        if GatewayRegistration.objects.filter(gateway_master=gateway_master).exists():
            raise ValidationError('GatewayRegistration with the provided gateway_id already exists', code='ID_already_in_use')

        # # gateway_nameが一致するか確認
        # if gateway_master.gateway_id.name != gateway_name:
        #     raise ValidationError('Provided gateway_name does not match with the existing one', code='Name_invalid')

        if gateway_name is None or gateway_name == "":
            raise ValidationError('gateway_name is required', code='Name_invalid')

        # GatewayRegistrationのオブジェクトを作成
        gateway_registration = GatewayRegistration.objects.create(
            company_id=company,
            alt_name=gateway_name,
            gateway_master=gateway_master
        )
        GatewayStartdate.objects.create(
            company_id=company,
            gateway_id=gateway_master.gateway_id,
            started_at=datetime.date.today()
        )
        # GatewayMasterのgatewayに紐づいたDeviceのentityのCompanyを設定する
        gateway = gateway_master.gateway_id
        if gateway:
            # gateway_idに紐づいたDeviceを取得
            devices = Device.objects.filter(gateway_id=gateway)
            for device in devices:
                if device:
                    if device.entity is None:
                        # 同名のentityがなければ新規作成、あれば使い回す
                        entity = Entity.objects.filter(name=device.pushlog_unique_id).first()
                        if entity is None:
                            device.entity = Entity.objects.create(
                                company=company,
                                name=device.pushlog_unique_id
                            )
                            data_structure = DataStructure.objects.create(
                                ancestor = device.entity,
                                descendant = device.entity,
                                depth = 0
                            )
                            device.save()
                        else:
                            entity.company = company
                            entity.save()
                            device.entity = entity
                            device.save()
                    else:
                        # EntityのCompanyを設定
                        device.entity.company = company
                        device.entity.save()

        # 登録時には、APIは呼び出さない。
        # 検索時に、API呼び出しを行い、各種Statusを更新する
        # 登録→一覧で二重にAPI呼び出しを行うのを回避するため
        # [更新]押下では、一覧を呼び出すので、そちらに集約した
        gateway = gateway_master.gateway_id
        if not gateway:
            raise NotFound("Gateway not found")
        result = {
            'type': gateway_master.gateway_type,            # 種別：'PUSHLOG'
            'name': gateway_name,                           # ゲートウェイ名
            'id': gateway.id,                               # ゲートウェイID
            'license_limit': gateway_master.license_limit,  # 利用可能期限
            'license_type': gateway_master.license_type,    # ライセンス種別
            'signal_level': 0,                              # LTE-M電波状態:0:未接続、電波状態を1:弱い~4:強いで表す
            'connected': False,                             # 接続状態
            'updated_at': None                              # 最終データ取得時間
        }

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        results = []
        queryset = self.filter_queryset(self.get_queryset())
        for gateway_registration in queryset:
            gateway_master = gateway_registration.gateway_master
            if not gateway_master:
                continue
            gateway = gateway_master.gateway_id
            if not gateway:
                continue
            pushlogapi = gateway.pushlog_api
            if not pushlogapi:
                continue
            pushlogapi_call = PushlogApiCall(pushlogapi)
            status = pushlogapi_call.status(gateway_id=gateway.id)
            gateway_name = gateway_registration.alt_name if gateway_registration.alt_name else gateway.name
            result = {
                'type': gateway_master.gateway_type,
                'name': gateway_name,
                'id': gateway.id,
                'license_limit': gateway_master.license_limit,
                'license_type': gateway_master.license_type,
                'signal_level': status.get('signalLevel', 0),
                'connected': status.get('connected', False),
                'updated_at': status.get('updatedAt', None)
            }
            gateway_master.connected = result['connected']
            gateway_master.save()
            results.append(result)

        return Response(results)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # alt_nameのみ変更
        alt_name = request.data.get('alt_name')
        if alt_name is None or alt_name == "":
            raise ValidationError('alt_name is required', code='Name_invalid')
        instance.alt_name = alt_name
        instance.save()

        return Response({'alt_name': instance.alt_name}, status=status.HTTP_200_OK)

# Graphデータの取得: 削減量：日単位のみ（旧計算方式）
class ChReductionDataPerDateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = ChannelDataReductionPerDateSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        week = self.request.query_params.get('week', None)      # weekは月の中での週番号（月曜始まり、0〜）
        company_id = self.request.query_params.get('company_id', None)
        mode = self.request.query_params.get('mode')

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            root_entity = target_company.root_entity
            if root_entity is None or not root_entity.id in all_permit_entity_ids:
                raise PermissionDenied()

        # company_idのチェック
        # TODO: ユーザ権限への対応
        if company_id is not None:
            # ユーザーが所属している企業か確認
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            # 無指定なら、ユーザの所属企業を取得
            company_id = self.request.user.company_id_id

        # 開始日終了日の計算
        # 年月がパラメータ指定されていれば絞り込む
        if year is not None and month is not None:
            year = int(year)
            month = int(month)
            if week is None:
                # week無指定　→　単純に年月で絞り込む
                if start is None and end is None:
                    start = 1
                    _, end = monthrange(year, month)
                    today = datetime.datetime.now()
                    if today.year == year and today.month == month:
                        if today.day == 1:
                          return []
                        end = today.day - 1
                # start、end指定　→　日付でさらに絞り込む
                first_date= datetime.datetime(int(year), int(month), int(start), 0, 0)
                last_date = datetime.datetime(int(year), int(month), int(end), 23, 59, 59)
            else:
                # week指定　→　指定週の範囲で絞り込む（月曜日始まり）
                first_date, last_date = get_week_range(int(year), int(month), int(week))
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)
                if yesterday < last_date:
                    last_date = yesterday
                    if first_date > last_date:
                        return []
        else:
            raise ValidationError('year, month must be specified')


        graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id)
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

        result_dict_merge = {}
        for graph_adapter in graph_adapters:
            if graph_adapter.is_co2_emissions_baseline:
                if graph_adapter.co2_emissions_baseline == 0.0:
                    reduction_coefficient = 0.0
                else:
                    reduction_coefficient = 1.0 - (graph_adapter.co2_emissions_current / graph_adapter.co2_emissions_baseline)
            else:
                reduction_coefficient = graph_adapter.co2_emissions_improvement_rate

            device = graph_adapter.device_number
            if device == None or device.entity == None or device.entity.id == None:
                continue
            entity_id = device.entity.id

            # 単価情報：光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）
            electric_unit_price = graph_adapter.utility_cost_price    
            electric_unit_co2 = graph_adapter.co2_emissions_current

            # 計算式文字列の取得
            equation_str = graph_adapter.equation_str
            if equation_str is None or equation_str == '':
                equation_str ='(x)'         # 計算式が取得できなかった場合は、xをそのまま返す

            # DATEの全データを取得
            data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE, get_data_at__range=(first_date, last_date)).order_by('get_data_at')

            aggregated_data = data_per_date.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute',
            ).annotate(
                economic_activity_value=Subquery(economic_activity_amount_query),
                electrical_value=F('value'),
            )

            result_dict = update_final_result_chdate(aggregated_data, equation_str, mode, reduction_coefficient, Data.DateType.DATE, electric_unit_price, electric_unit_co2, co2_unit_price)
            # 合成：同じ日付の場合は、electrical_value、electrical_price、co2_value、co2_priceの値を合計
            for date_key, dict_values in result_dict.items():
                if date_key in result_dict_merge:
                    result_dict_merge[date_key]['electrical_value'] = result_dict_merge[date_key].get('electrical_value', 0.0) + dict_values.get('electrical_value', 0.0)
                    result_dict_merge[date_key]['electrical_price'] = result_dict_merge[date_key].get('electrical_price', 0.0) + dict_values.get('electrical_price', 0.0)
                    result_dict_merge[date_key]['co2_value'] = result_dict_merge[date_key].get('co2_value', 0.0) + dict_values.get('co2_value', 0.0)
                    result_dict_merge[date_key]['co2_price'] = result_dict_merge[date_key].get('co2_price', 0.0) + dict_values.get('co2_price', 0.0)
                else:
                    result_dict_merge[date_key] = dict_values

        # 目標値、経済活動量の算出は内部で行う
        # その値を用いて削減量および原単位の計算を行う
        final_result = make_result(first_date, last_date, result_dict_merge, annual_plan_values, company_id, mode)

        # 年月日の昇順にソート
        result = sorted(final_result.values(), key=lambda x: (x['year'], x['month'], x['date']))

        return result

def make_result(first_date, last_date, dict_date_data, annual_plan_values, company_id, mode):
    # 結果格納領域
    result = {}

    # 原単位（経済活動量）
    economic_activity_values = {}

    # 日付分の領域を作成
    this_date = first_date
    while(this_date <= last_date):
        ymd_key = f"{this_date.year}-{this_date.month}-{this_date.day}"
        ym_key = f"{this_date.year}-{this_date.month}"
        # 結果
        result[ymd_key] = {
            'year': this_date.year,
            'month': this_date.month,
            'date': this_date.day,
            'electrical_value': 0.0,
            'electrical_price': 0.0,
            'co2_value': 0.0,
            'co2_price': 0.0,
        }
        # 経済活動量
        if ym_key not in economic_activity_values:
            economic_activity_amount = DailyEconomicActivityAmount.objects.filter(
                company_id = company_id, 
                activity_date__year = this_date.year, 
                activity_date__month = this_date.month
            ).values('value').first()
            if economic_activity_amount is not None:
                economic_activity_values[ym_key] = economic_activity_amount['value']
            else:
                economic_activity_values[ym_key] = 0.0

        this_date = this_date + datetime.timedelta(days=1)

    # 電力量のデータで上書き
    for time_key, item in dict_date_data.items():
        # 1日の実績値：電力量、光熱費、CO2排出量
        if time_key in result:
            result[time_key]['electrical_value'] = item['electrical_value']
            result[time_key]['electrical_price'] = item['electrical_price']
            result[time_key]['co2_value'] = item['co2_value']
            result[time_key]['co2_price'] = item['co2_price']

    # 年間目標値を取得するためのSubquery
    # 現状では、年に関するフィールドはないため、年指定なしで取得している
    if annual_plan_values is not None:
        annual_plan_electrical_value = annual_plan_values.electric
        annual_plan_electrical_price = annual_plan_values.utility_cost
        annual_plan_co2_value = annual_plan_values.co2_emissions
        annual_plan_co2_price = annual_plan_values.carbon_credit
    else:
        annual_plan_electrical_value = 0.0
        annual_plan_electrical_price = 0.0
        annual_plan_co2_value = 0.0
        annual_plan_co2_price = 0.0

    # 全フィールドで目標値と実績値の差分を求める
    for time_key, item in result.items():
        # 1年の日数
        year = item['year']
        days_in_year = 366 if isleap(year) else 365

        # 1日の目標値＝年間目標値/1年の日数
        day_plan_electrical_value = annual_plan_electrical_value / days_in_year
        day_plan_electrical_price = annual_plan_electrical_price / days_in_year
        day_plan_co2_value = annual_plan_co2_value / days_in_year
        day_plan_co2_price = annual_plan_co2_price / days_in_year


        result[time_key]['electrical_value'] = day_plan_electrical_value - item['electrical_value']
        result[time_key]['electrical_price'] = day_plan_electrical_price - item['electrical_price']
        result[time_key]['co2_value'] = day_plan_co2_value - item['co2_value']
        result[time_key]['co2_price'] = day_plan_co2_price - item['co2_price']

        if mode == "intensity":
            # 原単位（経済活動量）
            month = item['month']
            ym_key = f"{year}-{month}"
            economic_activity_value = economic_activity_values[ym_key]

            # 経済活動量で除算する
            if economic_activity_value and economic_activity_value > 0.0:
                result[time_key]['electrical_value'] = item['electrical_value'] / economic_activity_value
                result[time_key]['electrical_price'] = item['electrical_price'] / economic_activity_value
                result[time_key]['co2_value'] = item['co2_value'] / economic_activity_value
                result[time_key]['co2_price'] = item['co2_price'] / economic_activity_value
    return result


# Graphデータの取得: 分単位
# 指定時刻を先頭として、そこから4時間分のデータを取得
class ChDataPerMinuteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = ChannelDataPerMinuteSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        hour = self.request.query_params.get('hour', None)
        minute = self.request.query_params.get('minute', 0)
        company_id = self.request.query_params.get('company_id', None)
        mode = self.request.query_params.get('mode')

        # 日付が指定されていない場合はエラー
        if year is None or month is None or date is None or hour is None or minute is None:
            raise ValidationError('year, month, date, and hour must be specified')

        # 指定時刻から範囲を指定
        if year is not None and month is not None and date is not None and hour is not None and minute is not None:
            start_time = datetime.datetime(int(year), int(month), int(date), int(hour), int(minute), 0)
            end_time = start_time + datetime.timedelta(hours=4)

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            root_entity = target_company.root_entity
            if root_entity is None or not root_entity.id in all_permit_entity_ids:
                raise PermissionDenied()

        # company_idのチェック
        # TODO: ユーザ権限への対応
        if company_id is not None:
            # ユーザーが所属している企業か確認
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            # 無指定なら、ユーザの所属企業を取得
            company_id = self.request.user.company_id_id
        
        graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id)
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
        for graph_adapter in graph_adapters:
            graph_no = f"{graph_adapter.channel_no}"
            device = graph_adapter.device_number
            if graph_adapter.is_co2_emissions_baseline:
                if graph_adapter.co2_emissions_baseline == 0.0:
                    reduction_coefficient = 0.0
                else:
                    reduction_coefficient = 1.0 - (graph_adapter.co2_emissions_current / graph_adapter.co2_emissions_baseline)
            else:
                reduction_coefficient = graph_adapter.co2_emissions_improvement_rate

            if device == None or device.entity == None or device.entity.id == None:
                result_list_all.append({"graph_no":graph_no, "data":[]})
            else:
                entity_id = device.entity.id
                # 単価情報：光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）
                electric_unit_price = graph_adapter.utility_cost_price    
                electric_unit_co2 = graph_adapter.co2_emissions_current

                # 計算式文字列の取得
                equation_str = graph_adapter.equation_str
                if equation_str is None or equation_str == '':
                    equation_str ='(x)'         # 計算式が取得できなかった場合は、xをそのまま返す

                # DeviceのGatewayの使用開始日を取得
                gateway_id = device.gateway_id
                startdate_obj = GatewayStartdate.objects.filter(gateway_id=gateway_id).order_by('-updated_at').first()
                if startdate_obj is not None:
                    startdate = startdate_obj.started_at
                    data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE, get_data_at__date__gte=startdate).order_by('get_data_at')
                else:
                    data_per_minute = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.MINUTE).order_by('get_data_at')

                if start_time is not None and end_time is not None:
                    data_per_minute = data_per_minute.filter(get_data_at__range=(start_time, end_time))

                aggregated_data = data_per_minute.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                    'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'get_data_at__second'
                ).annotate(
                    economic_activity_value=Subquery(economic_activity_amount_query),
                    electrical_value=F('value'),
                )

                result_dict = update_final_result_chdate(aggregated_data, equation_str, mode, reduction_coefficient, Data.DateType.MINUTE, electric_unit_price, electric_unit_co2, co2_unit_price)
                result_list_all.append({"graph_no":graph_no, "data":result_dict.values()})

        return result_list_all

# Channelデータの取得: 時間単位
@extend_schema_view(
    list=extend_schema(
        description='CHごと合計/時間単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='month', location=OpenApiParameter.QUERY, type=int, description='月', required=True, examples=[OpenApiExample('e.g.1', value=2)]),
            OpenApiParameter(name='date', location=OpenApiParameter.QUERY, type=int, description='日', required=True, examples=[OpenApiExample('e.g.1', value=1)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='mode', location=OpenApiParameter.QUERY, type=str, description='表示モード(標準 / 原単位)', examples=[OpenApiExample('e.g.1', value='intensity')]),
            # OpenApiParameter(name='start', location=OpenApiParameter.QUERY, type=int, description='指定', examples=[OpenApiExample('e.g.1', value=1)]),
            # OpenApiParameter(name='end', location=OpenApiParameter.QUERY, type=int, description='指定', examples=[OpenApiExample('e.g.1', value=1)]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value={
                    "1":[
                        {
                            "hour": 0,
                            "minute": 0,
                            "electrical_value": 100.0,
                            "electrical_price": 2700,
                            "co2_value": 400.0,
                            "co2_price": 4000,
                        },
                    ]
                }
            ),
        ],
    ),
)
class ChDataPerHourViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = ChannelDataPerHourSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        company_id = self.request.query_params.get('company_id', None)
        mode = self.request.query_params.get('mode')

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            root_entity = target_company.root_entity
            if root_entity is None or not root_entity.id in all_permit_entity_ids:
                raise PermissionDenied()

        # company_idのチェック
        # TODO: ユーザ権限への対応
        if company_id is not None:
            # ユーザーが所属している企業か確認
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            # 無指定なら、ユーザの所属企業を取得
            company_id = self.request.user.company_id_id
        
        graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id)
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
        for graph_adapter in graph_adapters:
            graph_no = f"{graph_adapter.channel_no}"
            device = graph_adapter.device_number
            if graph_adapter.is_co2_emissions_baseline:
                if graph_adapter.co2_emissions_baseline == 0.0:
                    reduction_coefficient = 0.0
                else:
                    reduction_coefficient = 1.0 - (graph_adapter.co2_emissions_current / graph_adapter.co2_emissions_baseline)
            else:
                reduction_coefficient = graph_adapter.co2_emissions_improvement_rate

            if device == None or device.entity == None or device.entity.id == None:
                result_list_all.append({"graph_no":graph_no, "data":[]})
            else:
                entity_id = device.entity.id

                # 単価情報：光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）
                electric_unit_price = graph_adapter.utility_cost_price    
                electric_unit_co2 = graph_adapter.co2_emissions_current

                # 計算式文字列の取得
                equation_str = graph_adapter.equation_str
                if equation_str is None or equation_str == '':
                    equation_str ='(x)'         # 計算式が取得できなかった場合は、xをそのまま返す

                # DeviceのGatewayの使用開始日を取得
                gateway_id = device.gateway_id
                startdate_obj = GatewayStartdate.objects.filter(gateway_id=gateway_id).order_by('-updated_at').first()
                if startdate_obj is not None:
                    startdate = startdate_obj.started_at
                    data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR, get_data_at__date__gte=startdate).order_by('get_data_at')
                else:
                    data_per_hour = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.HOUR).order_by('get_data_at')

                if year is not None and month is not None and date is not None:
                    data_per_hour = data_per_hour.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date).order_by('get_data_at')
                    if start is not None and end is not None:
                        data_per_hour = data_per_hour.filter(get_data_at__time__range=(int(start), int(end))).order_by('get_data_at')

                aggregated_data = data_per_hour.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                    'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
                ).annotate(
                    economic_activity_value=Subquery(economic_activity_amount_query),
                    electrical_value=F('value'),
                )

                result_dict = update_final_result_chdate(aggregated_data, equation_str, mode, reduction_coefficient, Data.DateType.HOUR, electric_unit_price, electric_unit_co2, co2_unit_price)
                result_list_all.append({"graph_no":graph_no, "data":result_dict.values()})

        return result_list_all


# その月の週index(0始まり)からその週の月曜日と日曜日の日にちを取得
def get_week_range(year, month, week_index):
    # 月の初日を取得ß
    first_datetime = datetime.datetime(year, month, 1, 0, 0)

    # 月の初日が火曜以降の場合、前の月の月曜まで戻る
    start_datetime = first_datetime - datetime.timedelta(days=(first_datetime.weekday() - calendar.MONDAY))

    # 指定されたweek_indexの週の月曜日を取得
    start_datetime += datetime.timedelta(weeks=week_index)

    # 週の終わり（日曜日の23:59:59）を取得
    end_datetime = (start_datetime + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59))

    return start_datetime, end_datetime


@extend_schema_view(
    list=extend_schema(
        description='合計/日単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='month', location=OpenApiParameter.QUERY, type=int, description='月', required=True, examples=[OpenApiExample('e.g.1', value=2)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='week', location=OpenApiParameter.QUERY, type=str, description='その指定月(month)の週番号', examples=[OpenApiExample('e.g.1', value='1')]),
            OpenApiParameter(name='mode', location=OpenApiParameter.QUERY, type=str, description='表示モード(標準 / 原単位)', examples=[OpenApiExample('e.g.1', value='intensity')]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "date": 1,
                        "electrical_value": 1000.0,
                        "electrical_price": 27000,
                        "co2_value": 2000.0,
                        "co2_price": 3000000,
                    },
                ]
            ),
        ],
    ),
)
class ChDataPerDateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = ChannelDataPerDateSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        week = self.request.query_params.get('week', None)      # weekは月の中での週番号（月曜始まり、0〜）
        company_id = self.request.query_params.get('company_id', None)
        mode = self.request.query_params.get('mode')

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            root_entity = target_company.root_entity
            if root_entity is None or not root_entity.id in all_permit_entity_ids:
                raise PermissionDenied()

        # company_idのチェック
        # TODO: ユーザ権限への対応
        if company_id is not None:
            # ユーザーが所属している企業か確認
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            # 無指定なら、ユーザの所属企業を取得
            company_id = self.request.user.company_id_id
        
        graph_adapters = ChannelAdapter.objects.filter(company_id_id=company_id)
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
        for graph_adapter in graph_adapters:
            graph_no = f"{graph_adapter.channel_no}"
            device = graph_adapter.device_number
            if graph_adapter.is_co2_emissions_baseline:
                if graph_adapter.co2_emissions_baseline == 0.0:
                    reduction_coefficient = 0.0
                else:
                    reduction_coefficient = 1.0 - (graph_adapter.co2_emissions_current / graph_adapter.co2_emissions_baseline)
            else:
                reduction_coefficient = graph_adapter.co2_emissions_improvement_rate

            if device == None or device.entity == None or device.entity.id == None:
                result_list_all.append({"graph_no":graph_no, "data":[]})
            else:
                entity_id = device.entity.id

                # 単価情報：光熱費単価（円/kWh）、CO2排出係数（t-CO2/kWh）
                electric_unit_price = graph_adapter.utility_cost_price    
                electric_unit_co2 = graph_adapter.co2_emissions_current

                # 計算式文字列の取得
                equation_str = graph_adapter.equation_str
                if equation_str is None or equation_str == '':
                    equation_str ='(x)'         # 計算式が取得できなかった場合は、xをそのまま返す

                # DeviceのGatewayの使用開始日を取得
                gateway_id = device.gateway_id
                startdate_obj = GatewayStartdate.objects.filter(gateway_id=gateway_id).order_by('-updated_at').first()
                if startdate_obj is not None:
                    startdate = startdate_obj.started_at
                    data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE, get_data_at__date__gte=startdate).order_by('get_data_at')
                else:
                    data_per_date = Data.objects.filter(entity_id=entity_id, date_type=Data.DateType.DATE).order_by('get_data_at')

                if year is not None and month is not None:
                    if week is None:
                        data_per_date = data_per_date.filter(get_data_at__year=year, get_data_at__month=month).order_by('get_data_at')
                    else:
                        first_date, last_date = get_week_range(int(year), int(month), int(week))
                        data_per_date = data_per_date.filter(get_data_at__range=(first_date, last_date)).order_by('get_data_at')
                    if start is not None and end is not None:
                        data_per_date = data_per_date.filter(get_data_at__day__range=(int(start), int(end))).order_by('get_data_at')

                aggregated_data = data_per_date.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
                    'value', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute',
                ).annotate(
                    economic_activity_value=Subquery(economic_activity_amount_query),
                    electrical_value=F('value'),
                )

                result_dict = update_final_result_chdate(aggregated_data, equation_str, mode, reduction_coefficient, Data.DateType.DATE, electric_unit_price, electric_unit_co2, co2_unit_price)
                result_list_all.append({"graph_no":graph_no, "data":result_dict.values()})

        return result_list_all

def  update_final_result_chdate(data, equation_str, mode, reduction_coefficient, date_type, electric_unit_price, electric_unit_co2, co2_unit_price):
    result_dict = {}
    for item in data:
        item_year = item['get_data_at__year']
        item_month = item['get_data_at__month']
        item_date = item['get_data_at__day']
        item_hour = item['get_data_at__hour']
        item_minute = item['get_data_at__minute']

        time_key = ''
        if date_type == Data.DateType.MINUTE:
            item_second = item['get_data_at__second']
            time_key = f"{item_year}-{item_month}-{item_date}-{item_hour}-{item_minute}-{item_second}"

        elif date_type == Data.DateType.HOUR:
            time_key = f"{item_year}-{item_month}-{item_date}-{item_hour}-{item_minute}"

        elif date_type == Data.DateType.DATE:
            time_key = f"{item_year}-{item_month}-{item_date}"

        elif date_type == Data.DateType.MONTH:
            time_key = f"{item_year}-{item_month}"

        elif date_type == Data.DateType.YEAR:
            time_key = f"{item_year}"
            # ここには来ないはず

        # 1日の実績値：この段階で計算式を適用する.計算式には'x'が使われることになっている
        equation = parse_expr(equation_str)
        expr = symbols('x')
        electrical_value = float(equation.subs(expr, item['electrical_value'])) if item['electrical_value'] else 0.0
        electrical_price = electrical_value * electric_unit_price
        co2_value = electrical_value * electric_unit_co2
        co2_price = co2_value * co2_unit_price

        if mode == "intensity":
            # 原単位（経済活動量）
            economic_activity_value = item['economic_activity_value']

            if economic_activity_value and economic_activity_value > 0.0:
                electrical_value = electrical_value / economic_activity_value
                electrical_price = electrical_price / economic_activity_value
                co2_value = co2_value / economic_activity_value
                co2_price = co2_price / economic_activity_value

        if date_type == Data.DateType.MINUTE:
            result_obj = {
                'year': item_year,
                'month': item_month,
                'date': item_date,
                'hour': item_hour,
                'minute': item_minute,
                'second': item_second,
                'electrical_value': electrical_value,
                'electrical_price': electrical_price,
                'co2_value': co2_value * 1000,      # 内部計算結果は t-CO2e, 出力単位は kg-CO2e
                'co2_price': co2_price,
                'electrical_value_reduction': electrical_value * reduction_coefficient,
                'electrical_price_reduction': electrical_price * reduction_coefficient,
                'co2_value_reduction': co2_value * reduction_coefficient * 1000,    # 内部計算結果は t-CO2e, 出力単位は kg-CO2e
                'co2_price_reduction': co2_price * reduction_coefficient,
            }
        else:
            result_obj = {
                'year': item_year,
                'month': item_month,
                'date': item_date,
                'hour': item_hour,
                'minute': item_minute,
                'electrical_value': electrical_value,
                'electrical_price': electrical_price,
                'co2_value': co2_value * 1000,      # 内部計算結果は t-CO2e, 出力単位は kg-CO2e
                'co2_price': co2_price,
                'electrical_value_reduction': electrical_value * reduction_coefficient,
                'electrical_price_reduction': electrical_price * reduction_coefficient,
                'co2_value_reduction': co2_value * reduction_coefficient * 1000,    # 内部計算結果は t-CO2e, 出力単位は kg-CO2e
                'co2_price_reduction': co2_price * reduction_coefficient,
           }
        result_dict[time_key]=result_obj
    return result_dict

##
##
def  update_final_result(final_result, data, value_key, price_key, mode, fuel_unit, date_type):
    final_result_copy = final_result.copy()
    for item in data:
        item_year = item['get_data_at__year']
        item_month = item['get_data_at__month']
        item_date = item['get_data_at__day']
        item_hour = item['get_data_at__hour']
        item_minute = item['get_data_at__minute']
        time_key = ''
        if date_type == Data.DateType.MINUTE:
            item_second = item['get_data_at__second']
            time_key = f"{item_year}-{item_month}-{item_date}-{item_hour}-{item_minute}-{item_second}"
        elif date_type == Data.DateType.HOUR:
            time_key = f"{item_year}-{item_month}-{item_date}-{item_hour}-{item_minute}"
        elif date_type == Data.DateType.DATE:
            time_key = f"{item_year}-{item_month}-{item_date}"
        elif date_type == Data.DateType.MONTH:
            time_key = f"{item_year}-{item_month}"
        elif date_type == Data.DateType.YEAR:
            time_key = f"{item_year}"

        if time_key not in final_result_copy:
            if date_type == Data.DateType.MINUTE:
                final_result_copy[time_key] = {
                    'year': item_year,
                    'month': item_month,
                    'date': item_date,
                    'hour': item_hour,
                    'minute': item_minute,
                    'second': item_second,
                    'electrical_value': 0.0,
                    'electrical_price': 0,
                    'water_value': 0.0,
                    'water_price': 0,
                    'fuel_value': 0.0,
                    'fuel_price': 0,
                    'co2_value': 0.0,
                    'co2_price': 0,
                    'energy_saving_value': 0.0,
                    'renewal_energy_value': 0.0,
                    'fuel_unit': fuel_unit,
                }
            else:
                final_result_copy[time_key] = {
                    'year': item_year,
                    'month': item_month,
                    'date': item_date,
                    'hour': item_hour,
                    'minute': item_minute,
                    'electrical_value': 0.0,
                    'electrical_price': 0,
                    'water_value': 0.0,
                    'water_price': 0,
                    'fuel_value': 0.0,
                    'fuel_price': 0,
                    'co2_value': 0.0,
                    'co2_price': 0,
                    #'utility_costs': 0,
                    'fuel_unit': fuel_unit,
                }

        if mode == "intensity":
            final_result_copy[time_key][value_key] += (item[value_key + '_normalized'] if item[value_key + '_normalized'] is not None else 0.0)
            final_result_copy[time_key][price_key] += (item[price_key + '_normalized'] if item[price_key + '_normalized'] is not None else 0)
        else:
            final_result_copy[time_key][value_key] += item['sum_' + value_key] if item['sum_' + value_key] is not None else 0.0
            final_result_copy[time_key][price_key] += item['sum_' + price_key] if item['sum_' + price_key] is not None else 0
    return final_result_copy

# Dataをデバイスまでたどって一覧を取得する。その際に、デバイスの比重ρ（specific_gravity）を取得しておく
# ここでは、比重による値の再計算は行わない
def get_fuel_descendant_value(data, date_type):
    # 対象のentity_id一覧を取得
    entity_ids = data.filter(date_type=date_type).values_list('entity_id', flat=True).distinct()
    # entity_idを祖先とする子孫のentity_id一覧を作成
    descendant_list = [d.descendant_id for d in DataStructure.objects.filter(ancestor_id__in=entity_ids)]
    # 対象のデバイス一覧を取得
    target_activity_devices = Device.objects.filter(entity_id__in=descendant_list).select_related('entity')
    target_entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]

    # 比重ρを取得
    entity_rho_subquery = Device.objects.filter(entity_id=OuterRef('entity_id')
        ).annotate(specific_gravity2=Coalesce(Cast('specific_gravity',FloatField()), Value(1.0))
        ).values('specific_gravity2')[:1]

    # 子孫のentity_idから祖先のentity_idを取得
    descendant_ancestor_subquery = DataStructure.objects.filter(
        ancestor_id__in=entity_ids, descendant_id=OuterRef('entity_id')).values('ancestor_id')[:1]

    # 対象のデバイスの燃料データを取得
    fuel_data = Data.objects.filter(entity_id__in=target_entity_ids, date_type=date_type, data_type__name=DATA_TYPE_FUEL).order_by('get_data_at')
    fuel_data = fuel_data.annotate(
            rho=Subquery(entity_rho_subquery, output_field=FloatField()),
            target_entity_id = Subquery(descendant_ancestor_subquery),
        )

    return fuel_data


@extend_schema_view(
    list=extend_schema(
        description='合計/時間単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='month', location=OpenApiParameter.QUERY, type=int, description='月', required=True, examples=[OpenApiExample('e.g.1', value=2)]),
            OpenApiParameter(name='date', location=OpenApiParameter.QUERY, type=int, description='日', required=True, examples=[OpenApiExample('e.g.1', value=1)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='mode', location=OpenApiParameter.QUERY, type=str, description='表示モード(標準 / 原単位)', examples=[OpenApiExample('e.g.1', value='intensity')]),
            # OpenApiParameter(name='start', location=OpenApiParameter.QUERY, type=int, description='指定', examples=[OpenApiExample('e.g.1', value=1)]),
            # OpenApiParameter(name='end', location=OpenApiParameter.QUERY, type=int, description='指定', examples=[OpenApiExample('e.g.1', value=1)]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "hour": 0,
                        "minute": 0,
                        "electrical_value": 100.0,
                        "electrical_price": 2700,
                        "water_value": 200.0,
                        "water_price": 4400,
                        "fuel_value": 300.0,
                        "fuel_price": 9000,
                        "co2_value": 400.0,
                        "co2_price": 4000,
                        "hour": 1,
                        "get_data_date": "2023-01-01T01:00:00+09:00"
                    },
                ]
            ),
        ],
    ),

)
class DataPerHourViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = DataPerHourSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        activity_id = self.request.query_params.get('activity_id', None)
        company_id = self.request.query_params.get('company_id', None)
        entity_id = self.request.query_params.get('entity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            if entity_id is not None:
                if not entity_id in map(str, all_permit_entity_ids):
                    raise PermissionDenied()
            else:
                target_company = Company.objects.get(id=company_id)
                root_entity = target_company.root_entity
                has_some_entity_permission = UserEntityPermission.objects.filter(user_id=self.request.user.id, entity__company_id=company_id).exists()
                if root_entity is None or not has_some_entity_permission:
                    raise PermissionDenied()

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        if activity_id is not None:
            target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
            entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
            data_per_hour = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.HOUR).order_by('get_data_at')
        else:
            if company_id is not None:
                if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                    raise PermissionDenied()
                if entity_id is not None:
                    root_entity_id = entity_id
                else:
                    root_entity = Company.objects.get(id=company_id).root_entity
                    root_entity_id = root_entity.id if root_entity is not None else None
                    if root_entity_id is None:
                        raise PermissionDenied()
            elif entity_id is not None:
                root_entity_id = entity_id
            else:
                root_entity_id = self.request.user.company_id.root_entity_id
            data_per_hour = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.HOUR).order_by('get_data_at')

        if year is not None and month is not None and date is not None:
            data_per_hour = data_per_hour.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date).order_by('get_data_at')
            if start is not None and end is not None:
                data_per_hour = data_per_hour.filter(get_data_at__time__range=(int(start), int(end))).order_by('get_data_at')
        fuel_data = get_fuel_descendant_value(data_per_hour, Data.DateType.HOUR)
        if year is not None and month is not None and date is not None:
            fuel_data = fuel_data.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date).order_by('get_data_at')
            if start is not None and end is not None:
                fuel_data = fuel_data.filter(get_data_at__time__range=(int(start), int(end))).order_by('get_data_at')

        aggregated_electrical_data = data_per_hour.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_hour.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_hour.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0.0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_hour.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.HOUR)
        final_result = update_final_result(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.HOUR)
        final_result = update_final_result(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.HOUR)
        final_result = update_final_result(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.HOUR)

        final_result_list = list(final_result.values())

        return final_result_list




# その月の週index(0始まり)からその週の月曜日と日曜日の日にちを取得
def get_week_range(year, month, week_index):
    # 月の初日を取得ß
    first_datetime = datetime.datetime(year, month, 1, 0, 0)

    # 月の初日が火曜以降の場合、前の月の月曜まで戻る
    start_datetime = first_datetime - datetime.timedelta(days=(first_datetime.weekday() - calendar.MONDAY))

    # 指定されたweek_indexの週の月曜日を取得
    start_datetime += datetime.timedelta(weeks=week_index)

    # 週の終わり（日曜日の23:59:59）を取得
    end_datetime = (start_datetime + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59))

    return start_datetime, end_datetime


@extend_schema_view(
    list=extend_schema(
        description='合計/日単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='month', location=OpenApiParameter.QUERY, type=int, description='月', required=True, examples=[OpenApiExample('e.g.1', value=2)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='week', location=OpenApiParameter.QUERY, type=str, description='その指定月(month)の週番号', examples=[OpenApiExample('e.g.1', value='1')]),
            OpenApiParameter(name='mode', location=OpenApiParameter.QUERY, type=str, description='表示モード(標準 / 原単位)', examples=[OpenApiExample('e.g.1', value='intensity')]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "date": 1,
                        "electrical_value": 1000.0,
                        "electrical_price": 27000,
                        "water_value": 1930.0,
                        "water_price": 386000,
                        "fuel_value": 2900.0,
                        "fuel_price": 2030000,
                        "co2_value": 2000.0,
                        "co2_price": 3000000,
                        "energy_saving_value": 3009.0,
                        "renewal_energy_value": 933.0,
                        "get_data_date": "2023-01-01T00:00:00+09:00"
                    },
                ]
            ),
        ],
    ),

)

class DataPerDateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = DataPerDateSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        # weekは月の中での週番号
        week = self.request.query_params.get('week', None)
        activity_id = self.request.query_params.get('activity_id', None)
        company_id = self.request.query_params.get('company_id', None)
        entity_id = self.request.query_params.get('entity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            if entity_id is not None:
                if not entity_id in map(str, all_permit_entity_ids):
                    raise PermissionDenied()
            else:
                target_company = Company.objects.get(id=company_id)
                root_entity = target_company.root_entity
                has_some_entity_permission = UserEntityPermission.objects.filter(user_id=self.request.user.id, entity__company_id=company_id).exists()
                if root_entity is None or not has_some_entity_permission:
                    raise PermissionDenied()

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        if activity_id is not None:
            target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
            entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
            data_per_date = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.DATE).order_by('get_data_at')
        else:
            if company_id is not None:
                if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                    raise PermissionDenied()
                if entity_id is not None:
                    root_entity_id = entity_id
                else:
                    root_entity = Company.objects.get(id=company_id).root_entity
                    root_entity_id = root_entity.id if root_entity is not None else None
                    if root_entity_id is None:
                        raise PermissionDenied()
            elif entity_id is not None:
                root_entity_id = entity_id
            else:
                root_entity_id = self.request.user.company_id.root_entity_id
            data_per_date = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.DATE).order_by('get_data_at')

        if year is not None and month is not None:
            if week is None:
                data_per_date = data_per_date.filter(get_data_at__year=year, get_data_at__month=month).order_by('get_data_at')
            else:
                first_date, last_date = get_week_range(int(year), int(month), int(week))
                data_per_date = data_per_date.filter(get_data_at__range=(first_date, last_date)).order_by('get_data_at')
            if start is not None and end is not None:
                data_per_date = data_per_date.filter(get_data_at__day__range=(int(start), int(end))).order_by('get_data_at')
        fuel_data = get_fuel_descendant_value(data_per_date, Data.DateType.DATE)
        if year is not None and month is not None:
            if week is None:
                fuel_data = fuel_data.filter(get_data_at__year=year, get_data_at__month=month).order_by('get_data_at')
            else:
                first_date, last_date = get_week_range(int(year), int(month), int(week))
                fuel_data = fuel_data.filter(get_data_at__range=(first_date, last_date)).order_by('get_data_at')
            if start is not None and end is not None:
                fuel_data = fuel_data.filter(get_data_at__day__range=(int(start), int(end))).order_by('get_data_at')

        aggregated_electrical_data = data_per_date.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_date.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_date.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0.0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_date.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.DATE)
        final_result = update_final_result(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.DATE)
        final_result = update_final_result(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.DATE)
        final_result = update_final_result(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.DATE)

        final_result_list = list(final_result.values())

        return final_result_list




@extend_schema_view(
    list=extend_schema(
        description='合計/月単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='mode', location=OpenApiParameter.QUERY, type=str, description='表示モード(標準 / 原単位)', examples=[OpenApiExample('e.g.1', value='intensity')]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "month": 1,
                        "electrical_value": 1000.0,
                        "electrical_price": 27000,
                        "water_value": 1930.0,
                        "water_price": 386000,
                        "fuel_value": 2900.0,
                        "fuel_price": 2030000,
                        "co2_value": 2000.0,
                        "co2_price": 3000000,
                        "energy_saving_value": 3009.0,
                        "renewal_energy_value": 933.0,
                        "get_data_date": "2023-01-01T00:00:00+09:00"
                    },
                ]
            ),
        ],
    ),

)
class DataPerMonthViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = DataPerMonthSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        activity_id = self.request.query_params.get('activity_id', None)
        company_id = self.request.query_params.get('company_id', None)
        entity_id = self.request.query_params.get('entity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            if entity_id is not None:
                if not entity_id in map(str, all_permit_entity_ids):
                    raise PermissionDenied()
            else:
                target_company = Company.objects.get(id=company_id)
                root_entity = target_company.root_entity
                has_some_entity_permission = UserEntityPermission.objects.filter(user_id=self.request.user.id, entity__company_id=company_id).exists()
                if root_entity is None or not has_some_entity_permission:
                    raise PermissionDenied()

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        if activity_id is not None:
            target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
            entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
            data_per_month = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.MONTH).order_by('get_data_at')
        else:
            if company_id is not None:
                if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                    raise PermissionDenied()
                if entity_id is not None:
                    root_entity_id = entity_id
                else:
                    root_entity = Company.objects.get(id=company_id).root_entity
                    root_entity_id = root_entity.id if root_entity is not None else None
                    if root_entity_id is None:
                        raise PermissionDenied()
            elif entity_id is not None:
                root_entity_id = entity_id
            else:
                root_entity_id = self.request.user.company_id.root_entity_id
            data_per_month = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.MONTH).order_by('get_data_at')

        if year is not None:
            data_per_month = data_per_month.filter(get_data_at__year=year).order_by('get_data_at')
            if start is not None and end is not None:
                data_per_month = data_per_month.filter(get_data_at__month__range=(int(start), int(end))).order_by('get_data_at')
        fuel_data = get_fuel_descendant_value(data_per_month, Data.DateType.MONTH)
        if year is not None:
            fuel_data = fuel_data.filter(get_data_at__year=year).order_by('get_data_at')
            if start is not None and end is not None:
                fuel_data = fuel_data.filter(get_data_at__month__range=(int(start), int(end))).order_by('get_data_at')

        aggregated_electrical_data = data_per_month.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_month.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_month.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0.0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_month.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.MONTH)
        final_result = update_final_result(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.MONTH)
        final_result = update_final_result(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.MONTH)
        final_result = update_final_result(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.MONTH)

        final_result_list = list(final_result.values())

        return final_result_list


@extend_schema_view(
    list=extend_schema(
        description='合計/年単位',
        parameters=[
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='mode', location=OpenApiParameter.QUERY, type=str, description='表示モード(標準 / 原単位)', examples=[OpenApiExample('e.g.1', value='intensity')]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "year": 2023,
                        "electrical_value": 100000.0,
                        "electrical_price": 2700000,
                        "water_value": 10000.0,
                        "water_price": 2000000,
                        "fuel_value": 999999.0,
                        "fuel_price": 699999300,
                        "co2_value": 990290.0,
                        "co2_price": 1485435000,
                        "energy_saving_value": 1000.0,
                        "renewal_energy_value": 100.0,
                        "get_data_date": "2023-01-01"
                    },
                ]
            ),
        ],
    ),

)
class DataPerYearViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = DataPerYearSerializer

    def get_queryset(self):
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        activity_id = self.request.query_params.get('activity_id', None)
        company_id = self.request.query_params.get('company_id', None)
        entity_id = self.request.query_params.get('entity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        permit_entity_ids = UserEntityPermission.objects.filter(user_id=self.request.user.id).values_list('entity_id', flat=True)
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=permit_entity_ids).values_list('descendant_id', flat=True)
        target_company = Company.objects.get(id=company_id)
        if target_company.admin_user_id != self.request.user: # adminは対象企業の全エンティティを見られる
            if entity_id is not None:
                if not entity_id in map(str, all_permit_entity_ids):
                    raise PermissionDenied()
            else:
                target_company = Company.objects.get(id=company_id)
                root_entity = target_company.root_entity
                has_some_entity_permission = UserEntityPermission.objects.filter(user_id=self.request.user.id, entity__company_id=company_id).exists()
                if root_entity is None or not has_some_entity_permission:
                    raise PermissionDenied()

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        if activity_id is not None:
            target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
            entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
            data_per_year = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.YEAR).order_by('get_data_at')
        else:
            # NOTE: エンティティ指定でグラフデータを取る場合はここの実装を変える
            if company_id is not None:
                if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                    raise PermissionDenied()
                if entity_id is not None:
                    root_entity_id = entity_id
                else:
                    root_entity = Company.objects.get(id=company_id).root_entity
                    root_entity_id = root_entity.id if root_entity is not None else None
                    if root_entity_id is None:
                        raise PermissionDenied()
            elif entity_id is not None:
                root_entity_id = entity_id
            else:
                root_entity_id = self.request.user.company_id.root_entity_id
            data_per_year = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.YEAR).order_by('get_data_at')
        if start is not None and end is not None:
            data_per_year = data_per_year.filter(get_data_at__year__range=(int(start), int(end))).order_by('get_data_at')
        fuel_data = get_fuel_descendant_value(data_per_year, Data.DateType.YEAR)
        if start is not None and end is not None:
            fuel_data = fuel_data.filter(get_data_at__year__range=(int(start), int(end))).order_by('get_data_at')

        aggregated_electrical_data = data_per_year.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_year.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_year.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0.0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_year.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.YEAR)
        final_result = update_final_result(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.YEAR)
        final_result = update_final_result(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.YEAR)
        final_result = update_final_result(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.YEAR)

        final_result_list = list(final_result.values())

        return final_result_list

class DeviceDataViewSet(viewsets.ModelViewSet):
    # TODO: 古い機能で使っていたものっぽいのでちゃんと見て問題なさそうならフロントも含めて削除する(手動入力機能)
    queryset = DeviceDataPerHour.objects.all()
    serializer_class = DeviceDataPerHourSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


###
# TODO:廃止予定：ここから
###
@extend_schema_view(
    list=extend_schema(
        description='設備/時間単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='month', location=OpenApiParameter.QUERY, type=int, description='月', required=True, examples=[OpenApiExample('e.g.1', value=2)]),
            OpenApiParameter(name='date', location=OpenApiParameter.QUERY, type=int, description='日', required=True, examples=[OpenApiExample('e.g.1', value=1)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            # OpenApiParameter(name='start', location=OpenApiParameter.QUERY, type=int, description='指定', examples=[OpenApiExample('e.g.1', value=1)]),
            # OpenApiParameter(name='end', location=OpenApiParameter.QUERY, type=int, description='指定', examples=[OpenApiExample('e.g.1', value=1)]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "hour": 0,
                        "minute": 0,
                        "electrical_value": 100.0,
                        "electrical_price": 2700,
                        "water_value": 200.0,
                        "water_price": 4400,
                        "fuel_value": 300.0,
                        "fuel_price": 9000,
                        "co2_value": 400.0,
                        "co2_price": 4000,
                        "hour": 1,
                        "get_data_date": "2023-01-01T01:00:00+09:00"
                    },
                ]
            ),
        ],
    ),

)
class DeviceDataPerHourViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DeviceDataPerHourSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            pushlog_apis = PushLogApi.objects.filter(company_id=company_id)
        else:
            pushlog_apis = PushLogApi.objects.filter(company_id=self.request.user.company_id_id)
        devices = Device.objects.filter(pushlog_api__in=pushlog_apis)
        entity_to_device = {}
        for device in devices:
            if device.entity is not None:
                entity_id = device.entity.id
                if entity_id not in entity_to_device:
                    entity_to_device[entity_id] = device
        entity_ids = entity_to_device.keys()

        queryset = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.HOUR).order_by('get_data_at')
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)


        if year and month and date is not None:
            queryset = queryset.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date).order_by('get_data_at')

            if start and end is not None:
                queryset = queryset.filter(get_data_at__time__range=(datetime.time(int(start)), datetime.time(int(end)))).order_by('get_data_at')

            result = map(lambda data: {
                'year': data.get_data_at.year,
                'month': data.get_data_at.month,
                'date': data.get_data_at.day,
                'hour': data.get_data_at.hour,
                'minute': data.get_data_at.minute,
                'electrical_value': (data.value or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
                'electrical_price': (data.price or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
                'water_value': (data.value or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
                'water_price': (data.price or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
                'fuel_value': (data.value or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
                'fuel_price': (data.price or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
                'co2_value': (data.value or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
                'co2_price': (data.price or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
                'get_data_date': data.get_data_at,
                'device_id': entity_to_device[data.entity.id],
            }, queryset)

            return result



@extend_schema_view(
    list=extend_schema(
        description='設備/日単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='month', location=OpenApiParameter.QUERY, type=int, description='月', required=True, examples=[OpenApiExample('e.g.1', value=2)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='week', location=OpenApiParameter.QUERY, type=str, description='指定月(month)の週番号', examples=[OpenApiExample('e.g.1', value='1')]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "date": 1,
                        "electrical_value": 1000.0,
                        "electrical_price": 27000,
                        "water_value": 1930.0,
                        "water_price": 386000,
                        "fuel_value": 2900.0,
                        "fuel_price": 2030000,
                        "co2_value": 2000.0,
                        "co2_price": 3000000,
                        "energy_saving_value": 3009.0,
                        "renewal_energy_value": 933.0,
                        "get_data_date": "2023-01-01T00:00:00+09:00"
                    },
                ]
            ),
        ],
    ),

)
class DeviceDataPerDateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DeviceDataPerDateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            pushlog_apis = PushLogApi.objects.filter(company_id=company_id)
        else:
            pushlog_apis = PushLogApi.objects.filter(company_id=self.request.user.company_id_id)
        devices = Device.objects.filter(pushlog_api__in=pushlog_apis)
        entity_to_device = {}
        for device in devices:
            if device.entity is not None:
                entity_id = device.entity.id
                if entity_id not in entity_to_device:
                    entity_to_device[entity_id] = device
        entity_ids = entity_to_device.keys()

        queryset = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.DATE).order_by('get_data_at')
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        # weekは月の中での週番号
        week = self.request.query_params.get('week', None)

        # weekかmonthは必須
        if year and month is not None:
            if week is None:
                queryset = queryset.filter(get_data_at__year=year, get_data_at__month=month).order_by('get_data_at')

            if week is not None:
                first_date, last_date = get_week_range(int(year), int(month), int(week))
                queryset = queryset.filter(get_data_at__range=(first_date, last_date)).order_by('get_data_at')

            if start and end is not None:
                queryset = queryset.filter(get_data_at__day__range=(int(start), int(end))).order_by('get_data_at')

            result = map(lambda data: {
                'year': data.get_data_at.year,
                'month': data.get_data_at.month,
                'date': data.get_data_at.day,
                'hour': data.get_data_at.hour,
                'minute': data.get_data_at.minute,
                'electrical_value': (data.value or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
                'electrical_price': (data.price or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
                'water_value': (data.value or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
                'water_price': (data.price or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
                'fuel_value': (data.value or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
                'fuel_price': (data.price or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
                'co2_value': (data.value or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
                'co2_price': (data.price or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
                'get_data_date': data.get_data_at,
                'device_id': entity_to_device[data.entity.id],
            }, queryset)

            return result




@extend_schema_view(
    list=extend_schema(
        description='設備/月単位',
        parameters=[
            OpenApiParameter(name='year', location=OpenApiParameter.QUERY, type=int, description='年', required=True, examples=[OpenApiExample('e.g.1', value=2023)]),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
            OpenApiParameter(name='mode', location=OpenApiParameter.QUERY, type=str, description='表示モード(標準 / 原単位)', examples=[OpenApiExample('e.g.1', value='intensity')]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "month": 1,
                        "electrical_value": 1000.0,
                        "electrical_price": 27000,
                        "water_value": 1930.0,
                        "water_price": 386000,
                        "fuel_value": 2900.0,
                        "fuel_price": 2030000,
                        "co2_value": 2000.0,
                        "co2_price": 3000000,
                        "energy_saving_value": 3009.0,
                        "renewal_energy_value": 933.0,
                        "get_data_date": "2023-01-01T00:00:00+09:00"
                    },
                ]
            ),
        ],
    ),

)
class DeviceDataPerMonthViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeviceDataPerMonthSerializer

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            pushlog_apis = PushLogApi.objects.filter(company_id=company_id)
        else:
            pushlog_apis = PushLogApi.objects.filter(company_id=self.request.user.company_id_id)
        devices = Device.objects.filter(pushlog_api__in=pushlog_apis)
        entity_to_device = {}
        for device in devices:
            if device.entity is not None:
                entity_id = device.entity.id
                if entity_id not in entity_to_device:
                    entity_to_device[entity_id] = device
        entity_ids = entity_to_device.keys()

        queryset = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.MONTH).order_by('get_data_at')
        year = self.request.query_params.get('year', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)

        if year is not None:
            queryset = queryset.filter(get_data_at__year=year).order_by('get_data_at')

            if start and end is not None:
                queryset = queryset.filter(get_data_at__month__range=(int(start), int(end))).order_by('get_data_at')

            result = map(lambda data: {
                'year': data.get_data_at.year,
                'month': data.get_data_at.month,
                'date': data.get_data_at.day,
                'hour': data.get_data_at.hour,
                'minute': data.get_data_at.minute,
                'electrical_value': (data.value or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
                'electrical_price': (data.price or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
                'water_value': (data.value or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
                'water_price': (data.price or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
                'fuel_value': (data.value or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
                'fuel_price': (data.price or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
                'co2_value': (data.value or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
                'co2_price': (data.price or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
                'get_data_date': data.get_data_at,
                'device_id': entity_to_device[data.entity.id],
            }, queryset)

            return result


@extend_schema_view(
    list=extend_schema(
        description='設備/年単位',
        parameters=[
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, type=str, description='種類', examples=[OpenApiExample('e.g.1', value='total')]),
        ],
        examples=[
            OpenApiExample(
                'e.g.1',
                summary='',
                description='',
                value=[
                    {
                        "year": 2023,
                        "electrical_value": 100000.0,
                        "electrical_price": 2700000,
                        "water_value": 10000.0,
                        "water_price": 2000000,
                        "fuel_value": 999999.0,
                        "fuel_price": 699999300,
                        "co2_value": 990290.0,
                        "co2_price": 1485435000,
                        "energy_saving_value": 1000.0,
                        "renewal_energy_value": 100.0,
                        "get_data_date": "2023-01-01"
                    },
                ]
            ),
        ],
    ),

)
class DeviceDataPerYearViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DeviceDataPerYearSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            pushlog_apis = PushLogApi.objects.filter(company_id=company_id)
        else:
            pushlog_apis = PushLogApi.objects.filter(company_id=self.request.user.company_id_id)
        devices = Device.objects.filter(pushlog_api__in=pushlog_apis)
        entity_to_device = {}
        for device in devices:
            if device.entity is not None:
                entity_id = device.entity.id
                if entity_id not in entity_to_device:
                    entity_to_device[entity_id] = device
        entity_ids = entity_to_device.keys()

        queryset = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.YEAR).order_by('get_data_at')
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)

        if start and end is not None:
            queryset = queryset.filter(get_data_at__year__range=(int(start), int(end))).order_by('get_data_at')

        result = map(lambda data: {
            'year': data.get_data_at.year,
            'month': data.get_data_at.month,
            'date': data.get_data_at.day,
            'hour': data.get_data_at.hour,
            'minute': data.get_data_at.minute,
            'electrical_value': (data.value or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
            'electrical_price': (data.price or 0) if data.data_type.name == DATA_TYPE_ELECTRICITY else 0,
            'water_value': (data.value or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
            'water_price': (data.price or 0) if data.data_type.name == DATA_TYPE_WATER else 0,
            'fuel_value': (data.value or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
            'fuel_price': (data.price or 0) if data.data_type.name == DATA_TYPE_FUEL else 0,
            'co2_value': (data.value or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
            'co2_price': (data.price or 0) if data.data_type.name == DATA_TYPE_CO2 else 0,
            'get_data_date': data.get_data_at,
            'device_id': entity_to_device[data.entity.id],
        }, queryset)

        return result
###
# TODO:廃止予定：ここまで
###


# JCreditApplicationのViewSet
@extend_schema_view(
    list=extend_schema(
        description='JCreditApplication',
    ),
)
class JCreditApplicationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.AllowAny,]
    serializer_class = JCreditApplicationSerializer

    def get_queryset(self):
        queryset =  JCreditApplication.objects.all()
        return queryset

###
# TODO:廃止予定：ここから
###
class DeviceListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            pushlog_apis = PushLogApi.objects.filter(company_id=company_id)
        else:
            pushlog_apis = PushLogApi.objects.filter(company_id=self.request.user.company_id_id)
        devices = Device.objects.filter(pushlog_api__in=pushlog_apis).select_related("m_device_id").order_by("-created_at")
        enable_data_collection = self.request.query_params.get('enable_data_collection', None)
        if enable_data_collection == 'true':
            devices = devices.filter(enable_data_collection=True)
        return devices

# IHI様２次開発要求仕様に合わせ、PFとの連携用にすべての機器を返すViewを作成
class DeviceAllListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AllDeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        devices = Device.objects.all()
        return devices

@extend_schema_view(
    retrieve=extend_schema(
        description='設備詳細',
    ),
    create=extend_schema(
        description='設備登録',
        request=DeviceSerializer,
        responses=DeviceSerializer,
    ),
    update=extend_schema(
        description='設備更新',
        request=DeviceSerializer,
        responses=DeviceSerializer,
    ),
    partial_update=extend_schema(
        description='設備部分更新',
        request=DeviceSerializer,
        responses=DeviceSerializer,
    ),
    destroy=extend_schema(
        description='設備削除',
        request=DeviceSerializer,
        responses=DeviceSerializer,
    )
)
class DeviceDetailViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.method == 'PATCH':
            device_id = self.kwargs.get('pk')
            return Device.objects.filter(pk=device_id)

        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            pushlog_apis = PushLogApi.objects.filter(company_id=company_id)
        else:
            pushlog_apis = PushLogApi.objects.filter(company_id=self.request.user.company_id_id)
        return Device.objects.all().filter(pushlog_api__in=pushlog_apis)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)
###
# TODO:廃止予定：ここまで
###

class MDeviceViewSet(viewsets.ModelViewSet):
    queryset = MDevice.objects.all()
    serializer_class = MDeviceSerializer
    permission_classes = [IsAuthenticated]



class CostPredictionMixin:

    def calc_yearly_cost_prediction(self, target_window_df, target_year_df, date_lte):
        if (len(target_window_df) == 0):
            return {
                "electrical_value": 0,
                "water_value": 0,
                "fuel_value": 0,
                "co2_value": 0,
                "total_utility_cost_value": 0,
                "electrical_price": 0,
                "water_price": 0,
                "fuel_price": 0,
                "co2_price": 0,
                "total_utility_cost_price": 0
            }

        electrical_data_type_id = DataType.objects.get(name=DATA_TYPE_ELECTRICITY).id
        water_data_type_id = DataType.objects.get(name=DATA_TYPE_WATER).id
        fuel_data_type_id = DataType.objects.get(name=DATA_TYPE_FUEL).id
        co2_data_type_id = DataType.objects.get(name=DATA_TYPE_CO2).id

        electrical_window_df = target_window_df[target_window_df['data_type_id'] == electrical_data_type_id]
        water_window_df = target_window_df[target_window_df['data_type_id'] == water_data_type_id]
        fuel_window_df = target_window_df[target_window_df['data_type_id'] == fuel_data_type_id]
        co2_window_df = target_window_df[target_window_df['data_type_id'] == co2_data_type_id]

        avg_electrical_value = electrical_window_df["value"].fillna(0).sum() / len(electrical_window_df) if len(electrical_window_df) > 0 else 0
        avg_water_value = water_window_df["value"].fillna(0).sum() / len(water_window_df) if len(water_window_df) > 0 else 0
        avg_fuel_value = fuel_window_df["value"].fillna(0).sum() / len(fuel_window_df) if len(fuel_window_df) > 0 else 0
        avg_co2_value = co2_window_df["value"].fillna(0).sum() / len(co2_window_df) if len(co2_window_df) > 0 else 0
        avg_electrical_price = electrical_window_df["price"].fillna(0).sum() / len(electrical_window_df) if len(electrical_window_df) > 0 else 0
        avg_water_price = water_window_df["price"].fillna(0).sum() / len(water_window_df) if len(water_window_df) > 0 else 0
        avg_fuel_price = fuel_window_df["price"].fillna(0).sum() / len(fuel_window_df) if len(fuel_window_df) > 0 else 0
        avg_co2_price = co2_window_df["price"].fillna(0).sum() / len(co2_window_df) if len(co2_window_df) > 0 else 0

        # 年の残りの月数を計算
        remaining_months = 12 - date_lte.month

        year_electrical_df = target_year_df[target_year_df['data_type_id'] == electrical_data_type_id]
        year_water_df = target_year_df[target_year_df['data_type_id'] == water_data_type_id]
        year_fuel_df = target_year_df[target_year_df['data_type_id'] == fuel_data_type_id]
        year_co2_df = target_year_df[target_year_df['data_type_id'] == co2_data_type_id]

        # 対象年の既存データの合計値を計算
        target_year_electrical_value = year_electrical_df["value"].fillna(0).sum() if "value" in year_electrical_df.columns else 0
        target_year_water_value = year_water_df["value"].fillna(0).sum() if "value" in year_water_df.columns else 0
        target_year_fuel_value = year_fuel_df["value"].fillna(0).sum() if "value" in year_fuel_df.columns else 0
        target_year_co2_value = year_co2_df["value"].fillna(0).sum() if "value" in year_co2_df.columns else 0
        target_year_electrical_price = year_electrical_df["price"].fillna(0).sum() if "price" in year_electrical_df.columns else 0
        target_year_water_price = year_water_df["price"].fillna(0).sum() if "price" in year_water_df.columns else 0
        target_year_fuel_price = year_fuel_df["price"].fillna(0).sum() if "price" in year_fuel_df.columns else 0
        target_year_co2_price = year_co2_df["price"].fillna(0).sum() if "price" in year_co2_df.columns else 0

        # 今年の光熱費の予測値を計算
        electrical_value_prediction = target_year_electrical_value + avg_electrical_value * remaining_months
        water_value_prediction = target_year_water_value + avg_water_value * remaining_months
        fuel_value_prediction = target_year_fuel_value + avg_fuel_value * remaining_months
        co2_value_prediction = target_year_co2_value + avg_co2_value * remaining_months
        electrical_price_prediction = target_year_electrical_price + avg_electrical_price * remaining_months
        water_price_prediction = target_year_water_price + avg_water_price * remaining_months
        fuel_price_prediction = target_year_fuel_price + avg_fuel_price * remaining_months
        co2_price_prediction = target_year_co2_price + avg_co2_price * remaining_months

        return {
            "electrical_value": round(electrical_value_prediction),
            "water_value": round(water_value_prediction),
            "fuel_value": round(fuel_value_prediction),
            "co2_value": round(co2_value_prediction),
            "total_utility_cost_value": round(electrical_value_prediction + water_value_prediction + fuel_value_prediction),
            "electrical_price": round(electrical_price_prediction),
            "water_price": round(water_price_prediction),
            "fuel_price": round(fuel_price_prediction),
            "co2_price": round(co2_price_prediction),
            "total_utility_cost_price": round(electrical_price_prediction + water_price_prediction + fuel_price_prediction)
        }


    def calc_monthly_cost_prediction(self, target_window_df, target_month_df, target_date):
        if (len(target_window_df) == 0):
            return {
                "electrical_value": 0,
                "water_value": 0,
                "fuel_value": 0,
                "co2_value": 0,
                "total_utility_cost_value": 0,
                "electrical_price": 0,
                "water_price": 0,
                "fuel_price": 0,
                "co2_price": 0,
                "total_utility_cost_price": 0
            }
        electrical_data_type_id = DataType.objects.get(name=DATA_TYPE_ELECTRICITY).id
        water_data_type_id = DataType.objects.get(name=DATA_TYPE_WATER).id
        fuel_data_type_id = DataType.objects.get(name=DATA_TYPE_FUEL).id
        co2_data_type_id = DataType.objects.get(name=DATA_TYPE_CO2).id

        electrical_window_df = target_window_df[target_window_df['data_type_id'] == electrical_data_type_id]
        water_window_df = target_window_df[target_window_df['data_type_id'] == water_data_type_id]
        fuel_window_df = target_window_df[target_window_df['data_type_id'] == fuel_data_type_id]
        co2_window_df = target_window_df[target_window_df['data_type_id'] == co2_data_type_id]

        avg_electrical_value = electrical_window_df["value"].fillna(0).sum() / len(electrical_window_df) if len(electrical_window_df) > 0 else 0
        avg_water_value = water_window_df["value"].fillna(0).sum() / len(water_window_df) if len(water_window_df) > 0 else 0
        avg_fuel_value = fuel_window_df["value"].fillna(0).sum() / len(fuel_window_df) if len(fuel_window_df) > 0 else 0
        avg_co2_value = co2_window_df["value"].fillna(0).sum() / len(co2_window_df) if len(co2_window_df) > 0 else 0
        avg_electrical_price = electrical_window_df["price"].fillna(0).sum() / len(electrical_window_df) if len(electrical_window_df) > 0 else 0
        avg_water_price = water_window_df["price"].fillna(0).sum() / len(water_window_df) if len(water_window_df) > 0 else 0
        avg_fuel_price = fuel_window_df["price"].fillna(0).sum() / len(fuel_window_df) if len(fuel_window_df) > 0 else 0
        avg_co2_price = co2_window_df["price"].fillna(0).sum() / len(co2_window_df) if len(co2_window_df) > 0 else 0

        # 月の残りの日数を計算
        _, this_month_last_day = calendar.monthrange(target_date.year, target_date.month)
        remaining_days = (this_month_last_day - target_date.day) + 1

        # 対象月の既存データの合計値を計算
        month_electrical_df = target_month_df[target_month_df['data_type_id'] == electrical_data_type_id]
        month_water_df = target_month_df[target_month_df['data_type_id'] == water_data_type_id]
        month_fuel_df = target_month_df[target_month_df['data_type_id'] == fuel_data_type_id]
        month_co2_df = target_month_df[target_month_df['data_type_id'] == co2_data_type_id]

        target_month_electrical_value = month_electrical_df["value"].fillna(0).sum() if "value" in month_electrical_df.columns else 0
        target_month_water_value = month_water_df["value"].fillna(0).sum() if "value" in month_water_df.columns else 0
        target_month_fuel_value = month_fuel_df["value"].fillna(0).sum() if "value" in month_fuel_df.columns else 0
        target_month_co2_value = month_co2_df["value"].fillna(0).sum() if "value" in month_co2_df.columns else 0
        target_month_electrical_price = month_electrical_df["price"].fillna(0).sum() if "price" in month_electrical_df.columns else 0
        target_month_water_price = month_water_df["price"].fillna(0).sum() if "price" in month_water_df.columns else 0
        target_month_fuel_price = month_fuel_df["price"].fillna(0).sum() if "price" in month_fuel_df.columns else 0
        target_month_co2_price = month_co2_df["price"].fillna(0).sum() if "price" in month_co2_df.columns else 0

        # 今月の光熱費の予測値を計算
        electrical_value_prediction = target_month_electrical_value + avg_electrical_value * remaining_days
        water_value_prediction = target_month_water_value + avg_water_value * remaining_days
        fuel_value_prediction = target_month_fuel_value + avg_fuel_value * remaining_days
        co2_value_prediction = target_month_co2_value + avg_co2_value * remaining_days
        electrical_price_prediction = target_month_electrical_price + avg_electrical_price * remaining_days
        water_price_prediction = target_month_water_price + avg_water_price * remaining_days
        fuel_price_prediction = target_month_fuel_price + avg_fuel_price * remaining_days
        co2_price_prediction = target_month_co2_price + avg_co2_price * remaining_days

        return {
            "electrical_value": round(electrical_value_prediction),
            "water_value": round(water_value_prediction),
            "fuel_value": round(fuel_value_prediction),
            "co2_value": round(co2_value_prediction),
            "total_utility_cost_value": round(electrical_value_prediction + water_value_prediction + fuel_value_prediction),
            "electrical_price": round(electrical_price_prediction),
            "water_price": round(water_price_prediction),
            "fuel_price": round(fuel_price_prediction),
            "co2_price": round(co2_price_prediction),
            "total_utility_cost_price": round(electrical_price_prediction + water_price_prediction + fuel_price_prediction)
        }

class MonthlyCostPredictionView(CostPredictionMixin, views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        now = timezone.now()
        year = int(request.query_params.get("year", now.year))
        month = int(request.query_params.get("month", now.month))

        date_lte = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now.year != year or now.month != month:
            _, last_day_of_month = monthrange(year, month)
            end_of_month = datetime.datetime(year, month, last_day_of_month).date()
            date_lte = end_of_month

        company_id = request.query_params.get("company_id", None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            root_entity = Company.objects.get(id=company_id).root_entity
            root_entity_id = root_entity.id if root_entity is not None else None
        else:
            root_entity_id = self.request.user.company_id.root_entity_id

        WINDOW_SIZE = 14
        target_window_data = Data.objects.filter(
            get_data_at__lte=date_lte,
            get_data_at__gte=date_lte - datetime.timedelta(days=WINDOW_SIZE),
            entity_id=root_entity_id,
            date_type=Data.DateType.DATE,
        ).order_by("get_data_at")
        target_month_data = Data.objects.filter(
            get_data_at__year=year,
            get_data_at__month=month,
            entity_id=root_entity_id,
            date_type=Data.DateType.DATE,
        ).order_by("get_data_at")

        target_window_df = pd.DataFrame.from_records(target_window_data.values())
        target_month_df = pd.DataFrame.from_records(target_month_data.values())

        predicted_values = self.calc_monthly_cost_prediction(target_window_df, target_month_df, date_lte)

        return Response(predicted_values)


class YearlyCostPredictionView(CostPredictionMixin, views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        now = timezone.now()
        year = int(request.query_params.get("year", now.year))
        date_lte = (
            datetime.datetime(now.year, now.month, 1)
            - relativedelta(days=1)
        )
        if now.year != year:
            date_lte = datetime.datetime(year, 12, 31).date()

        company_id = request.query_params.get("company_id", None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            root_entity = Company.objects.get(id=company_id).root_entity
            root_entity_id = root_entity.id if root_entity is not None else None
        else:
            root_entity_id = self.request.user.company_id.root_entity_id

        WINDOW_SIZE = 3
        target_window_data = Data.objects.filter(
            get_data_at__lte=date_lte,
            get_data_at__gte=(
                date_lte - relativedelta(months=WINDOW_SIZE)
            ),
            # pushlog_api__in=pushlog_apis,
            entity_id=root_entity_id,
            date_type=Data.DateType.MONTH,
        ).order_by("get_data_at")

        target_year_data = Data.objects.filter(
            get_data_at__year=date_lte.year,
            get_data_at__lte=date_lte,
            # pushlog_api__in=pushlog_apis
            entity_id=root_entity_id,
            date_type=Data.DateType.MONTH,
        ).order_by("get_data_at")

        target_window_df = pd.DataFrame.from_records(target_window_data.values())
        target_year_df = pd.DataFrame.from_records(target_year_data.values())

        predicted_values = self.calc_yearly_cost_prediction(
            target_window_df=target_window_df,
            target_year_df=target_year_df,
            date_lte=date_lte,
        )

        return Response(predicted_values)

class MonthlyCostTargetListAPIView(generics.ListAPIView):
    serializer_class = MonthlyCostTargetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            filters = {'company_id': company_id}
        else:
            filters = {'company_id': self.request.user.company_id}

        year = self.request.query_params.get('year')
        if year is not None:
            filters['year'] = year

        month = self.request.query_params.get('month')
        if month is not None:
            filters['month'] = month

        target_type = self.request.query_params.get('target_type')
        if target_type is not None:
            filters['target_type'] = target_type

        return MonthlyCostTarget.objects.filter(**filters)

class MonthlyCostTargetDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = MonthlyCostTargetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=self.kwargs["company_id"]).exists():
            raise PermissionDenied()
        return MonthlyCostTarget.objects.filter(
            company_id=self.kwargs["company_id"],
            year=self.kwargs["year"],
            month=self.kwargs["month"],
            target_type=self.kwargs["target_type"],
        )

    def get_object(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        target_type = self.kwargs['target_type']
        company_id = self.kwargs['company_id']
        return self.get_queryset().get(year=year, month=month, target_type=target_type, company_id=company_id)

    def put(self, request, *args, **kwargs):
        year = kwargs['year']
        month = kwargs['month']
        target_type = kwargs['target_type']
        company_id = kwargs['company_id']

        request.data['year'] = year
        request.data['month'] = month
        request.data['target_type'] = target_type
        request.data['company'] = company_id

        try:
            instance = self.get_object()
        except MonthlyCostTarget.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class GatewayListView(generics.ListCreateAPIView):
    serializer_class = GatewaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        gateway_ids = GatewayRegistration.objects.filter(company_id_id=company_id).values_list('gateway_master__gateway_id_id', flat=True)
        return Gateway.objects.filter(id__in=gateway_ids)

class GatewayDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GatewaySerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            company_id = self.request.user.company_id_id
        gateway_ids = GatewayRegistration.objects.filter(company_id_id=company_id).values_list('gateway_master__gateway_id_id', flat=True)
        return Gateway.objects.filter(id__in=gateway_ids)

class UnitListView(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

class UnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

class DeviceTypeListView(generics.ListAPIView):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class LiquidTypeListView(generics.ListAPIView):
    queryset = LiquidType.objects.all()
    serializer_class = LiquidTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class DeviceUnitPriceListView(generics.ListCreateAPIView):
    serializer_class = DeviceUnitPriceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        filters = {}
        device_id = self.request.query_params.get('device_id')
        if device_id is not None:
            filters['device_id'] = device_id

        return DeviceUnitPrice.objects.filter(**filters)

class DeviceUnitPriceUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeviceUnitPrice.objects.all()
    serializer_class = DeviceUnitPriceSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

class EconomicActivityTypeViewSet(viewsets.ModelViewSet):
    serializer_class = EconomicActivityTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.method == 'PATCH':
            activity_type_id = self.kwargs.get('pk')
            return EconomicActivityType.objects.filter(pk=activity_type_id)

        if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=self.request.user.company_id_id).exists():
            raise PermissionDenied()
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            return EconomicActivityType.objects.filter(company_id=company_id)
        return EconomicActivityType.objects.filter(user_id=self.request.user.company_id.admin_user_id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

class DailyEconomicActivityAmountViewSet(viewsets.ModelViewSet):
    serializer_class = DailyEconomicActivityAmountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        company_id = self.request.query_params.get('company_id', None)
        if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
            raise PermissionDenied()
        if company_id is not None:
            queryset = DailyEconomicActivityAmount.objects.filter(company_id=company_id).order_by('activity_date')
        else:
            queryset = DailyEconomicActivityAmount.objects.all().order_by('activity_date')

        # 各月の1日のデータをその月の原単位として扱う
        queryset = queryset.filter(activity_date__day=1)
        activity_data = map(
            lambda record: {
                "year": record.activity_date.year,
                "month": record.activity_date.month,
                "value": record.value,
            },
            queryset,
        )
        return Response(activity_data)

class EconomicActivityAmountUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyEconomicActivityAmountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return DailyEconomicActivityAmount.objects.filter(company_id=company_id)

    def get_object(self):
        date = self.kwargs['date']
        year = date.split('-')[0]
        month = date.split('-')[1]
        return self.get_queryset().get(activity_date__year=year, activity_date__month=month)

    def put(self, request, *args, **kwargs):
        company_id = kwargs['company_id']
        date = kwargs['date']

        request.data['company_id'] = company_id
        request.data['activity_date'] = date
        try:
            instance = self.get_object()
        except DailyEconomicActivityAmount.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except DailyEconomicActivityAmount.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class EconomicActivityUnitViewSet(viewsets.ModelViewSet):
    serializer_class = EconomicActivityUnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return EconomicActivityUnit.objects.filter()

class EntityDestroyView(generics.DestroyAPIView):
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company_id = self.kwargs.get('company_id')
        return Entity.objects.filter(company_id=company_id)

    def get_object(self):
        entity_id = self.kwargs['entity_id']
        return self.get_queryset().get(id=entity_id)

class EntityListCreateView(generics.ListCreateAPIView):
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]

    def read_leaf_entity_ids(self, company_id):
        subquery = DataStructure.objects.filter(
            ancestor=OuterRef('pk'),
            ancestor__company_id=company_id,
            depth__gt=0
        )
        return Entity.objects.annotate(
            has_children=Exists(subquery)
        ).filter(has_children=False).values('id')

    def get_queryset(self):
        company_id = self.kwargs.get('company_id')
        only_leaf_nodes = self.request.query_params.get('only_leaf_nodes', None)

        company = Company.objects.get(id=company_id)
        if company.admin_user_id == self.request.user:
            leaf_entity_ids = self.read_leaf_entity_ids(company_id)
            if only_leaf_nodes == 'true':
                return Entity.objects.filter(company_id=company_id, id__in=leaf_entity_ids)
            return Entity.objects.filter(company_id=company_id)

        permissions = UserEntityPermission.objects.filter(user_id=self.request.user.id, entity_id__company_id=company_id)
        entity_ids = permissions.values('entity_id')
        all_permit_entity_ids = DataStructure.objects.filter(ancestor_id__in=entity_ids).values('descendant_id')
        if only_leaf_nodes == 'true':
            leaf_entity_ids = self.read_leaf_entity_ids(company_id)
            target_entity_ids = all_permit_entity_ids.filter(descendant_id__in=leaf_entity_ids)
            return Entity.objects.filter(company_id=company_id, id__in=target_entity_ids)
        return Entity.objects.filter(company_id=company_id, id__in=all_permit_entity_ids)

    def create(self, request, *args, **kwargs):
        if "parent_entity_id" not in request.data:
            return Response(
                {"error": "parent_entity_idは必須です"}, status=status.HTTP_400_BAD_REQUEST
            )

        company_id = self.kwargs.get("company_id")
        data = request.data.copy()
        data["company"] = company_id
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            self.perform_create(serializer)
            created_entity = serializer.instance
            parent_entity = Entity.objects.get(id=request.data["parent_entity_id"])

            if (
                parent_entity is None
                or parent_entity.company.id != company_id
            ):
                return Response(
                    {"error": "parent_entity_idが不正です"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ancestor_entities = DataStructure.objects.filter(descendant=parent_entity)
            for ancestor_entity in ancestor_entities:
                DataStructure.objects.create(
                    ancestor=ancestor_entity.ancestor,
                    descendant=created_entity,
                    depth=ancestor_entity.depth + 1,
                )
            DataStructure.objects.create(
                ancestor=created_entity, descendant=created_entity, depth=0
            )

            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DataStructureListView(generics.ListAPIView):
    serializer_class = DataStructureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company_id = self.kwargs.get('company_id')
        return DataStructure.objects.filter(ancestor__company_id=company_id)


# /api/v1/entities/:entity_id/XXXX
def  update_final_result_for_entities(final_result, data, value_key, price_key, mode, fuel_unit, date_type):
    final_result_copy = final_result.copy()
    for item in data:
        item_datetime = item['get_data_at']
        item_year = item['get_data_at__year']
        item_month = item['get_data_at__month']
        item_date = item['get_data_at__day']
        item_hour = item['get_data_at__hour']
        item_minute = item['get_data_at__minute']

        # fuelの時には、下位階層の合計を求めるために、下位階層のレコードに祖先のentity_idをancestor_idに入れている
        item_entity_id = item['target_entity_id'] if value_key == 'fuel_value' else item['entity_id']
        entity_time_key = ''
        if date_type == Data.DateType.MINUTE:
            item_second = item['get_data_at__second']
            entity_time_key = f"{item_entity_id}-{item_year}-{item_month}-{item_date}-{item_hour}-{item_minute}-{item_second}"
        elif date_type == Data.DateType.HOUR:
            entity_time_key = f"{item_entity_id}-{item_year}-{item_month}-{item_date}-{item_hour}-{item_minute}"
        elif date_type == Data.DateType.DATE:
            entity_time_key = f"{item_entity_id}-{item_year}-{item_month}-{item_date}"
        elif date_type == Data.DateType.MONTH:
            entity_time_key = f"{item_entity_id}-{item_year}-{item_month}"
        elif date_type == Data.DateType.YEAR:
            entity_time_key = f"{item_entity_id}-{item_year}"

        if entity_time_key not in final_result_copy:
            if date_type == Data.DateType.MINUTE:
                final_result_copy[entity_time_key] = {
                    'year': item_year,
                    'month': item_month,
                    'date': item_date,
                    'hour': item_hour,
                    'minute': item_minute,
                    'second': item_second,
                    'electrical_value': 0,
                    'electrical_price': 0,
                    'water_value': 0,
                    'water_price': 0,
                    'fuel_value': 0,
                    'fuel_price': 0,
                    'co2_value': 0,
                    'co2_price': 0,
                    'get_data_date': item_datetime, # item['get_data_at'],
                    'entity_id': item_entity_id,
                    'fuel_unit': fuel_unit,
                }
            else:
                final_result_copy[entity_time_key] = {
                    'year': item_year,
                    'month': item_month,
                    'date': item_date,
                    'hour': item_hour,
                    'minute': item_minute,
                    'electrical_value': 0,
                    'electrical_price': 0,
                    'water_value': 0,
                    'water_price': 0,
                    'fuel_value': 0,
                    'fuel_price': 0,
                    'co2_value': 0,
                    'co2_price': 0,
                    'get_data_date': item_datetime, # item['get_data_at'],
                    'entity_id': item_entity_id,
                    'fuel_unit': fuel_unit,
                }

        if mode == "intensity":
            final_result_copy[entity_time_key][value_key] += (item[value_key + '_normalized'] if item[value_key + '_normalized'] is not None else 0)
            final_result_copy[entity_time_key][price_key] += (item[price_key + '_normalized'] if item[price_key + '_normalized'] is not None else 0)
        else:
            final_result_copy[entity_time_key][value_key] += item['sum_' + value_key] if item['sum_' + value_key] is not None else 0
            final_result_copy[entity_time_key][price_key] += item['sum_' + price_key] if item['sum_' + price_key] is not None else 0
        if item['get_data_at'] > final_result_copy[entity_time_key]['get_data_date']:
            final_result_copy[entity_time_key]['get_data_date'] = item['get_data_at']

    return final_result_copy


def validate_entity_permission(entity_id, user):
    entity = Entity.objects.filter(id=entity_id).first()
    has_some_entity_permission = entity and UserEntityPermission.objects.filter(user_id=user.id, entity__company_id=entity.company.id).exists()
    if entity_id is not None:
        entity = Entity.objects.get(id=entity_id)
        if entity.company.admin_user_id != user and not has_some_entity_permission:
            raise PermissionDenied()

# DataPerHourViewSet()を元に作成
class EntitiesDataPerHourViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'entity_id'
    serializer_class = EntitiesDataPerHourSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        activity_id = self.request.query_params.get('activity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        entity_id = self.kwargs['entity_id']
        validate_entity_permission(entity_id, self.request.user)

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        # if activity_id is not None:
        #     target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
        #     entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
        #     data_per_hour = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.HOUR).order_by('get_data_at')
        # else:
        #     if company_id is not None:
        #         if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
        #             raise PermissionDenied()
        #         if entity_id is not None:
        #             root_entity_id = entity_id
        #         else:
        #             root_entity = Company.objects.get(id=company_id).root_entity
        #             root_entity_id = root_entity.id if root_entity is not None else None
        #             if root_entity_id is None:
        #                 raise PermissionDenied()
        #     elif entity_id is not None:
        #         root_entity_id = entity_id
        #     else:
        #         root_entity_id = self.request.user.company_id.root_entity_id
        #     data_per_hour = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.HOUR).order_by('get_data_at')

        # ここから追加
        ancestor_id = self.kwargs['entity_id']
        entity_ids = [ds.descendant.id for ds in DataStructure.objects.filter(ancestor_id=ancestor_id, depth=1)]
        data_per_hour = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.HOUR).order_by('get_data_at')
        # ここまで

        if year is not None and month is not None and date is not None:
            data_per_hour = data_per_hour.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date).order_by('get_data_at')
            if start is not None and end is not None:
                data_per_hour = data_per_hour.filter(get_data_at__time__range=(int(start), int(end))).order_by('get_data_at')
        fuel_data = get_fuel_descendant_value(data_per_hour, Data.DateType.HOUR)
        if year is not None and month is not None and date is not None:
            fuel_data = fuel_data.filter(get_data_at__year=year, get_data_at__month=month, get_data_at__day=date).order_by('get_data_at')
            if start is not None and end is not None:
                fuel_data = fuel_data.filter(get_data_at__time__range=(int(start), int(end))).order_by('get_data_at')

        aggregated_electrical_data = data_per_hour.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_hour.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_hour.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'target_entity_id'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0.0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_hour.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result_for_entities(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.HOUR)
        final_result = update_final_result_for_entities(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.HOUR)
        final_result = update_final_result_for_entities(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.HOUR)
        final_result = update_final_result_for_entities(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.HOUR)

        final_result_list = list(final_result.values())

        return final_result_list

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        return obj

# DataPerDateViewSet()を元に作成
class EntitiesDataPerDateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'entity_id'
    serializer_class = EntitiesDataPerDateSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        # weekは月の中での週番号
        week = self.request.query_params.get('week', None)
        activity_id = self.request.query_params.get('activity_id', None)
        # company_id = self.request.query_params.get('company_id', None)
        # entity_id = self.request.query_params.get('entity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        entity_id = self.kwargs['entity_id']
        validate_entity_permission(entity_id, self.request.user)

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        # if activity_id is not None:
        #     target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
        #     entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
        #     data_per_date = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.DATE).order_by('get_data_at')
        # else:
        #     if company_id is not None:
        #         if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
        #             raise PermissionDenied()
        #         if entity_id is not None:
        #             root_entity_id = entity_id
        #         else:
        #             root_entity = Company.objects.get(id=company_id).root_entity
        #             root_entity_id = root_entity.id if root_entity is not None else None
        #             if root_entity_id is None:
        #                 raise PermissionDenied()
        #     elif entity_id is not None:
        #         root_entity_id = entity_id
        #     else:
        #         root_entity_id = self.request.user.company_id.root_entity_id
        #     data_per_date = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.DATE).order_by('get_data_at')

        # ここから追加
        ancestor_id = self.kwargs['entity_id']
        entity_ids = [ds.descendant.id for ds in DataStructure.objects.filter(ancestor_id=ancestor_id, depth=1)]
        data_per_date = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.DATE).order_by('get_data_at')
        # ここまで

        if year is not None and month is not None:
            if week is None:
                data_per_date = data_per_date.filter(get_data_at__year=year, get_data_at__month=month).order_by('get_data_at')
            else:
                first_date, last_date = get_week_range(int(year), int(month), int(week))
                data_per_date = data_per_date.filter(get_data_at__range=(first_date, last_date)).order_by('get_data_at')
            if start is not None and end is not None:
                data_per_date = data_per_date.filter(get_data_at__day__range=(int(start), int(end))).order_by('get_data_at')
        fuel_data = get_fuel_descendant_value(data_per_date, Data.DateType.DATE)
        if year is not None and month is not None:
            if week is None:
                fuel_data = fuel_data.filter(get_data_at__year=year, get_data_at__month=month).order_by('get_data_at')
            else:
                first_date, last_date = get_week_range(int(year), int(month), int(week))
                fuel_data = fuel_data.filter(get_data_at__range=(first_date, last_date)).order_by('get_data_at')
            if start is not None and end is not None:
                fuel_data = fuel_data.filter(get_data_at__day__range=(int(start), int(end))).order_by('get_data_at')

        aggregated_electrical_data = data_per_date.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_date.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_date.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'target_entity_id'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0.0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_date.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result_for_entities(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.DATE)
        final_result = update_final_result_for_entities(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.DATE)
        final_result = update_final_result_for_entities(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.DATE)
        final_result = update_final_result_for_entities(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.DATE)

        final_result_list = list(final_result.values())

        return final_result_list

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        return obj


# DataPerMonthViewSet()を元に作成
class EntitiesDataPerMonthViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'entity_id'
    serializer_class = EntitiesDataPerMonthSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        activity_id = self.request.query_params.get('activity_id', None)
        # company_id = self.request.query_params.get('company_id', None)
        # entity_id = self.request.query_params.get('entity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        entity_id = self.kwargs['entity_id']
        validate_entity_permission(entity_id, self.request.user)

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        # if activity_id is not None:
        #     target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
        #     entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
        #     data_per_month = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.MONTH).order_by('get_data_at')
        # else:
        #     if company_id is not None:
        #         if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
        #             raise PermissionDenied()
        #         if entity_id is not None:
        #             root_entity_id = entity_id
        #         else:
        #             root_entity = Company.objects.get(id=company_id).root_entity
        #             root_entity_id = root_entity.id if root_entity is not None else None
        #             if root_entity_id is None:
        #                 raise PermissionDenied()
        #     elif entity_id is not None:
        #         root_entity_id = entity_id
        #     else:
        #         root_entity_id = self.request.user.company_id.root_entity_id
        #     data_per_month = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.MONTH).order_by('get_data_at')

        # ここから追加
        ancestor_id = self.kwargs['entity_id']
        entity_ids = [ds.descendant.id for ds in DataStructure.objects.filter(ancestor_id=ancestor_id, depth=1)]
        data_per_month = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.MONTH).order_by('get_data_at')
        # ここまで

        if year is not None:
            data_per_month = data_per_month.filter(get_data_at__year=year).order_by('get_data_at')
            if start is not None and end is not None:
                data_per_month = data_per_month.filter(get_data_at__month__range=(int(start), int(end))).order_by('get_data_at')
        fuel_data = get_fuel_descendant_value(data_per_month, Data.DateType.MONTH)
        if year is not None:
            fuel_data = fuel_data.filter(get_data_at__year=year).order_by('get_data_at')
            if start is not None and end is not None:
                fuel_data = fuel_data.filter(get_data_at__month__range=(int(start), int(end))).order_by('get_data_at')

        aggregated_electrical_data = data_per_month.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_month.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_month.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'target_entity_id'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_month.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result_for_entities(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.MONTH)
        final_result = update_final_result_for_entities(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.MONTH)
        final_result = update_final_result_for_entities(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.MONTH)
        final_result = update_final_result_for_entities(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.MONTH)

        final_result_list = list(final_result.values())

        return final_result_list

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        return obj

# DataPerYearViewSet()を元に作成
class EntitiesDataPerYearViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'entity_id'
    serializer_class = EntitiesDataPerYearSerializer

    def get_queryset(self):
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        activity_id = self.request.query_params.get('activity_id', None)
        # company_id = self.request.query_params.get('company_id', None)
        # entity_id = self.request.query_params.get('entity_id', None)
        fuel_unit = self.request.query_params.get('fuel_unit', 'm3')

        # エンティティに許可があるかチェック
        entity_id = self.kwargs['entity_id']
        validate_entity_permission(entity_id, self.request.user)

        # 最新のDailyEconomicActivityAmountのvalueを取得
        latest_values = DailyEconomicActivityAmount.objects.filter(
            activity_type_id=activity_id
        ).order_by('-activity_date').values('value')[:1]

        # if activity_id is not None:
        #     target_activity_devices = Device.objects.filter(economic_activity_type_id=activity_id).select_related('entity')
        #     entity_ids = [device.entity.id for device in target_activity_devices if device.entity is not None]
        #     data_per_year = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.YEAR).order_by('get_data_at')
        # else:
        #     if company_id is not None:
        #         if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
        #             raise PermissionDenied()
        #         if entity_id is not None:
        #             root_entity_id = entity_id
        #         else:
        #             root_entity = Company.objects.get(id=company_id).root_entity
        #             root_entity_id = root_entity.id if root_entity is not None else None
        #             if root_entity_id is None:
        #                 raise PermissionDenied()
        #     elif entity_id is not None:
        #         root_entity_id = entity_id
        #     else:
        #         root_entity_id = self.request.user.company_id.root_entity_id
        #     data_per_year = Data.objects.filter(entity_id=root_entity_id, date_type=Data.DateType.YEAR).order_by('get_data_at')
        # if start is not None and end is not None:
        #     data_per_year = data_per_year.filter(get_data_at__year__range=(int(start), int(end))).order_by('get_data_at')

        # ここから追加
        ancestor_id = self.kwargs['entity_id']
        entity_ids = [ds.descendant.id for ds in DataStructure.objects.filter(ancestor_id=ancestor_id, depth=1)]
        data_per_year = Data.objects.filter(entity_id__in=entity_ids, date_type=Data.DateType.YEAR).order_by('get_data_at')
        # ここまで
        fuel_data = get_fuel_descendant_value(data_per_year, Data.DateType.YEAR)

        aggregated_electrical_data = data_per_year.filter(data_type__name=DATA_TYPE_ELECTRICITY).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_electrical_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_electrical_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            electrical_value_normalized=Round2(F('sum_electrical_value') / F('latest_value')),
            electrical_price_normalized=Round2(F('sum_electrical_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_water_data = data_per_year.filter(data_type__name=DATA_TYPE_WATER).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_water_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_water_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            water_value_normalized=Round2(F('sum_water_value') / F('latest_value')),
            water_price_normalized=Round2(F('sum_water_price') / F('latest_value')),
        ).order_by('get_data_at')

        # 燃料は子孫までたどって、最下層のデータを単位と比重で変換する
        # aggregated_fuel_data = data_per_year.filter(data_type__name=DATA_TYPE_FUEL).values(
        aggregated_fuel_data = fuel_data.filter(data_type__name=DATA_TYPE_FUEL).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'target_entity_id'
        ).annotate(
            fuel_unit=Value(fuel_unit, output_field=models.CharField()),
        ).annotate(
            new_value=Case(
                When(fuel_unit='L', then=Value(1000) * Coalesce(F('value'), 0.0)),
                When(fuel_unit='kg', then=Value(1000) * Coalesce(F('value'), 0.0) * F('rho')),
                default=Coalesce(F('value'), 0.0),
                output_field=FloatField()
            )
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_fuel_value=Round2(Coalesce(Sum('new_value'), 0.0)),
            sum_fuel_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            fuel_value_normalized=Round2(F('sum_fuel_value') / F('latest_value')),
            fuel_price_normalized=Round2(F('sum_fuel_price') / F('latest_value')),
        ).order_by('get_data_at')

        aggregated_co2_data = data_per_year.filter(data_type__name=DATA_TYPE_CO2).values(
            'value', 'price', 'get_data_at', 'get_data_at__year', 'get_data_at__month', 'get_data_at__day', 'get_data_at__hour', 'get_data_at__minute', 'entity_id'
        ).annotate(
            latest_value=Subquery(latest_values),
            sum_co2_value=Round2(Coalesce(Sum('value'), 0.0)),
            sum_co2_price=Round2(Coalesce(Sum('price'), 0)),
        ).annotate(
            co2_value_normalized=Round2(F('sum_co2_value') / F('latest_value')),
            co2_price_normalized=Round2(F('sum_co2_price') / F('latest_value')),
        ).order_by('get_data_at')

        final_result = {}
        mode = self.request.query_params.get('mode')
        final_result = update_final_result_for_entities(final_result, aggregated_electrical_data, 'electrical_value', 'electrical_price', mode, fuel_unit, Data.DateType.YEAR)
        final_result = update_final_result_for_entities(final_result, aggregated_water_data, 'water_value', 'water_price', mode, fuel_unit, Data.DateType.YEAR)
        final_result = update_final_result_for_entities(final_result, aggregated_fuel_data, 'fuel_value', 'fuel_price', mode, fuel_unit, Data.DateType.YEAR)
        final_result = update_final_result_for_entities(final_result, aggregated_co2_data, 'co2_value', 'co2_price', mode, fuel_unit, Data.DateType.YEAR)

        final_result_list = list(final_result.values())

        return final_result_list

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        return obj

# 単価履歴
#   field :
#     'electric_unit_price' :   "電気(円/kWh)",
#     'water_unit_price'    :   "水(円/m3)",
#     'fuel_unit_price'     :   "燃料(円/m3)",
#     'co2_unit_price'      :   "CO2(円/t-CO2)",
#     'electric_unit_co2'   :   "電気(t-CO2/kWh)",
#     'water_unit_co2'      :   "水(t-CO2/m3)",
#     'fuel_unit_co2'       :   "燃料(t-CO2/m3)",
class UnitPriceHistoryView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnitPriceHistorySerializer

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)
        field = self.request.query_params.get('field', None)

        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            data = UnitPriceHistory.objects.filter(company_id=company_id)
        else:
            data = UnitPriceHistory.objects.all()

        if field is not None:
            data = data.filter(field=field)
        return data.order_by('created_at')

    def create(self, request, *args, **kwargs):
        company_id = self.request.data.get('company_id', None)
        field = self.request.data.get('field', None)
        before = self.request.data.get('before', None)
        after = self.request.data.get('after', None)
        name = self.request.data.get('name', None)

        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            company = Company.objects.filter(id=company_id).first()
            if company is None or company.admin_user_id != self.request.user:
                raise PermissionDenied()

        if field is None or before is None or after is None or name is None:
            return Response(
                {"detail": "Invalid field, before, after or name."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(before, (int, float)) or not isinstance(after, (int, float)):
            return Response(
                {"detail": "Invalid before or after."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if before < 0 or after < 0:
            return Response(
                {"detail": "before or after must be greater than 0."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if before == after:
            return Response(
                {"detail": "before and after must be different."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "Invalid data.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

class LatestUnitPriceView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnitPriceHistorySerializer

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id', None)

        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            queryset = UnitPriceHistory.objects.filter(company_id=company_id)
        else:
            queryset = UnitPriceHistory.objects.none()

        # 各フィールドごとの最新の日付を取得
        latest_dates = queryset.values('field').annotate(latest_date=Max('created_at'))

        # 最新の日付を持つレコードのみを取得
        latest_records = [queryset.filter(field=entry['field'], created_at=entry['latest_date']).first() for entry in latest_dates]

        return latest_records

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = {record.field: record.after for record in queryset if record is not None}
        return Response(response_data)


class UserEntityPermissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserEntityPermissionSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        entity_id = self.request.query_params.get('entity_id', None)
        only_user_permitted = self.request.query_params.get('only_user_permitted', False)

        company = Company.objects.filter(id=company_id).first()
        if company is None or (only_user_permitted != 'true' and company.admin_user_id != self.request.user):
            raise PermissionDenied()

        if not CompanyUser.objects.filter(
            user_id=self.request.user.id, company_id=company_id
        ).exists():
            raise PermissionDenied()

        user_ids = CompanyUser.objects.filter(
            company_id=company_id
        ).values('user_id')

        if entity_id is not None:
            if only_user_permitted == 'true':
                return UserEntityPermission.objects.filter(
                    user_id=self.request.user.id,
                    entity_id=entity_id
                ).order_by("created_at")
            return UserEntityPermission.objects.filter(
                user_id__in=user_ids,
                entity_id=entity_id
            ).order_by("created_at")

        if only_user_permitted == 'true':
            return UserEntityPermission.objects.filter(
                user_id=self.request.user.id,
            ).order_by("created_at")
        return UserEntityPermission.objects.filter(
            user_id__in=user_ids,
        ).order_by("created_at")

    def create(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        company = Company.objects.filter(id=company_id).first()
        if company is None or company.admin_user_id != self.request.user:
            raise PermissionDenied()

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            if not CompanyUser.objects.filter(
                user_id=user.id, company_id=company_id
            ).exists():
                return Response(
                    {"detail": "Invalid company or user."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            entity = serializer.validated_data.get('entity')
            if company_id != entity.company_id:
                return Response(
                    {"detail": "Invalid company or entity."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            self.send_email_to_user(request.user, user, entity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email_to_user(self, from_user, to_user, entity):
        message = Mail(
            from_email = SENDER_EMAIL,
            to_emails = [to_user.email],
            subject = 'エンティティに対するアクセス権限が付与されました',
            plain_text_content = f'{from_user.username}さんから「{entity.name}」に対するアクセス権限が付与されました。\n{FRONTEND_URL}'
        )
        try:
            SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            e_str = str(e)
            logging.info(f"ユーザーエンティティ権限の付与のメール通知でエラーが発生しました。：{e_str}")

class UserEntityPermissionDestroyView(generics.DestroyAPIView):
    serializer_class = UserEntityPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserEntityPermission.objects.all()

    def destroy(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        company = Company.objects.filter(id=company_id).first()
        if company is None or company.admin_user_id != self.request.user:
            raise PermissionDenied()

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name='start_datetime',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                required=True,
                description='YYYY-MM-DDTHH:MM:SS 形式の開始日時'
            ),
            OpenApiParameter(
                name='end_datetime',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                required=True,
                description='YYYY-MM-DDTHH:MM:SS 形式の終了日時'
            ),
        ],
        responses={200: OpenApiTypes.BINARY, 400: OpenApiTypes.STR},
        description='start_datetime から end_datetime までの、指定した企業の1分周期データの CSV ファイルを返却',
    )
)
class MinutelyDataCSVDownload(views.APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CSVRenderer]

    def get(self, request, company_id):
        start_datetime = request.query_params.get('start_datetime', None)
        end_datetime = request.query_params.get('end_datetime', None)
        if start_datetime is None or end_datetime is None:
            return Response(
                {"detail": "Invalid start_datetime or end_datetime."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_datetime = datetime.datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S').replace(second=0, microsecond=0).astimezone(timezone.utc)
        end_datetime = datetime.datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S').replace(second=0, microsecond=0).astimezone(timezone.utc)

        response = create_minutely_channel_csv_response(company_id, start_datetime, end_datetime)
        return response

class HourlyDataCSVDownloadView(views.APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CSVRenderer]

    def get(self, request, company_id):
        start_datetime = request.query_params.get('start_datetime', None)
        end_datetime = request.query_params.get('end_datetime', None)
        if start_datetime is None or end_datetime is None:
            return Response(
                {"detail": "Invalid start_datetime or end_datetime."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_datetime = datetime.datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S').replace(second=0, microsecond=0).astimezone(timezone.utc)
        end_datetime = datetime.datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M:%S').replace(second=0, microsecond=0).astimezone(timezone.utc)

        response = create_hourly_channel_csv_response(company_id, start_datetime, end_datetime)
        return response

class DailyDataCSVDownloadView(views.APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CSVRenderer]

    def get(self, request, company_id):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        if start_date is None or end_date is None:
            return Response(
                {"detail": "Invalid start_date or end_date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0 ,second=0, microsecond=0).astimezone(timezone.utc)
        end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(timezone.utc)

        response = create_daily_channel_csv_response(company_id, start_datetime, end_datetime)
        return response

class CSVUploadError(Exception):
    """
    CSVアップロード時に発生するエラーを表すカスタム例外クラス。

    Attributes:
        message (str): エラーメッセージ。
        http_status (status): HTTPステータスコード。デフォルトは400 (Bad Request)。
    """
    def __init__(self, message, http_status=status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.http_status = http_status

@extend_schema(
    tags=['CSV Upload'],
    operation_id='upload_csv',
    summary='CSVファイルのアップロード',
    description='CSVファイルをアップロードし、サーバー側で処理します。',
    request={
        'content': {
            'multipart/form-data': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'file': {
                            'type': 'string',
                            'format': 'binary',
                            'description': 'アップロードするCSVファイル',
                        }
                    },
                    'required': ['file'],
                }
            }
        }
    },
    responses={
        201: OpenApiExample(
            '成功例',
            summary='正常にアップロードされました',
            value='ファイルが正常にアップロードされました。',
        ),
        400: OpenApiExample(
            'エラー例',
            summary='CSVファイルが含まれていません。',
            value='CSVファイルが含まれていません。',
        ),
        409: OpenApiExample(
            name='既存データエラー',
            summary='このゲートウェイ名はpushlogのゲートウェイとして登録済みです。',
            value='ここのゲートウェイ名はpushlogのゲートウェイとして登録済みです。',
        ),
        422: [
            OpenApiExample(
                name='入力データ不正エラー',
                summary='入力データが不正です。',
                value='ゲートウェイ名が記載されていません。',
            ),
            OpenApiExample(
                name='入力データ不正エラー',
                summary='入力データが不正です。',
                value='CH名が一致しませんでした。',
            ),
            OpenApiExample(
                name='入力データ不正エラー',
                summary='データの書式が不正です。',
                value='日時の書式が正しくないか、数値データが数値でない可能性があります。'
            ),
            OpenApiExample(
                name='入力データ不正エラー',
                summary='データの書式が不正です。',
                value='データが空です。'
            ),
        ],
        500: OpenApiExample(
            name='サーバーエラー',
            summary='内部サーバーエラーが発生しました。',
            value='エラーが発生しました。',
        ),
    },
)
class CSVUploadView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, company_id):
        start_time = datetime.datetime.now()
        # 処理が終わった後に経過時間を計算
        if 'file' not in request.FILES:
            return Response("CSVファイルが含まれていません。", status=status.HTTP_400_BAD_REQUEST)

        company = Company.objects.get(id=company_id)

        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)
        # 先頭行を読み込む（ゲートウェイIDが記載されている）、BOMがついているので消さないと文字列照合で不一致になる
        special_header = next(reader)
        gateway_id = special_header[0].replace("\ufeff", "")
        gateway_name = special_header[1] if len(special_header) >= 2 else None
        if gateway_id == "":
            return Response("ゲートウェイIDが記載されていません。", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if gateway_name is None or gateway_name == "":
            gateway_name = gateway_id

        # ２行目をCSVとして読み込む（２列目以降に、CH名＝データ取得対象名が羅列されている）
        csv_header = next(reader)

        # トランザクション管理の開始
        # ロールバックのため、transactionの内部では、異常があった場合はExceptionを起こしている
        try:
            with transaction.atomic():
                # ゲートウェイを取得/作成して、CH=データ取得対象＝Deviceを生成する
                device_no_to_entity_dict = self.get_or_create_gateway_and_device(company, gateway_id, gateway_name, csv_header)

                # 残り全てのデータを読み込んで、先頭をdatetimeに変換したlistのlistを準備する
                # 変換時にエラーが出たなら、不正データが含まれている
                try:
                    coefficient = 0.001     # Whの値で来るのをkWhに変換
                    line_list = [[self.parse_datetime_with_timezone(row[0])] + [(float(value)*coefficient if value else 0.0) for value in row[1:]] for row in reader]
                except:
                    raise CSVUploadError("日時の書式が正しくないか、数値データが数値でない可能性があります。", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                if len(line_list) == 0:
                    raise CSVUploadError("データが空です。", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                data_type = DataType.objects.filter(name=DATA_TYPE_ELECTRICITY).first() # 電力

                # 分単位のデータを作成、元々のデータの時間間隔情報も取得
                date_type = Data.DateType.MINUTE    # 分単位
                line_list.sort()
                one_minute_list, interval_sec, interval_min = self.make_one_minute_datas(line_list)
                self.save_aggregated_data(one_minute_list, company, device_no_to_entity_dict, data_type, date_type)

                # 時間単位データの更新・作成
                date_type = Data.DateType.HOUR      # 時間単位
                new_list = self.aggregate_data(one_minute_list, date_type)
                self.save_aggregated_data(new_list, company, device_no_to_entity_dict, data_type, date_type)

                # 日単位データの更新・作成
                date_type = Data.DateType.DATE      # 日単位
                new_list = self.aggregate_data(new_list, date_type)
                self.save_aggregated_data(new_list, company, device_no_to_entity_dict, data_type, date_type)

                # 月単位データの更新・作成
                date_type = Data.DateType.MONTH     # 月単位
                new_list = self.aggregate_data(new_list, date_type)
                self.save_aggregated_data(new_list, company, device_no_to_entity_dict, data_type, date_type)

                # 年単位データの更新・作成
                date_type = Data.DateType.YEAR      # 年単位
                new_list = self.aggregate_data(new_list, date_type)
                self.save_aggregated_data(new_list, company, device_no_to_entity_dict, data_type, date_type)

                # アップロード履歴の作成
                CsvUploadHistory.objects.create(company_id=company.id, file_name=csv_file.name, size_bytes=csv_file.size)

        except CSVUploadError as e:
            return Response(str(e), status=e.http_status)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return Response("エラーが発生しました。"+str(traceback_str), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # return Response("エラーが発生しました。"+str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        # 経過時間を計算
        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        return Response({"message": "ファイルが正常にアップロードされました。", "elapsed_seconds": elapsed_time, "file_name": csv_file.name}, status=status.HTTP_201_CREATED)

    def parse_datetime_with_timezone(self, line):
        try:
            # 秒が含まれている場合のフォーマットで試す
            dt_naive = datetime.datetime.strptime(line, '%Y/%m/%d %H:%M:%S')
        except:
            # 秒が含まれていない場合のフォーマットで試す
            dt_naive = datetime.datetime.strptime(line, '%Y/%m/%d %H:%M')
                
        # タイムゾーン情報を追加してタイムゾーン対応の日時オブジェクトを生成
        dt_aware = timezone.make_aware(dt_naive, timezone.get_default_timezone())
        return dt_aware
    
    def get_or_create_gateway_and_device(self, company, gateway_id, gateway_name, csv_header):
        """
        会社とゲートウェイID、CSVヘッダーを受け取り、ゲートウェイとデバイスを取得または作成します。
        
        この関数は、指定された会社とゲートウェイIDに基づいてゲートウェイを検索し、存在しない場合は新たに作成します。
        また、CSVヘッダーに基づいてデバイスを確認または作成し、デバイス番号とエンティティの辞書を返します。
        ゲートウェイ名がpushlogのゲートウェイとして既に登録されている場合や、CH名が一致しない場合は例外を発生させます。
        
        Parameters:
        company (Company): デバイスが属する会社のインスタンス。
        gateway_id (str): ゲートウェイのID。
        csv_header (list): CSVファイルのヘッダー情報。
        
        Returns:
        dict: デバイス番号とエンティティの辞書。
              処理が成功した場合、デバイス番号と対応するエンティティのマッピングが含まれます。
        
        Raises:
        CSVUploadError: ゲートウェイ名がpushlogのゲートウェイとして既に登録されている場合、またはCH名が一致しない場合に発生します。
        """
        # Gatewayを取得する
        gateway = Gateway.objects.filter(id=gateway_id).first()
        if gateway:
            if gateway.pushlog_api != None:
                # pushlog_api_keyがあるということはpushlogのゲートウェイとして登録されているのでエラー
                raise CSVUploadError("このゲートウェイはpushlogのゲートウェイとして登録済みです。", http_status=status.HTTP_409_CONFLICT)

            # GatewayRegistration（companyとgateway_masterの中間テーブル）を検索する
            gateway_registration = GatewayRegistration.objects.filter(company_id=company, gateway_master__gateway_id__id=gateway_id).first()

            if gateway_registration is not None:
                # ゲートウェイが登録されている場合、CH=データ取得対象＝Deviceを確認する
                devices = Device.objects.filter(gateway_id=gateway, input_source=Device.InputSource.CSV)
                device_dict = {device.device_number: device.data_source_name for device in devices}
                csv_ch_dict = {ch_no: ch_name for ch_no, ch_name in enumerate(csv_header[1:], 1)}
                if device_dict != csv_ch_dict:
                    raise CSVUploadError("CH名が一致しませんでした。", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                # 他の企業に登録されている
                raise CSVUploadError("このゲートウェイは登録済みです。", http_status=status.HTTP_409_CONFLICT)
        else:
            # ゲートウェイを作成する
            gateway = Gateway.objects.create(id=gateway_id, name=gateway_name, pushlog_api=None)

            # GatewayMasterを生成する
            gateway_master = GatewayMaster.objects.create(gateway_type="CSV_upload", gateway_id=gateway)
            # GatewayRegistrationを生成する
            GatewayRegistration.objects.create(gateway_master=gateway_master, company_id=company)

            # CH=データ取得対象＝Deviceを生成する
            for ch_no, ch_name in enumerate(csv_header[1:], 1):
                # entityを生成する
                entity_name = f"{gateway_id}-{ch_no}"
                entity = Entity.objects.create(name=entity_name, company=company)
                # deviceを生成する
                device_name = f"{gateway_id}-{ch_no}"
                Device.objects.create(name=device_name, data_source_name=ch_name, device_number=ch_no, 
                                               gateway_id=gateway, input_source=Device.InputSource.CSV,
                                               entity=entity)
            devices = Device.objects.filter(gateway_id=gateway)
        device_no_to_entity_dict = {device.device_number: device.entity for device in devices}
        return device_no_to_entity_dict

    def make_one_minute_datas(self, line_list):
        """
        1分間隔のデータを生成する。
        元データの時間間隔は、必ずしも固定でなく、数秒程度の揺らぎがあることを前提とする

        Args:
        line_list (list): 元のデータリスト。各要素は日時オブジェクトと複数の数値データを含むリスト。

        Returns:
        tuple: 生成された1分間隔のデータリスト、データ間隔の秒数、データ間隔の分数を含むタプル。
        """
        # 最小の時間差を求める
        min_time_diff_seconds = min((b[0] - a[0] for a, b in zip(line_list, line_list[1:])), default=datetime.timedelta(0)).total_seconds()

        # データ間隔が何分区切りに近いかを
        interval_min = int((min_time_diff_seconds + 30) // 60)
        # 10秒区切りでどこに近いか
        interval_sec = int(((min_time_diff_seconds+9) // 10) * 10) 

        result_list = []
        if interval_min <= 1:   # 1分以内の間隔の場合
            # 時間情報で秒以下を0にして丸める
            for row in line_list:
                row[0] = row[0].replace(second=0, microsecond=0)
            # 同じ時間のデータは、各要素の値の合計を求める
            for key, group in groupby(line_list, key=itemgetter(0)):
                # 各グループ内で値を合計（空白orNoneな項目は0.0として扱う）
                sum_values = [sum(values) for values in zip(*[item[1:] for item in group])]
                result_list.append([key] + sum_values)
        else:   # 1分より大きい間隔の場合
            # 時間情報で秒以下を0にして丸め、1分単位で分割して昇順にソートする
            line_list = sorted(
                [[row[0].replace(second=0, microsecond=0) + datetime.timedelta(minutes=i)] + [value / interval_min for value in row[1:]]
                 for row in line_list for i in range(interval_min)], key=lambda x: x[0])
            # 同じ時間のデータは、各要素の値の合計を求める
            for key, group in groupby(line_list, key=itemgetter(0)):
                # 各グループ内で値を合計（空白orNoneな項目は0.0として扱う）
                sum_values = [sum(values) for values in zip(*[item[1:] for item in group])]
                result_list.append([key] + sum_values)
        return result_list, interval_sec, interval_min


    def aggregate_data(self, line_list, date_type):
        """
        指定された日付タイプに基づいてデータを集計する。

        この関数は、指定された日付タイプ（時間、日、月、年）に基づいて、入力されたデータリストを集計します。
        各データ行は、最初の要素として日時オブジェクトを持ち、その後に数値データが続きます。
        集計は、指定された日付タイプに応じて、日時オブジェクトを丸めることによって行われます。
        例えば、時間単位で集計する場合、分、秒、マイクロ秒は0に設定されます。
        集計されたデータは、同じ丸められた日時を持つ行の数値データの合計として計算されます。

        Args:
            line_list (list): 集計するデータのリスト。各要素は日時オブジェクトと数値データを含むリスト。
            date_type (Data.DateType): 集計する日付のタイプ。時間、日、月、年のいずれか。

        Returns:
            list: 集計されたデータリスト。各要素は日時オブジェクトと数値データの合計を含むリスト。
        """
        aggregated_data = defaultdict(lambda: [0] * (len(line_list[0]) - 1))
        
        for row in line_list:
            time = row[0]
            if date_type == Data.DateType.HOUR: # 時間単位で集計＝30分単位なので注意
                if time.minute < 30:
                    rounded_time = time.replace(minute=0, second=0, microsecond=0)
                else:
                    rounded_time = time.replace(minute=30, second=0, microsecond=0)
            elif date_type == Data.DateType.DATE:
                rounded_time = time.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_type == Data.DateType.MONTH:
                rounded_time = time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif date_type == Data.DateType.YEAR:
                rounded_time = time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                raise ValueError("Unsupported date_type")
            
            for i, value in enumerate(row[1:], start=1):
                aggregated_data[rounded_time][i-1] += value
        
        aggregated_list = [[time] + values for time, values in sorted(aggregated_data.items())]
        
        return aggregated_list

    def save_aggregated_data(self, aggregated_data, company, device_no_to_entity_dict, data_type, date_type):
        """
        指定時間単位のデータをデータベースに保存する。

        この関数は、指定時間単位で集計されたデータリストを受け取り、それらをデータベースに保存する。
        既存のデータがある場合はそのデータを更新し、ない場合は新しいデータとして追加する。
        この処理はトランザクション内で行われ、全てのデータの保存または更新が成功した場合のみ完了する。

        Args:
            aggregated_data (list): 指定時間単位のデータリスト。各要素は日時オブジェクトと数値データを含むリスト。
            company (Company): データに関連する会社のオブジェクト。
            device_no_to_entity_dict (dict): デバイス番号とエンティティオブジェクトのマッピング辞書。
            data_type (int): データの種類を示す整数値。ex) DATA_TYPE_ELECTRICITY
        """
        # 指定時間単位のデータをDB登録
        # aggregated_dataは時間の昇順にソートされている
        start_time = aggregated_data[0][0]  # 先頭のデータの時間
        end_time = aggregated_data[-1][0]   # 末尾のデータの時間

        # entity一覧を作成
        target_entities = device_no_to_entity_dict.values()

        # 指定された時間範囲内の既存データを取得
        existing_data_qs = Data.objects.filter(
            get_data_at__range=(start_time, end_time),
            data_type=data_type,
            date_type=date_type,
            entity_id__in=target_entities
        )
        existing_data_map = {(data.get_data_at, data.entity_id): data for data in existing_data_qs}

        # 更新または新規作成するデータオブジェクトのリスト
        update_list = []
        create_list = []

        for row in aggregated_data:
            get_data_at = row[0]
            for no, device_data in enumerate(row[1:], start=1):
                entity = device_no_to_entity_dict[no]
                key = (get_data_at, entity.id)

                if key in existing_data_map:
                    # 既存データの更新
                    existing_data = existing_data_map[key]
                    existing_data.value = device_data
                    update_list.append(existing_data)
                else:
                    # 新規データの作成
                    new_data = Data(
                                get_data_at=get_data_at, 
                                data_type=data_type, 
                                date_type=date_type, 
                                value=device_data, 
                                entity=entity
                            )
                    create_list.append(new_data)

        # バルクで更新または作成
        Data.objects.bulk_update(update_list, ['value'], batch_size=100)
        Data.objects.bulk_create(create_list, batch_size=100)


class CarbonFootprintViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarbonFootprintSerializer

    lookup_field = 'id'

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        return CarbonFootprint.objects.filter(company_id__id=company_id)
    
    def create(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()        
        company = Company.objects.get(id=company_id)

        carbon_footprint = CarbonFootprint.objects.create(
            company_id=company,
            process_name = request.data.get('process_name', '工程'),
            channel_name = request.data.get('channel_name', 'チャンネル'),
            start_date = request.data.get('start_date', None),
            end_date = request.data.get('end_date', None),
            electric_value = request.data.get('electric_value', 0.0),
            co2_emissions = request.data.get('co2_emissions', 0.0),
            scope_no = request.data.get('scope_no', 1)
            )
        serializer = self.get_serializer(carbon_footprint)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()        
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class CarbonFootprintKgViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarbonFootprintKgSerializer

    lookup_field = 'id'

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        return CarbonFootprint.objects.filter(company_id__id=company_id)
    
    def create(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()        
        company = Company.objects.get(id=company_id)

        carbon_footprint = CarbonFootprint.objects.create(
            company_id=company,
            process_name = request.data.get('process_name', '工程'),
            channel_name = request.data.get('channel_name', 'チャンネル'),
            start_date = request.data.get('start_date', None),
            end_date = request.data.get('end_date', None),
            electric_value = request.data.get('electric_value', 0.0),
            co2_emissions = float(request.data.get('co2_emissions', 0.0)) * 0.001,  # kg-CO2e to t-CO2e for internal storage
            scope_no = request.data.get('scope_no', 2)      # 2 = 電気
            )
        serializer = self.get_serializer(carbon_footprint)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CarbonFootprintChannelViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarbonFootprintChannelSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        return CarbonFootprint.objects.filter(company_id_id=company_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        results_dict = {}
        for carbon_footprint in queryset:
            name = carbon_footprint.channel_name
            value = carbon_footprint.co2_emissions
            results_dict[name] = value + results_dict.get(name, 0.0)
        results = [{"name": k, "value": v} for k, v in results_dict.items()]
        return Response(results)


class CarbonFootprintScopeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CarbonFootprintScopeSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        return CarbonFootprint.objects.filter(company_id_id=company_id)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        results_dict = {}
        ghg_value = 0.0
        for carbon_footprint in queryset:
            scope = carbon_footprint.scope_no
            value = carbon_footprint.co2_emissions
            results_dict[scope] = value + results_dict.get(scope, 0.0)
            ghg_value += value
        results = {"ghg_emmision": ghg_value, "scope1": results_dict.get(1, 0.0), "scope2": results_dict.get(2, 0.0), "scope3": results_dict.get(3, 0.0)}
        return Response(results)

# 常時データ表示領域（右の年月日指定に依存しない）：電力量、予測値
class ValuesActualPredictionTarget():
    '''
    実績値、目標値、予測値を計算
    '''
    def __init__(self):
        pass

    # 月の実績値：電力量
    def monthly_actual_electrical_value(self, entity_id, startdate):
        value, _ = self.monthly_actual_electrical(entity_id, startdate)
        return value

    # 月の目標値：電力量
    def monthly_target_electrical_value(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.electric / 12 if not yearly_target_values is None else 0

    # 月の目標値：光熱費
    def monthly_target_electrical_price(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.utility_cost / 12 if not yearly_target_values is None else 0

    # 月の目標値：CO2排出量
    def monthly_target_co2emissions_value(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.co2_emissions / 12 if not yearly_target_values is None else 0

    # 月の目標値：カーボンクレジット   
    def monthly_target_carbon_credit(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.carbon_credit / 12 if not yearly_target_values is None else 0

    # 月の目標値：電力削減量
    def monthly_target_electrical_reduce(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.electric_reduce / 12 if not yearly_target_values is None else 0

    # 月の目標値：光熱削減費
    def monthly_target_utility_cost_reduce(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.utility_cost_reduce / 12 if not yearly_target_values is None else 0

    # 月の目標値：CO2削減量
    def monthly_target_co2emissions_reduce(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.co2_emissions_reduce / 12 if not yearly_target_values is None else 0

    # 年の目標値：電力量
    def yearly_target_electrical_value(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.electric if not yearly_target_values is None else 0

    # 年の目標値：光熱費
    def yearly_target_electrical_price(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.utility_cost if not yearly_target_values is None else 0

    # 年の目標値：CO2排出量
    def yearly_target_co2emissions_value(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.co2_emissions if not yearly_target_values is None else 0

    # 年の目標値：カーボンクレジット   
    def yearly_target_carbon_credit(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.carbon_credit if not yearly_target_values is None else 0

    # 年の目標値：電力削減量
    def yearly_target_electrical_reduce(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.electric_reduce if not yearly_target_values is None else 0

    # 年の目標値：光熱削減費
    def yearly_target_utility_cost_reduce(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.utility_cost_reduce if not yearly_target_values is None else 0

    # 年の目標値：CO2削減量
    def yearly_target_co2emissions_reduce(self, company_id):
        yearly_target_values = self.yearly_target(company_id)
        return yearly_target_values.co2_emissions_reduce if not yearly_target_values is None else 0

    # 月の予測値：電力量
    def monthly_prediction_electrical_value(self, entity_id, startdate):
        return self.monthly_prediction_electrical(entity_id, startdate)[0]

    # 年の予測値：電力量
    def yearly_prediction_electrical_value(self, entity_id, startdate):
        return self.yearly_prediction_electrical(entity_id, startdate)[0]


    def monthly_actual_electrical(self, entity_id, startdate):
        '''
        月の電力量の実績値を計算
        '''
        # 本日の始まり時刻、昨日の最終時刻、月の始まり日
        now = timezone.now()
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_yesterday = start_of_today - relativedelta(seconds=1)
        start_of_month = datetime.datetime(now.year, now.month, 1).date()

        # 既存データ：1日00:00:00〜昨日23:59:59までのデータ
        target_month_df = self.get_df(start_of_month, end_of_yesterday, entity_id, startdate, Data.DateType.DATE)

        # 実績値を計算
        actual_electrical = self.calc_cost_actual(target_month_df, DATA_TYPE_ELECTRICITY)
        return actual_electrical

    def yearly_target(self, company_id):
        '''
        年の目標値を取得
        '''
        # 月の目標値は、年の目標値を12で割る
        now = timezone.now()
        year = now.year

        try:
            anual_plan_values = AnnualPlanValues.objects.get(company_id=company_id)
        except AnnualPlanValues.DoesNotExist:
            anual_plan_values = None
             
        return anual_plan_values

    def monthly_prediction_electrical(self, entity_id, startdate):
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
        target_window_df = self.get_df(start_of_today - datetime.timedelta(days=WINDOW_SIZE), end_of_yesterday, entity_id, startdate, Data.DateType.DATE)

        # 予測月の既存データ：1日00:00:00〜昨日23:59:59までのデータ
        target_month_df = self.get_df(startday_of_month, end_of_yesterday, entity_id, startdate, Data.DateType.DATE)

        # 予測値を計算
        predicted_electrical = self.calc_cost_prediction(target_window_df, target_month_df, remaining_days, DATA_TYPE_ELECTRICITY)
        return predicted_electrical

    def yearly_prediction_electrical(self, entity_id, startdate):
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
        target_window_df = self.get_df(start_of_thismonth - relativedelta(months=WINDOW_SIZE), end_of_lastmonth, entity_id, startdate, Data.DateType.MONTH)

        # 予測年の既存データ：1月1日〜先月までのデータ
        target_year_df = self.get_df(start_of_thisyear, end_of_lastmonth, entity_id, startdate, Data.DateType.MONTH) 

        # 予測値を計算
        predicted_electrical = self.calc_cost_prediction(target_window_df, target_year_df, remaining_months, DATA_TYPE_ELECTRICITY)
        return predicted_electrical

    def calc_cost_prediction(self, target_window_df, target_period_df, remaining_count, type_name):
        '''
        各種の予測値を計算
        @param target_window_df: 予測の元データ（14日分/三ヶ月分）
        @param target_period_df: 予測期間の既存データ
        @param remaining_count: 今日から月末までの残り日数（今日を含む）／今月から年末までの残り月数（今月を含む）
        @param type_name: データタイプ名 := DATA_TYPE_ELECTRICITY|DATA_TYPE_CO2
        @return: 予測値
        '''
        if (len(target_window_df) == 0):
            return (0.0, 0.0)

        type_id = DataType.objects.get(name=type_name).id

        # 予測の元データの平均値を計算
        data_window_df = target_window_df[target_window_df['data_type_id'] == type_id]
        avg_value, avg_price = self.calc_avg(data_window_df)

        # 対象期間の既存データの合計値を計算
        if (len(target_period_df) == 0):
            target_value, target_price = (0.0, 0.0)
        else:
            data_period_df = target_period_df[target_period_df['data_type_id'] == type_id]
            target_value, target_price = self.calc_sum(data_period_df)

        # 今月の光熱費の予測値を計算
        value_prediction = target_value + avg_value * remaining_count
        price_prediction = target_price + avg_price * remaining_count
        return (value_prediction, price_prediction)

    def calc_cost_actual(self, target_period_df, type_name):
        '''
        実績値を計算
        @param target_period_df: 予測対象期間の既存データ
        @param type_name: データタイプ名 := DATA_TYPE_ELECTRICITY|DATA_TYPE_CO2
        @return: 実績値
        '''
        if (len(target_period_df) == 0):
            return (0.0, 0.0)

        type_id = DataType.objects.get(name=type_name).id

        # 対象月の既存データの合計値を計算
        data_month_df = target_period_df[target_period_df['data_type_id'] == type_id]
        target_value, target_price = self.calc_sum(data_month_df)

        return (target_value, target_price)

    def get_df(self, start, end, entity_id, startdate, date_type):
        data = Data.objects.filter(get_data_at__range=[start, end], entity_id=entity_id, date_type=date_type).order_by('get_data_at')

        if startdate is not None:
            data = Data.objects.filter(get_data_at__range=[start, end], entity_id=entity_id, date_type=date_type, get_data_at__date__gte=startdate).order_by('get_data_at')
        else:
            data = Data.objects.filter(get_data_at__range=[start, end], entity_id=entity_id, date_type=date_type).order_by('get_data_at')

        df = pd.DataFrame.from_records(data.values())
        return df

    def calc_sum(self, data_df):
        if len(data_df) > 0:
            sum_value = data_df["value"].fillna(0).sum()
            sum_price = data_df["price"].fillna(0).sum()
            return (sum_value, sum_price)
        else:
            return (0.0, 0.0)

    def calc_avg(self, data_df):
        if len(data_df) > 0:
            avg_value = data_df["value"].fillna(0).sum() / len(data_df)
            avg_price = data_df["price"].fillna(0).sum() / len(data_df)
            return (avg_value, avg_price)
        else:
            return (0.0, 0.0)

    def get_graph_setting(self, graph_adapter:ChannelAdapter):
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
            if graph_adapter.co2_emissions_baseline >= 0.0:
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

    # 円/t-CO₂
    def get_carbon_credit_price(self, company_id):
        annual_plan_values = AnnualPlanValues.objects.filter(company_id__id=company_id).first()
        if annual_plan_values is None:
            return 0.0
        return annual_plan_values.carbon_credit_price

    # Channel番号の取得：エラーなら０を返す
    def int_range16(self, value):
        try:
            val = int(value)
            return val if 1 <= val <= 16 else 0
        except:
            return 0

    # comma区切りの数字列からChannel番号を切り出してリストにして返す
    def get_channel_no_list(self, channel_numbers):
        if channel_numbers is not None:
            channel_numbers = [num for num in set(self.int_range16(c) for c in channel_numbers.split(',')) if num != 0]

        if channel_numbers is None or len(channel_numbers) == 0:
            channel_numbers = [i for i in range(1, 17)]
        return channel_numbers


# 実績値：電力量
class ValuesElectricalViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # ch query parameter
        channel_numbers = self.get_channel_no_list(request.query_params.get('ch', None))

        # graph情報の取得：指定番号のみを対象とする
        actual_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の実績値：電力量 kWh
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            value = self.monthly_actual_electrical_value(entity_id, startdate)

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            actual_value += float(equation.subs(expr, value))

        # 月間目標値：電力量
        target_value = self.monthly_target_electrical_value(company_id)

        # 目標値に対する実績値の割合
        rate_value = actual_value / target_value if target_value != 0 else 0

        data = {
            'actual_value': actual_value,
            'target_value': target_value,
            'rate_value': rate_value
            }
        return Response(data)
    
# 実績値：光熱費
class ValuesUtilityCostsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # ch query parameter
        channel_numbers = self.get_channel_no_list(request.query_params.get('ch', None))

        # graph情報の取得：指定番号のみを対象とする
        actual_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の実績値：電力量 kWh
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            value = self.monthly_actual_electrical_value(entity_id, startdate)

            # graphごとの円/kWh
            electric_price = graph_setting['electric_price']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            actual_value += float(equation.subs(expr, value)) * float(electric_price)

        # 月間目標値：光熱費
        target_value = self.monthly_target_electrical_price(company_id)

        # 目標値に対する実績値の割合
        rate_value = actual_value / target_value if target_value != 0 else 0

        data = {
            'actual_value': actual_value,
            'target_value': target_value,
            'rate_value': rate_value
            }
        return Response(data)

# 実績値：CO2排出量

class ValuesCO2EmissionsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # ch query parameter
        channel_numbers = self.get_channel_no_list(request.query_params.get('ch', None))

        # graph情報の取得：指定番号のみを対象とする
        actual_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の実績値：電力量 kWh
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            value = self.monthly_actual_electrical_value(entity_id, startdate)

            # graphごとのt-CO₂/kWh
            co2_coefficient = graph_setting['co2_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            actual_value += float(equation.subs(expr, value)) * float(co2_coefficient)

        # 月間目標値：CO2排出量
        target_value = self.monthly_target_co2emissions_value(company_id)

        # 目標値に対する実績値の割合
        rate_value = actual_value / target_value if target_value != 0 else 0

        data = {
            'actual_value': actual_value,
            'target_value': target_value,
            'rate_value': rate_value
            }
        return Response(data)
    
# 実績値：カーボンクレジット量
class ValuesCarbonCreditViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # ch query parameter
        channel_numbers = self.get_channel_no_list(request.query_params.get('ch', None))

        # graph情報の取得：指定番号のみを対象とする
        actual_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の実績値：電力量 kWh
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            value = self.monthly_actual_electrical_value(entity_id, startdate)

            # graphごとのt-CO₂/kWh
            co2_coefficient = graph_setting['co2_coefficient']

            # 円/t-CO₂
            carbon_credit_price = self.get_carbon_credit_price(company_id)

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            actual_value += float(equation.subs(expr, value)) * float(co2_coefficient) * float(carbon_credit_price) * float(reduction_coefficient)

        # 月間目標値：カーボンクレジット
        target_value = self.monthly_target_carbon_credit(company_id)

        # 目標値に対する実績値の割合
        rate_value = actual_value / target_value if target_value != 0 else 0

        data = {
            'actual_value': actual_value,
            'target_value': target_value,
            'rate_value': rate_value
            }
        return Response(data)

# 実績値：電力削減量
class ReductionElectricalViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # ch query parameter
        channel_numbers = self.get_channel_no_list(request.query_params.get('ch', None))

        # graph情報の取得：指定番号のみを対象とする
        actual_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の実績値：電力量 kWh
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            value = self.monthly_actual_electrical_value(entity_id, startdate)

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            actual_value += float(equation.subs(expr, value)) * float(reduction_coefficient)

        # 月間目標値：電力削減量
        target_value = self.monthly_target_electrical_reduce(company_id)

        # 目標値に対する実績値の割合
        rate_value = actual_value / target_value if target_value != 0 else 0

        data = {
            'actual_value': actual_value,
            'target_value': target_value,
            'rate_value': rate_value
            }
        return Response(data)

# 実績値：光熱削減費
class ReductionUtilityCostsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # ch query parameter
        channel_numbers = self.get_channel_no_list(request.query_params.get('ch', None))

        # graph情報の取得：指定番号のみを対象とする
        actual_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の実績値：電力量 kWh
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            value = self.monthly_actual_electrical_value(entity_id, startdate)

            # graphごとの円/kWh
            electric_price = graph_setting['electric_price']

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            actual_value += float(equation.subs(expr, value)) * float(electric_price) * float(reduction_coefficient)

        # 月間目標値：光熱削減費
        target_value = self.monthly_target_utility_cost_reduce(company_id)

        # 目標値に対する実績値の割合
        rate_value = actual_value / target_value if target_value != 0 else 0

        data = {
            'actual_value': actual_value,
            'target_value': target_value,
            'rate_value': rate_value
            }
        return Response(data)

# 実績値：CO2削減量
class ReductionCO2EmissionsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # ch query parameter
        channel_numbers = self.get_channel_no_list(request.query_params.get('ch', None))

        # graph情報の取得：指定番号のみを対象とする
        actual_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id, channel_no__in=channel_numbers):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の実績値：電力量 kWh
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            value = self.monthly_actual_electrical_value(entity_id, startdate)

            # graphごとのt-CO₂/kWh
            co2_coefficient = graph_setting['co2_coefficient']

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            actual_value += float(equation.subs(expr, value)) * float(co2_coefficient) * float(reduction_coefficient)

        # 月間目標値：CO2削減量
        target_value = self.monthly_target_co2emissions_reduce(company_id)

        # 目標値に対する実績値の割合
        rate_value = actual_value / target_value if target_value != 0 else 0

        data = {
            'actual_value': actual_value,
            'target_value': target_value,
            'rate_value': rate_value
            }
        return Response(data)


# year, monthを指定→その月の予測値を計算
# 予測値：電力量
class PredictionElectricalViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # graph情報の取得
        monthly_prediction_value = 0.0
        yearly_prediction_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の予測値/年間予測値：電力量
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            monthly_value = self.monthly_prediction_electrical_value(entity_id, startdate)
            yearly_value = self.yearly_prediction_electrical_value(entity_id, startdate)

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            monthly_prediction_value += float(equation.subs(expr, monthly_value))
            yearly_prediction_value += float(equation.subs(expr, yearly_value))

        # 年間目標値：電力量
        yearly_target_value = self.yearly_target_electrical_value(company_id)

        # 改善率＝目標値に対する予測値の割合
        yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_value if yearly_target_value != 0 else 0)

        data = {
            'monthly_prediction_value': monthly_prediction_value,
            'yearly_prediction_value': yearly_prediction_value,
            'yearly_target_value': yearly_target_value,
            'yearly_improvement_rate': yearly_improvement_rate
            }
        return Response(data)

# 予測値：光熱費
class PredictionUtilityCostsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # graph情報の取得
        monthly_prediction_value = 0.0
        yearly_prediction_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の予測値/年間予測値：電力量
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            monthly_value = self.monthly_prediction_electrical_value(entity_id, startdate)
            yearly_value = self.yearly_prediction_electrical_value(entity_id, startdate)

            # graphごとの円/kWh
            electric_price = graph_setting['electric_price']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(electric_price)
            yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(electric_price)

        # 年間目標値：光熱費
        yearly_target_value = self.yearly_target_electrical_price(company_id)

        # 改善率＝目標値に対する予測値の割合
        yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_value if yearly_target_value != 0 else 0)

        data = {
            'monthly_prediction_value': monthly_prediction_value,
            'yearly_prediction_value': yearly_prediction_value,
            'yearly_target_value': yearly_target_value,
            'yearly_improvement_rate': yearly_improvement_rate
            }
        return Response(data)

# 予測値：CO2排出量
class PredictionCO2EmissionsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # graph情報の取得
        monthly_prediction_value = 0.0
        yearly_prediction_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の予測値/年間予測値：電力量
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            monthly_value = self.monthly_prediction_electrical_value(entity_id, startdate)
            yearly_value = self.yearly_prediction_electrical_value(entity_id, startdate)

            # graphごとのt-CO₂/kWh
            co2_coefficient = graph_setting['co2_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(co2_coefficient)
            yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(co2_coefficient)

        # 年間目標値：CO2排出量
        yearly_target_value = self.yearly_target_co2emissions_value(company_id)

        # 改善率＝目標値に対する予測値の割合
        yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_value if yearly_target_value != 0 else 0)

        data = {
            'monthly_prediction_value': monthly_prediction_value,
            'yearly_prediction_value': yearly_prediction_value,
            'yearly_target_value': yearly_target_value,
            'yearly_improvement_rate': yearly_improvement_rate
            }
        return Response(data)

# 予測値：カーボンクレジット量
class PredictionCarbonCreditViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            root_entity = Company.objects.get(id=company_id).root_entity
            root_entity_id = root_entity.id if root_entity is not None else None
        else:
            raise Http404
        
        # graph情報の取得
        monthly_prediction_value = 0.0
        yearly_prediction_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の予測値/年間予測値：電力量
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            monthly_value = self.monthly_prediction_electrical_value(entity_id, startdate)
            yearly_value = self.yearly_prediction_electrical_value(entity_id, startdate)

            # graphごとのt-CO₂/kWh
            co2_coefficient = graph_setting['co2_coefficient']

            # 円/t-CO₂
            carbon_credit_price = self.get_carbon_credit_price(company_id)

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(co2_coefficient) * float(carbon_credit_price) * float(reduction_coefficient)
            yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(co2_coefficient) * float(carbon_credit_price) * float(reduction_coefficient)

        # 年間目標値：カーボンクレジット量
        yearly_target_value = self.yearly_target_carbon_credit(company_id)

        # 改善率＝目標値に対する予測値の割合
        yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_value if yearly_target_value != 0 else 0)

        data = {
            'monthly_prediction_value': monthly_prediction_value,
            'yearly_prediction_value': yearly_prediction_value,
            'yearly_target_value': yearly_target_value,
            'yearly_improvement_rate': yearly_improvement_rate
            }
        return Response(data)

# 予測値：電力削減量
class PredictionReductionElectricalViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # graph情報の取得
        monthly_prediction_value = 0.0
        yearly_prediction_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の予測値/年間予測値：電力量
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            monthly_value = self.monthly_prediction_electrical_value(entity_id, startdate)
            yearly_value = self.yearly_prediction_electrical_value(entity_id, startdate)

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(reduction_coefficient)
            yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(reduction_coefficient)

        # 年間目標値：電力削減量
        yearly_target_value = self.yearly_target_electrical_reduce(company_id)

        # 改善率＝目標値に対する予測値の割合
        yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_value if yearly_target_value != 0 else 0)

        data = {
            'monthly_prediction_value': monthly_prediction_value,
            'yearly_prediction_value': yearly_prediction_value,
            'yearly_target_value': yearly_target_value,
            'yearly_improvement_rate': yearly_improvement_rate
            }
        return Response(data)

# 予測値：光熱削減費
class PredictionReductionUtilityCostsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
            root_entity = Company.objects.get(id=company_id).root_entity
            root_entity_id = root_entity.id if root_entity is not None else None
        else:
            raise Http404

        # graph情報の取得
        monthly_prediction_value = 0.0
        yearly_prediction_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの円/kWh
            electric_price = graph_setting['electric_price']

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # graphごとの月の予測値/年間予測値：電力量
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            monthly_value = self.monthly_prediction_electrical_value(entity_id, startdate)
            yearly_value = self.yearly_prediction_electrical_value(entity_id, startdate)

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(electric_price) * float(reduction_coefficient)
            yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(electric_price) * float(reduction_coefficient)

        # 年間目標値：光熱削減費
        yearly_target_price = self.yearly_target_utility_cost_reduce(company_id)

        # 改善率＝目標値に対する予測値の割合
        yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_price if yearly_target_price != 0 else 0)

        data = {
            'monthly_prediction_value': monthly_prediction_value,
            'yearly_prediction_value': yearly_prediction_value,
            'yearly_target_price': yearly_target_price,
            'yearly_improvement_rate': yearly_improvement_rate
            }
        return Response(data)

# 予測値：CO2削減量
class PredictionReductionCO2EmissionsViewSet(ValuesActualPredictionTarget, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.kwargs['company_id']
        if company_id is not None:
            if not CompanyUser.objects.filter(user_id=self.request.user.id, company_id=company_id).exists():
                raise PermissionDenied()
        else:
            raise Http404

        # graph情報の取得
        monthly_prediction_value = 0.0
        yearly_prediction_value = 0.0
        for graph_adapter in ChannelAdapter.objects.filter(company_id_id=company_id):
            # graphごとの設定値
            graph_setting = self.get_graph_setting(graph_adapter)
            if graph_setting is None:
                continue

            # graphごとの月の予測値/年間予測値：電力量
            entity_id = graph_setting['entity_id']
            startdate = graph_setting['startdate']
            monthly_value = self.monthly_prediction_electrical_value(entity_id, startdate)
            yearly_value = self.yearly_prediction_electrical_value(entity_id, startdate)

            # graphごとのt-CO₂/kWh
            co2_coefficient = graph_setting['co2_coefficient']

            # 削減量係数
            reduction_coefficient = graph_setting['reduction_coefficient']

            # 計算式に基づく結果を加算：グラフごとに計算式は異なっている
            equation_str = graph_setting['equation_str']
            equation = parse_expr(equation_str)
            expr = symbols('x')
            monthly_prediction_value += float(equation.subs(expr, monthly_value)) * float(co2_coefficient) * float(reduction_coefficient)
            yearly_prediction_value += float(equation.subs(expr, yearly_value)) * float(co2_coefficient) * float(reduction_coefficient)

        # 年間目標値：CO2排出削減量
        yearly_target_value = self.yearly_target_co2emissions_reduce(company_id)

        # 改善率＝目標値に対する予測値の割合
        yearly_improvement_rate = 1.0 - (yearly_prediction_value / yearly_target_value if yearly_target_value != 0 else 0)

        data = {
            'monthly_prediction_value': monthly_prediction_value,
            'yearly_prediction_value': yearly_prediction_value,
            'yearly_target_value': yearly_target_value,
            'yearly_improvement_rate': yearly_improvement_rate
            }
        return Response(data)


class Co2EmissionsFactorsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        co2_emissions_factors = Co2EmissionsFactor.objects.all()
        result = [{"name": factor.name, "no":factor.no, "factor":factor.factor, "region_name": factor.region_name} for factor in co2_emissions_factors]
        result = sorted(result, key=lambda x: x["no"])
        return Response(result)

class CsvUploadHistoryListView(generics.ListAPIView):
    serializer_class = CsvUploadHistorySerializer

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return CsvUploadHistory.objects.filter(company_id=company_id)

def fetch_and_save_data(target_device, pushlog_api_call, params, from_datetime, to_datetime):
    response_data = pushlog_api_call.historical(gateway_id=target_device.gateway_id.id, params=params)
    if response_data == None:
        logging.error("対象期間のデータ取得に失敗しました")
        return

    for trigger_data in response_data:
        for data_source_nm, historical_values in trigger_data['data'].items():
            if data_source_nm != target_device.data_source_name:
                continue
            # from_datetimeからto_datetimeまでをインターバルの区切りでループする
            current_target_time = from_datetime
            while current_target_time < to_datetime:
                target_time_0 = current_target_time + datetime.timedelta(minutes=INTERVAL_MINUTES)
                target_time_1 = current_target_time
                if target_device.is_instantaneous:
                    create_instantaneous_timeseries_data(target_device, historical_values, target_time_0, target_time_1, target_time_1, target_time_1)
                else:
                    create_cumulative_timeseries_data(target_device, historical_values, target_time_0, target_time_1, target_time_1, target_time_1)
                current_target_time += datetime.timedelta(minutes=INTERVAL_MINUTES)

def fetch_pushlog_data(request, device_id):
    if request.method == 'POST':
        form = FetchDataForm(request.POST)
        if form.is_valid():
            # 対象期間をそれぞれ取得インターバルの区切りになるように切り下げ、切り上げを行う
            from_datetime = round_time_to_prev_min(form.cleaned_data['start_datetime'], INTERVAL_MINUTES)
            to_datetime = round_time_to_next_min(form.cleaned_data['end_datetime'], INTERVAL_MINUTES)

            # 取得用の時間の設定
            fetch_from_datetime = from_datetime - datetime.timedelta(minutes=BUFFER_MINUTES) # 補完用にBUFFER_MINUTES分余分に取得する
            fetch_to_datetime = to_datetime + datetime.timedelta(minutes=1)
            fetch_from_unixtime = get_unix_time(fetch_from_datetime)
            fetch_to_unixtime = get_unix_time(fetch_to_datetime)
            params = {
                'from' : fetch_from_unixtime,
                'to' : fetch_to_unixtime,
            }

            target_device = Device.objects.get(id=device_id)
            if target_device.enable_data_collection == False:
                messages.error(request, "デバイスのデータ収集が無効になっています")
                return render(request, 'fetch_pushlog_data_done.html')
            if target_device.pushlog_api == None:
                messages.error(request, "デバイスにPushログAPIが設定されていません")
                return render(request, 'fetch_pushlog_data_done.html')

            pushlog_api_call = PushlogApiCall(pushlog_api=target_device.pushlog_api)
            if target_device.gateway_id == None:
                messages.error(request, "デバイスにゲートウェイが設定されていません")
                return render(request, 'fetch_pushlog_data_done.html')

            thread_fetch = threading.Thread(target=fetch_and_save_data, args=(target_device, pushlog_api_call, params, from_datetime, to_datetime))
            thread_fetch.start()

            return render(request, 'fetch_pushlog_data_done.html')
    else:
        form = FetchDataForm()
    return render(request, 'fetch_pushlog_data.html', {'form': form})
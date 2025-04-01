import csv
import datetime
import io

from collections import defaultdict
from itertools import groupby
from operator import itemgetter
# Create your views here.
from django.db import models, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema, extend_schema_view)
from rest_framework import (filters, generics, mixins, permissions, status,
                            views, viewsets)
from rest_framework.exceptions import NotFound, APIException, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVRenderer
from users.models import CompanyUser

from ..constants import DATA_TYPE_ELECTRICITY
from ..function_calls import PushlogApiCall
from ..function_create_csv_response import create_minutely_channel_csv_response, create_hourly_channel_csv_response, create_daily_channel_csv_response
from ..models import (AnnualPlanValues, CarbonFootprint,
                     ChannelAdapter, Co2EmissionsFactor, Company, 
                     DailyEconomicActivityAmount,
                     Data, DataStructure, DataType, Device, 
                     EconomicActivityType,
                     EconomicActivityUnit, Entity, Gateway,
                     GatewayMaster, GatewayRegistration, GatewayStartdate,
                     RegisteredLimit,
                     CsvUploadHistory)
from .serializer import (
                         AnnualPlanValuesSerializer,
                         CarbonFootprintSerializer, 
                         CarbonFootprintKgSerializer,
                         CarbonFootprintChannelSerializer,
                         CarbonFootprintScopeSerializer,
                         ChannelAdapterGatewaySerializer,
                         ChannelAdapterSerializer,
                         DailyEconomicActivityAmountSerializer,
                         EconomicActivityTypeSerializer,
                         EconomicActivityUnitSerializer,
                         GatewayRegistrationSerializer,
                         GatewayStartdateSerializer,
                         GraphDataSerializer,
                         RegisteredGatewayCountSerializer,
                         RegisteredUserCountSerializer,
                         CsvUploadHistorySerializer)
from datetime import timedelta


from .trendgraph_services import ( get_graph_data_seq_minutes, get_graph_data_seq_hours, get_graph_data_seq_days,
                                  get_graph_data_latest_minutes, get_graph_data_latest_hours, get_graph_data_latest_days,
                                  get_graph_data_ranking_minutes, get_graph_data_ranking_hours, get_graph_data_ranking_days
                                  )
from .actual_prediction_services import get_actual_values, get_predicted_values
from .permission_services import is_user_manager, is_user_viewer, is_user_normal, permitted_entity
from .utils import get_channel_no_list
import logging

# トレンドグラフ画面
# 時系列データの取得
class GraphDataSeqViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = GraphDataSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        hour = self.request.query_params.get('hour', None)
        minute = self.request.query_params.get('minute', 0)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        week = self.request.query_params.get('week', None)      # weekは月の中での週番号（月曜始まり、0〜）
        mode = self.request.query_params.get('mode', None)
        company_id = self.request.query_params.get('company_id', None)
        user_id = self.request.user.id

        range_type = self.request.query_params.get('range_type', None)
        data_type = self.request.query_params.get('data_type', None)

        # エンティティに許可があるかチェック
        if not permitted_entity(company_id, user_id):
            raise PermissionDenied()

        # company_idのチェック
        if company_id is not None:
            # ユーザーが所属している企業か確認
            if not is_user_normal(company_id, user_id):
                raise PermissionDenied()
        else:
            # 無指定なら、ユーザの所属企業を取得
            company_id = self.request.user.company_id_id

        if range_type == 'minutes':
            # 日付が指定されていない場合はエラー
            if year is None or month is None or date is None or hour is None or minute is None:
                raise ValidationError('year, month, date, hour and minute must be specified')
            return get_graph_data_seq_minutes(company_id, data_type, mode, year, month, date, hour, minute)
        elif range_type == 'hours':
            return get_graph_data_seq_hours(company_id, data_type, mode, year, month, date, start, end)
        elif range_type == 'days':
            return get_graph_data_seq_days(company_id, data_type, mode, year, month, start, end, week)
        else:
            raise ValidationError('range_type must be minutes, hours or days')


# 最新データ一覧の取得
class GraphDataLatestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = GraphDataSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        hour = self.request.query_params.get('hour', None)
        minute = self.request.query_params.get('minute', 0)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        week = self.request.query_params.get('week', None)      # weekは月の中での週番号（月曜始まり、0〜）
        mode = self.request.query_params.get('mode', None)
        company_id = self.request.query_params.get('company_id', None)
        user_id = self.request.user.id

        range_type = self.request.query_params.get('range_type', None)
        data_type = self.request.query_params.get('data_type', None)

        # エンティティに許可があるかチェック
        if not permitted_entity(company_id, user_id):
            raise PermissionDenied()

        # company_idのチェック
        if company_id is not None:
            # ユーザーが所属している企業か確認
            if not is_user_normal(company_id, user_id):
                raise PermissionDenied()
        else:
            # 無指定なら、ユーザの所属企業を取得
            company_id = self.request.user.company_id_id

        if range_type == 'minutes':
            # 日付が指定されていない場合はエラー
            if year is None or month is None or date is None or hour is None or minute is None:
                raise ValidationError('year, month, date, hour and minute must be specified')
            return get_graph_data_latest_minutes(company_id, data_type, mode, year, month, date, hour, minute)
        elif range_type == 'hours':
            return get_graph_data_latest_hours(company_id, data_type, mode, year, month, date, start, end)
        elif range_type == 'days':
            return get_graph_data_latest_days(company_id, data_type, mode, year, month, start, end, week)
        else:
            raise ValidationError('range_type must be minutes, hours or days')


# データランキングの取得
# 指定範囲内の各グラフの合計値のランキング：デフォルトは、上位3件＋その他
class GraphDataRankingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = GraphDataSerializer

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        date = self.request.query_params.get('date', None)
        hour = self.request.query_params.get('hour', None)
        minute = self.request.query_params.get('minute', 0)
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        week = self.request.query_params.get('week', None)      # weekは月の中での週番号（月曜始まり、0〜）
        mode = self.request.query_params.get('mode', None)
        top = self.request.query_params.get('top', None)
        company_id = self.request.query_params.get('company_id', None)
        user_id = self.request.user.id

        range_type = self.request.query_params.get('range_type', None)
        data_type = self.request.query_params.get('data_type', None)

        # エンティティに許可があるかチェック
        if not permitted_entity(company_id, user_id):
            raise PermissionDenied()

        # company_idのチェック
        if company_id is not None:
            # ユーザーが所属している企業か確認
            if not is_user_normal(company_id, user_id):
                raise PermissionDenied()
        else:
            # 無指定なら、ユーザの所属企業を取得
            company_id = self.request.user.company_id_id

        if range_type == 'minutes':
            # 日付が指定されていない場合はエラー
            if year is None or month is None or date is None or hour is None or minute is None:
                raise ValidationError('year, month, date, hour and minute must be specified')
            return get_graph_data_ranking_minutes(company_id, data_type, mode, top, year, month, date, hour, minute)
        elif range_type == 'hours':
            return get_graph_data_ranking_hours(company_id, data_type, mode, top, year, month, date, start, end)
        elif range_type == 'days':
            return get_graph_data_ranking_days(company_id, data_type, mode, top, year, month, start, end, week)
        else:
            raise ValidationError('range_type must be minutes, hours or days')



# 実績値
class ActualValuesViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.request.query_params.get('company_id', None)
        user_id = self.request.user.id

        if company_id is not None:
            if not is_user_viewer(company_id, user_id):
                raise PermissionDenied()
        else:
            raise Http404

        data_type = self.request.query_params.get('data_type', None)
        channel_numbers = get_channel_no_list(request.query_params.get('ch', None)) # ch=1,2,3

        result = get_actual_values(company_id, data_type, channel_numbers)

        return Response(result)


# 予測値
class PredictedValuesViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        company_id = self.request.query_params.get('company_id', None)
        user_id = self.request.user.id
        if company_id is not None:
            if not is_user_viewer(company_id, user_id):
                raise PermissionDenied()
        else:
            raise Http404

        data_type = self.request.query_params.get('data_type', None)

        result = get_predicted_values(company_id, data_type)
        return Response(result)










# グラフ情報の管理

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
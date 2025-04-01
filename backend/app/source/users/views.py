import datetime
import logging
from django.db import transaction
import jwt
from config.settings import DEMO_ACCOUNT_PASSWORD, FRONTEND_URL, SECRET_KEY
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import F
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema, extend_schema_view
from ihiapp.function_update_data import kick_delete_thread
# モデルをインポート
from ihiapp.models import UnitPriceHistory, UserEntityPermission
from rest_framework import (generics, mixins, permissions, status, views,
                            viewsets)
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import USER_EMAIL_EXISTS_ERROR
from ihiapp.constants import SENDER_EMAIL
from .forms import CreateAdminUserForm, CreateUserForm, DeleteDataForm
from .models import (Company, CompanyUser, Notification, User,
                     UserActivationToken)
from .serializer import (CompanySerializer, DailyRevenueSerializer,
                         NotificationSerializer, UserActivationSerializer,
                         UserSerializer, ActivateUserSerializer, UserByActivationTokenSerializer)
from ihiapp.function_create_set_password_message import create_set_password_message
from ihiapp.function_send_mail import send_mail_from_service

class CustomUserPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return super().has_permission(request, view)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema_view(
    create=extend_schema(
        description="ユーザ作成",
        request=UserSerializer,
        responses={201: UserSerializer},
    )
)
class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    permission_classes = [CustomUserPermission]

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            if USER_EMAIL_EXISTS_ERROR in str(e):
                return Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"message": USER_EMAIL_EXISTS_ERROR},
                )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=e.detail)

        with transaction.atomic():
            user = serializer.save()
            if (user.company_id):
                company_user = CompanyUser(user=user, company=user.company_id)
                company_user.save()
                if user.company_id.root_entity:
                    user_entity_permission = UserEntityPermission(user=user, entity=user.company_id.root_entity)
                    user_entity_permission.save()

        return Response(status=status.HTTP_201_CREATED, data=UserSerializer(user).data)

    def update(self, request, *args, **kwargs):
        request_data = request.data.copy()
        # 閲覧権限のみのユーザーは権限関係のデータを変更できないようにする
        if (
            not request.user.groups.filter(name="管理権限").exists()
            and not request.user.groups.filter(name="ユーザー管理者").exists()
            and not request.user.company_id.admin_user_id == request.user
        ):
            request_data.pop("has_view_role", None)
            request_data.pop("has_manage_role", None)

        serializer = self.get_serializer(
            self.get_object(), data=request_data, partial=True
        )
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            if USER_EMAIL_EXISTS_ERROR in str(e):
                return Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"message": USER_EMAIL_EXISTS_ERROR},
                )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=e.detail)

        serializer.save()
        return Response(serializer.data)

    def get_queryset(self):
        user_id = self.kwargs.get("pk")
        if str(user_id) == str(self.request.user.id):
            return User.objects.filter(id=user_id)

        if self.request.method == "PATCH" or self.request.method == "PUT" or self.request.method == "DELETE":
            user = User.objects.get(id=user_id)
            company = user.company_id
            if CompanyUser.objects.filter(user=self.request.user, company=company).exists():
                return User.objects.filter(id=user_id)
            else:
                return User.objects.none()

        email = self.request.query_params.get("email", None)
        company_id = self.request.query_params.get("company_id", None)
        if email is not None and company_id is not None:
            target_uesr = User.objects.filter(email=email).first()
            if target_uesr is not None:
                company = Company.objects.filter(id=company_id).first()
                if company is not None:
                    company_user = CompanyUser.objects.filter(
                        user=target_uesr, company=company
                    ).first()
                    if company_user is not None:
                        return User.objects.filter(id=target_uesr.id)
        elif company_id is not None:
            company = Company.objects.filter(id=company_id).first()
            if company is not None:
                company_users = CompanyUser.objects.filter(company=company)
                return User.objects.filter(id__in=company_users.values("user"))
        return User.objects.none()


class UserActivationViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserActivationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            user_activation_token = UserActivationToken.objects.get(
                key=request.data["token"]
            )
        except UserActivationToken.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"message": "トークンが不正です"}
            )

        user = user_activation_token.user
        if timezone.now() <= user_activation_token.expiration_date:
            user.is_active = True
            user.save()
            user_activation_token.delete()
            return Response(status=status.HTTP_200_OK)
        user_activation_token.delete()
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"message": "トークンの有効期限が切れています"}
        )

    def get_queryset(self):
        return User.objects.all()


class ActivateUserView(APIView):
    # 通常の認証はせず、アクティベーショントークンを検証する
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_USER_ACTIVATION_TOKEN')
        if not token:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED, data={"message": "トークンが無効です"}
            )
        try:
            user_activation_token = UserActivationToken.objects.get(
                key=token
            )
        except Exception:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED, data={"message": "トークンが無効です"}
            )

        serializer = ActivateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={ "errors": serializer.errors }
            )
        user = user_activation_token.user
        if timezone.now() <= user_activation_token.expiration_date:
            user.is_active = True
            user.username = request.data.get('username')
            user.affiliation = request.data.get('affiliation')
            user.set_password(request.data.get('password'))
            user.save()
            user_activation_token.delete()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        user_activation_token.delete()
        return Response(
            status=status.HTTP_401_UNAUTHORIZED, data={"message": "トークンが無効です"}
        )

class UserByActivationTokenView(APIView):
    # 通常の認証はせず、アクティベーショントークンを検証する
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_USER_ACTIVATION_TOKEN')
        if not token:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED, data={"message": "トークンが無効です"}
            )
        try:
            user_activation_token = UserActivationToken.objects.get(
                key=token
            )
        except Exception:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED, data={"message": "トークンが無効です"}
            )

        user = user_activation_token.user
        if timezone.now() <= user_activation_token.expiration_date:
            return Response(UserByActivationTokenSerializer(user).data, status=status.HTTP_200_OK)
        return Response(
            status=status.HTTP_401_UNAUTHORIZED, data={"message": "トークンが無効です"}
        )

class CurrentUserView(
    views.APIView,
):
    serializer_class = UserSerializer

    def get(self, request, format=None):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"message": "認証情報がありません"},
            )

    def get_queryset(self):
        return User.objects.all()


class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Notification.objects.filter(user=self.request.user).order_by(
                F("created_at").desc()
            )
        else:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"message": "認証情報がありません"},
            )


class NotificationDetailView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]


class UpdateDailyRevenueView(generics.UpdateAPIView):
    serializer_class = DailyRevenueSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# パスワードの変更
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response({'error': 'パスワードが違います。'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'success': 'パスワードが正常に更新されました。'}, status=status.HTTP_200_OK)

def send_user_activation_email(user, token):
    mail_subject = "【IHIダッシュボード運営事務局】 パスワード設定・再設定について"

    url = f"{FRONTEND_URL}/signup-with-magic-link?token={token.key}"
    message = create_set_password_message(url)

    send_mail_from_service(mail_subject, message, [user.email])

# CreateUserFormを使用して、ユーザーを作成する、作成後、パスワードリセットのメールを送信する
def create_user(request, company_id):
    if request.method == 'POST':
        form = CreateUserForm(request.POST, initial={'company_id': company_id})
        if form.is_valid():
            form.save()
            user = form.save(commit=False)
            user.company_id = Company.objects.get(id=company_id)
            user.is_staff = False
            user.is_active = False
            with transaction.atomic():
                user.save()
                if (user.company_id):
                    company_user = CompanyUser(user=user, company=user.company_id)
                    company_user.save()
                    # UserEntityPermission
                    if user.company_id.root_entity:
                        user_entity_permission = UserEntityPermission(user=user, entity=user.company_id.root_entity)
                        user_entity_permission.save()

            if user:
                token = UserActivationToken(user=user)
                token.save()
                send_user_activation_email(user, token)

            return redirect('admin:users_user_changelist')
    else:
        form = CreateUserForm(initial={'company_id': company_id})
    return render(request, 'create_user.html', {'form': form})


# CreateAdminUserFormを使用して、管理者ユーザーを作成する
def create_admin_user(request, company_id):
    if request.method == 'POST':
        form = CreateAdminUserForm(request.POST, initial={'company_id': company_id})
        if form.is_valid():
            user = form.save(commit=False)
            user.company_id = Company.objects.get(id=company_id)
            user.is_staff = True
            user.is_active = True
            user.save()

            # グループ取得（存在しない場合は作成）
            group, created = Group.objects.get_or_create(name='ユーザー管理者')
            # ユーザーをグループに追加
            user.groups.add(group)

            # companyのadmin_user_idにuserのFKを設定する
            company = Company.objects.get(id=company_id)
            company.admin_user_id = user
            company.save()

            # CompanyUserに登録
            company_user = CompanyUser(user=user, company=company)
            company_user.save()

            # UserEntityPermission
            if company.root_entity:
                user_entity_permission = UserEntityPermission(user=user, entity=company.root_entity)
                user_entity_permission.save()

            return redirect('admin:users_user_changelist')
    else:
        form = CreateAdminUserForm(initial={'company_id': company_id})
    return render(request, 'create_user.html', {'form': form})


# DeleteDataFormを使用して、日時を取得し該当するデータを削除する
def delete_data(request, company_id):
    if request.method == 'POST':
        form = DeleteDataForm(request.POST, initial={'company_id': company_id})
        if form.is_valid():
            # 日時を取得
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            # 企業名を取得
            company = Company.objects.get(id=company_id)
            # メッセージを作成
            msg = f"次の企業、日付、時間が指定されました<br>　企業：{company}<br>　日付： {date}<br>時間： {time}<br>＊指定の日時以前のデータを削除します<br>"

            # 削除処理を実行
            kick_delete_thread(date, time, company_id)
            return render(request, 'delete_data_done.html', {'msg': msg})
    else:
        form = DeleteDataForm(initial={'company_id': company_id})
    return render(request, 'delete_data.html', {'form': form})



# api /reset_password_requestからパスワードリセットをリクエストできるようにViewを準備、一旦使用していない
class PasswordResetRequestView(APIView):
    queryset = User.objects.none()
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            mail_subject = 'Password Reset Requested'
            message = f'Click the link to reset password http://{current_site.domain}/user/reset_password/{uid}/{token}'
            send_mail(mail_subject, message, 'admin@mywebsite.com', [user.email])
        return Response({'message': 'メールが送信されました'}, status=status.HTTP_200_OK)

# api /reset_password/<uidb64>/<token>/からパスワードをリセットできるようにViewを準備
class PasswordResetConfirmView(APIView):
    queryset = User.objects.none()
    permission_classes = [AllowAny]
    def post(self, request, uidb64, token):
        password = request.data.get('password')
        try:
            uid = uid_decoder(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.is_active = True
                user.save()
                # user情報を返す
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'トークンが無効です。'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'message': 'uidが無効です。'}, status=status.HTTP_400_BAD_REQUEST)

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # NOTE: 実装時点でbizのエンティティ周りの権限仕様が不明瞭なため、いったん企業とユーザーの紐付けだけ見ている
        # permit_company_ids = set( map(lambda x: x.entity.company.id, UserEntityPermission.objects.filter(user=self.request.user)) )
        # admin_company_ids = set( map(lambda x: x.id, Company.objects.filter(admin_user_id=self.request.user)) )
        # permit_company_ids = permit_company_ids | admin_company_ids
        user_company_ids = set( map(lambda x: x.company.id, CompanyUser.objects.filter(user=self.request.user)) )
        # company_ids = permit_company_ids & user_company_ids
        return Company.objects.all().filter(id__in=user_company_ids)

    def partial_update(self, request, *args, **kwargs):
        # リクエストが来た時点でのオブジェクトの現在の状態を取得
        instance = self.get_object()
        original_data = model_to_dict(instance)

        # リクエストデータに基づいてオブジェクトを更新
        response = super().partial_update(request, *args, **kwargs)

        # 更新後のオブジェクトの状態を取得
        instance = self.get_object()
        updated_data = model_to_dict(instance)

        # 差分を取得
        field_name = {'electric_unit_price':"電気(円/kWh)",
                        'water_unit_price':"水(円/m3)",
                        'fuel_unit_price':"燃料(円/m3)",
                        'co2_unit_price':"CO2(円/t-CO2)",
                        'electric_unit_co2':"電気(t-CO2/kWh)",
                        'water_unit_co2':"水(t-CO2/m3)",
                        'fuel_unit_co2':"燃料(t-CO2/m3)",}
        diff = {k: (original_data[k], updated_data[k]) for k in original_data if original_data[k] != updated_data[k] and k in field_name.keys()}

        # 差分をUnitPriceHistoryオブジェクトとして保存
        for field, (old_value, new_value) in diff.items():
            history = UnitPriceHistory(
                company=instance,
                field=field,
                name=field_name[field],
                before=old_value,
                after=new_value,
            )
            history.save()

        return response

class DemoAccountAuthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        demo_user = User.objects.get(is_demo=True)
        refresh = RefreshToken.for_user(demo_user)
        access_token = str(refresh.access_token)

        return Response({'access': access_token}, status=status.HTTP_200_OK)

class IsCompanyAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        company_id = kwargs.get('pk')
        if Company.objects.filter(id=company_id).exists():
            company = Company.objects.get(id=company_id)
        else:
            return Response({'message': '企業が存在しません'}, status=status.HTTP_400_BAD_REQUEST)

        if company.admin_user_id == request.user:
            return Response({'is_admin': True}, status=status.HTTP_200_OK)
        else:
            return Response({'is_admin': False}, status=status.HTTP_200_OK)
import hashlib
import logging
import uuid
from ihiapp.constants import SENDER_EMAIL, REPLY_TO_EMAIL
from config.settings import FRONTEND_URL
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from ihiapp.function_create_set_password_message import create_set_password_message
from django.core.mail import EmailMessage
from ihiapp.function_send_mail import send_mail_from_service

class Company(models.Model):
    """企業"""

    class Meta:
        verbose_name = "企業"
        verbose_name_plural = "企業"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=30, unique=True, verbose_name="企業名")
    economic_activity_unit = models.ForeignKey(
        "ihiapp.EconomicActivityUnit",
        null=True,
        on_delete=models.CASCADE,
        verbose_name="経済活動単位",
    )
    # 料金単価設定
    electric_unit_price = models.IntegerField(default=0, verbose_name="電気(円/kWh)")
    water_unit_price = models.IntegerField(default=0, verbose_name="水(円/m3)")
    fuel_unit_price = models.IntegerField(default=0, verbose_name="燃料(円/m3)")
    co2_unit_price = models.IntegerField(default=0, verbose_name="CO2(円/t-CO2)")

    # CO2排出量単価設定
    electric_unit_co2 = models.FloatField(default=0, verbose_name="電気(t-CO2/kWh)")
    water_unit_co2 = models.FloatField(default=0, verbose_name="水(t-CO2/m3)")
    fuel_unit_co2 = models.FloatField(default=0, verbose_name="燃料(t-CO2/m3)")

    # 管理者のuser_id(user_idはUserモデルのFK)
    # admin_user_id = models.ForeignKey("User", null=True, on_delete=models.CASCADE, verbose_name="管理者")
    admin_user_id = models.ForeignKey("User", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="管理者")
    root_entity = models.ForeignKey('ihiapp.Entity', null=True, blank=True, on_delete=models.CASCADE, verbose_name="ルートエンティティ", related_name='root_company' )
    batch_enabled = models.BooleanField(default=False, verbose_name="バッチ処理の有効化")

    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.name


class UserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = User.objects.filter(email=email, is_active=False).first()
        if user:
            # 仮登録状態のユーザーが存在する場合は一度削除する
            user.delete()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)

        user_activation_token = UserActivationToken(user=user)
        user_activation_token.save()

        self.send_user_activation_email(user, user_activation_token)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def send_user_activation_email(self, user, token):
        mail_subject = "【IHIダッシュボード運営事務局】 パスワード設定・再設定について"

        url = f"{FRONTEND_URL}/signup-with-magic-link?token={token.key}"
        message = create_set_password_message(url)

        send_mail_from_service(mail_subject, message, [user.email])

from cryptography.fernet import Fernet
from django.conf import settings


class EncryptedCharField(models.CharField):
    def from_db_value(self, value, expression, connection):
        if value is not None:
            # raise ValueError("TEST: %s  , %s "%(settings.ENCRYPTION_KEY , value))
            if settings.ENCRYPTION_KEY is None:
                 raise ValueError("ENCRYPTION_KEY is not set.")
            return Fernet(settings.ENCRYPTION_KEY).decrypt(value.encode()).decode()
        return value

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value is not None:
            if settings.ENCRYPTION_KEY is None:
                raise ValueError("ENCRYPTION_KEY is not set.")
            return Fernet(settings.ENCRYPTION_KEY).encrypt(value.encode()).decode()
        return value

class User(AbstractBaseUser, PermissionsMixin):
    """Custom User"""

    class Meta:
        verbose_name = "ユーザ"
        verbose_name_plural = "ユーザ"
        constraints = [
            models.UniqueConstraint(fields=['is_demo'], name='unique_true_is_demo', condition=models.Q(is_demo=True))
        ]

    # username_validator = UnicodeUsernameValidator()

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    username = models.CharField(max_length=30, unique=False, verbose_name="氏名")
    email = models.EmailField(unique=True, verbose_name="メールアドレス")  # これで認証する
    is_active = models.BooleanField(default=False, verbose_name="アクティブ権限")
    is_staff = models.BooleanField(default=True, verbose_name="スタッフ権限")
    is_superuser = models.BooleanField(default=False, verbose_name="管理者権限")
    is_locked = models.BooleanField(default=False, verbose_name="アカウントのロック状態")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="アカウント作成日時")
    password_changed = models.BooleanField(default=False, verbose_name="パスワードを変更したか")
    password_changed_date = models.DateTimeField(
        blank=True, null=True, verbose_name="最終パスワード変更日時"
    )
    company_id = models.ForeignKey(
        Company, null=True, on_delete=models.CASCADE, verbose_name="企業"
    )

    is_agreed_to_terms_of_service = models.BooleanField(default=False, verbose_name="利用規約に同意したか")

    daily_revenue = models.BigIntegerField(verbose_name="1日あたりの売上", blank=True, null=True)
    is_demo = models.BooleanField(default=False, verbose_name="デモユーザーかどうか")
    affiliation = models.CharField(max_length=100, verbose_name="所属", blank=True, null=True)

    # # 料金単価設定
    # electric_unit_price = models.IntegerField(default=0, verbose_name="電気(円/kWh)")
    # water_unit_price = models.IntegerField(default=0, verbose_name="水(円/m3)")
    # fuel_unit_price = models.IntegerField(default=0, verbose_name="燃料(円/m3)")
    # co2_unit_price = models.IntegerField(default=0, verbose_name="CO2(円/t-CO2)")

    # # CO2排出量単価設定
    # electric_unit_co2 = models.FloatField(default=0, verbose_name="電気(t-CO2/kWh)")
    # water_unit_co2 = models.FloatField(default=0, verbose_name="水(t-CO2/m3)")
    # fuel_unit_co2 = models.FloatField(default=0, verbose_name="燃料(t-CO2/m3)")

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELD = ""

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f'{self.email} ({self.username})'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


ACTIVATION_EXPIRATION_HOURS = 72


def default_expiration_date():
    return timezone.now() + timezone.timedelta(hours=ACTIVATION_EXPIRATION_HOURS)


class UserActivationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True)
    expiration_date = models.DateTimeField(default=default_expiration_date)


class Notification(models.Model):
    class Meta:
        verbose_name = "お知らせ"
        verbose_name_plural = "お知らせ"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

class CompanyUser(models.Model):
    class Meta:
        verbose_name = "企業とユーザーの紐付け"
        verbose_name_plural = "企業とユーザーの紐付け"
        unique_together = (('company', 'user'),)

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="企業")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザ")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.company} ({self.user})'

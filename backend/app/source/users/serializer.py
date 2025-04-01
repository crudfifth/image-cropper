from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .constants import USER_EMAIL_EXISTS_ERROR
from .models import Company, Notification, User, CompanyUser


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "economic_activity_unit",
                    "electric_unit_price", "water_unit_price", "fuel_unit_price", "co2_unit_price",
                    "electric_unit_co2", "water_unit_co2", "fuel_unit_co2", "batch_enabled", "root_entity_id",
                  ]

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField()
    company = CompanySerializer(source="company_id", read_only=True)
    is_admin = serializers.SerializerMethodField()
    is_manager = serializers.SerializerMethodField()
    has_manage_role = serializers.BooleanField(required=False)
    has_view_role = serializers.BooleanField(required=False)
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_demo",
            "is_locked",
            "company_id",
            "company",
            "daily_revenue",
            "is_agreed_to_terms_of_service",
            "affiliation",

            "is_admin",
            "is_manager",
            "has_manage_role",
            "has_view_role",
        )

    # 運営者
    def get_is_admin(self, obj):
        return obj.groups.filter(name="運営者").exists()

    # ユーザー管理者
    def get_is_manager(self, obj):
        return obj.company_id.admin_user_id == obj or obj.groups.filter(name="ユーザー管理者").exists()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['has_manage_role'] = instance.groups.filter(name="管理権限").exists()
        ret['has_view_role'] = instance.groups.filter(name="閲覧権限").exists()
        return ret

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if self.instance:
            if attrs.get("email") and User.objects.filter(email=attrs["email"], is_active=True).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(USER_EMAIL_EXISTS_ERROR)
            return attrs
        if attrs.get("email") and User.objects.filter(email=attrs["email"], is_active=True).exists():
            raise serializers.ValidationError(USER_EMAIL_EXISTS_ERROR)
        return attrs

    def create(self, validated_data):
        is_superuser = validated_data.get("is_superuser", False)
        if is_superuser:
            user = User.objects.create_superuser(
                email=validated_data["email"],
                password=validated_data.get("password", None),
                username=validated_data["username"],
                is_staff=validated_data.get("is_staff", True),
                company_id=validated_data.get("company_id", None),
                affiliation=validated_data.get("affiliation", None),
                is_locked=validated_data.get("is_locked", False),
            )
        else:
            user = User.objects.create_user(
                email=validated_data["email"],
                password=validated_data.get("password", None),
                username=validated_data["username"],
                is_staff=validated_data.get("is_staff", True),
                company_id=validated_data.get("company_id", None),
                affiliation=validated_data.get("affiliation", None),
                is_locked=validated_data.get("is_locked", False),
            )

        if validated_data.get("is_admin"):
            user.groups.add(Group.objects.get(name="運営者"))
        if validated_data.get("is_manager"):
            user.groups.add(Group.objects.get(name="ユーザー管理者"))
        if validated_data.get("has_manage_role"):
            user.groups.add(Group.objects.get(name="管理権限"))
        # 閲覧権限を持つ状態で常に作成
        user.groups.add(Group.objects.get(name="閲覧権限"))
        user.save()

        return user

    def update(self, instance, validated_data):
        is_admin = validated_data.pop('is_admin', None)
        is_manager = validated_data.pop('is_manager', None)
        has_manage_role = validated_data.pop('has_manage_role', None)
        has_view_role = validated_data.pop('has_view_role', None)

        for attr, value in validated_data.items():
            if attr != "password":
                setattr(instance, attr, value)

        # has_manage_roleの処理
        if has_manage_role is not None:
            manage_role_group = Group.objects.get(name="管理権限")
            if has_manage_role:
                instance.groups.add(manage_role_group)
            else:
                instance.groups.remove(manage_role_group)

        # has_view_roleの処理
        if has_view_role is not None:
            view_role_group = Group.objects.get(name="閲覧権限")
            if has_view_role:
                instance.groups.add(view_role_group)
            else:
                instance.groups.remove(view_role_group)

        instance.save()

        return instance


class UserActivationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

class ActivateUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    affiliation = serializers.CharField()
    password = serializers.CharField()

class UserByActivationTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "title", "body", "created_at", "updated_at"]

class DailyRevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['daily_revenue']

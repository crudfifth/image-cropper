import hashlib

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from ihiapp.models import AnnualPlanValues, DataStructure, Entity, UnitPriceHistory
from .models import Company, CompanyUser, Notification, User
from ihiapp.models import ChannelAdapter

@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('company_id',)}),
        (_('個人情報',), {'fields': ('email','username', 'password',)}),
        # (_('料金単価設定',), {'fields': ('electric_unit_price', 'water_unit_price', 'fuel_unit_price', 'co2_unit_price',)}),
        # (_('CO2排出量単価設定',), {'fields': ('electric_unit_co2', 'water_unit_co2', 'fuel_unit_co2',)}),
        (_('権限',), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_locked', 'groups', 'user_permissions')}),
        (_('パスワード',), {'fields': ('password_changed', 'password_changed_date',)}),
        (_('日時関連',), {'fields': ('last_login', 'date_joined',)}),
        # (_('1日あたりの売上',), {'fields': ('daily_revenue',)}),
    )

    list_display = (
        'email',
        'username',
        'company_id',
        'is_active',
        'is_staff',
        'is_superuser',
        'is_locked',
        'groups_display',
        'password_changed',
        'password_changed_date',
        'last_login',
        'date_joined',
        'is_company_admin',
        )

    # company_idのadmin_user_idと一致する場合はTrueを表示する
    def is_company_admin(self, obj=None):
        if obj.company_id is not None:
               return obj.company_id.admin_user_id == obj
        return False
    is_company_admin.boolean = True
    is_company_admin.short_description = 'ユーザー管理者'


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'company_id', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'daily_revenue')}
        ),
    )

    def get_list_display(self, request):
        # 現在のユーザーがスーパーユーザーでない場合、一覧表示から非表示にし、任意のフィールドを表示する。
        if not request.user.is_superuser:
            group = request.user.groups.all()
            if group.filter(name='運営者').exists():
                list_display = (
                'email',
                'username',
                'company_id',
                'is_active',
                'groups_display',
                'last_login',
                'date_joined',
                'is_company_admin',
                )
            else:
                list_display = (
                'email',
                'username',
                'company_id',
                'last_login',
                'date_joined',
                'is_active',
                'is_company_admin',
                )

            return list_display
        return super().get_list_display(request)

    def get_fieldsets(self, request, obj=None):
        # 現在のユーザーがスーパーユーザーでない場合、フォームから非表示にし、任意のフィールドを表示する。
        if not request.user.is_superuser:
            group = request.user.groups.all()
            if group.filter(name='運営者').exists():
                # return super().get_fieldsets(request, obj)
                fieldsets = (
                    (None, {'fields': ('company_id',)}),
                    (_('個人情報',), {'fields': ('email','username',)}),
                    (_('権限',), {'fields': ('is_active','groups')}),
                    (_('日時関連',), {'fields': ('last_login', 'date_joined',)}),
                )
            else:
                fieldsets = (
                    (None, {'fields': ('company_id',)}),
                    (_('個人情報',), {'fields': ('email','username',)}),
                    (_('日時関連',), {'fields': ('last_login', 'date_joined',)}),
                )
            return fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ()
        if not request.user.is_superuser:
            readonly_fields += ('email', 'company_id', 'last_login', 'date_joined',)
        return readonly_fields

    def get_list_filter(self, request):
        group = request.user.groups.all()
        list_filter = ()
        if request.user.is_superuser:
            list_filter += (
                'company_id',
                'is_active',
                'is_superuser',
            )
        else :
            if group.filter(name='運営者').exists():
                list_filter += ('company_id',)
        return list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        group = request.user.groups.all()
        if request.user.is_superuser:
            return qs
        if group.filter(name='運営者').exists():
            return qs.filter(is_superuser=False)
        return qs.filter(company_id=request.user.company_id)

    # ユーザー管理者の場合はカスタムしたユーザー作成画面にリダイレクトする
    def add_view(self, request, form_url='', extra_context=None):
        group = request.user.groups.all()
        if group.filter(name='ユーザー管理者').exists():
            company = request.user.company_id
            return HttpResponseRedirect(reverse('create_user', args=[company.id]))
        return super().add_view(request, form_url, extra_context)

    # 
    def groups_display(self, obj):
        result_list = []
        groups = obj.groups.all()
        if groups.exists():
            for group in groups:
                result_list.append(group.name)
        return format_html("<br>".join(result_list))
    groups_display.short_description = "所属グループ"
 
# 企業に紐づいた管理者ユーザーを作成する
def create_admin_user_action(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(request, "1つの企業を選択してください", level='ERROR')
        return
    # companyのadmin_user_idがNoneじゃない場合は作成しない
    company = queryset.first()
    if company.admin_user_id is not None:
        modeladmin.message_user(request, "選択した企業はユーザー管理者が既に存在します", level='ERROR')
        return

    return HttpResponseRedirect(reverse('create_admin_user', args=[company.id]))

create_admin_user_action.short_description = "選択した企業の「ユーザー管理者」を作成する"


# 企業に紐づいた一般ユーザーを作成する
def create_user_action(modeladmin, request, queryset):
       if queryset.count() != 1:
           modeladmin.message_user(request, "1つの企業を選択してください", level='ERROR')
           return
       company = queryset.first()
       return HttpResponseRedirect(reverse('create_user', args=[company.id]))

create_user_action.short_description = "選択した企業の「一般ユーザー」を作成する"


# 企業に紐づいた取得データを削除する
def delete_data_action(modeladmin, request, queryset):
       if queryset.count() != 1:
           modeladmin.message_user(request, "1つの企業を選択してください", level='ERROR')
           return
       company = queryset.first()
       return HttpResponseRedirect(reverse('delete_data', args=[company.id]))

delete_data_action.short_description = "選択した企業の「取得データ」を削除する"

def create_entity_and_structure(modeladmin, request, queryset):
    for company in queryset:
        entity = Entity.objects.create(name=company.name, company=company)
        DataStructure.objects.create(ancestor=entity, descendant=entity, depth=0)
        company.root_entity = entity
        company.save()

create_entity_and_structure.short_description = '選択した企業に対してエンティティとデータ構造を作成'

# 企業に紐づいたチャンネル情報を作成する
def create_channel_action(modeladmin, request, queryset):
    if queryset.count() != 1:
        # 企業が複数選択されている場合はエラーを返す
        modeladmin.message_user(request, "1つの企業を選択してください", level='ERROR')
        return
    company = queryset.first()
    # root_entityがNoneの場合はエンティティデータとデータ構造を作成する
    if company.root_entity is None:
        entity = Entity.objects.create(name=company.name, company=company)
        DataStructure.objects.create(ancestor=entity, descendant=entity, depth=0)
        company.root_entity = entity
        company.save()

    # チャンネル情報が存在する場合はエラーを返す
    if ChannelAdapter.objects.filter(company_id=company).first() is not None:
        modeladmin.message_user(request, "選択した企業にはチャンネル情報が既に存在します", level='ERROR')
        return
    # チャンネル情報を作成する（CH1 - CH16）
    for ch_no in range(1, 17):
        ChannelAdapter.objects.create(
            company_id=company,
            channel_no=ch_no, 
            channel_name='CH_' + str(ch_no),
            device_number=None,
            equation_str="(x)",
        )

    # create a new AnnualPlanValuesView object
    AnnualPlanValues.objects.create(
        company_id=company,
        utility_cost=0.0,
        utility_cost_reduce=0.0,
        electric=0.0, 
        electric_reduce=0.0,
        co2_emissions=0.0, 
        co2_emissions_reduce=0.0,
        carbon_credit=0.0, 
        carbon_credit_price=0.0)


# create_channel_action.short_description = '選択した企業に対してチャンネル及びエンティティとデータ構造を作成'
create_channel_action.short_description = '選択した企業に対して内部情報を作成する'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin_user_id','economic_activity_unit', 'batch_enabled_display', 'created_at', 'updated_at',)
    # list_filter = ('created_at', 'updated_at',)
    search_fields = ('name',)
    ordering = ('-name',)
    fieldsets = (
        (None, {'fields': ('name', 'admin_user_id', 'economic_activity_unit', 'root_entity', 'batch_enabled')}),
        # (_('単価',), {'fields': ('electric_unit_price', 'water_unit_price', 'fuel_unit_price', 'co2_unit_price',)}),
        # (_('CO2排出量',), {'fields': ('electric_unit_co2', 'water_unit_co2', 'fuel_unit_co2',)}),
        (_('日時',), {'fields': ('created_at', 'updated_at',)}),
    )
    # actions = [create_user_action, create_admin_user_action, delete_data_action, create_entity_and_structure, create_channel_action]
    actions = [create_admin_user_action, create_channel_action]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ('created_at', 'updated_at',)
        if not request.user.is_superuser:
            readonly_fields += ('root_entity',)
        return readonly_fields

    def save_model(self, request, obj, form, change):
        # 変更前のオブジェクトの状態を取得
        if change:
            original_data = model_to_dict(Company.objects.get(pk=obj.pk))
        else:
            original_data = {}

        # オブジェクトを保存
        super().save_model(request, obj, form, change)

        # 変更後のオブジェクトの状態を取得
        updated_data = model_to_dict(obj)

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
                company=obj,
                field=field,
                name=field_name[field],
                before=old_value,
                after=new_value,
            )
            history.save()

    def batch_enabled_display(self, obj):
        icon = format_html('<img src="/sensor/static/admin/img/icon-{}.svg" alt="{}">', 'yes' if obj.batch_enabled else 'no', obj.batch_enabled)
        return format_html('{}&nbsp;&nbsp;&nbsp;&nbsp;{}', icon, '有効' if obj.batch_enabled else '無効')
    batch_enabled_display.short_description = f"{Company._meta.get_field('batch_enabled').verbose_name}"

@admin.register(Notification)
class Notification(admin.ModelAdmin):
    list_display = ('user', 'title', 'body', 'created_at', 'updated_at',)
    list_filter = ('created_at', 'updated_at',)
    search_fields = ('user',)
    ordering = ('-user',)
    readonly_fields = ('created_at', 'updated_at',)
    fieldsets = (
        (None, {'fields': ('user', 'title', 'body')}),
        (_('日時',), {'fields': ('created_at', 'updated_at',)}),
    )

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'created_at', 'updated_at',)
    list_filter = ('user', 'company',)
    search_fields = ('user', 'company',)
    readonly_fields = ('created_at', 'updated_at',)
    fieldsets = (
        (None, {'fields': ('company', 'user',)}),
        (_('日時',), {'fields': ('created_at', 'updated_at',)}),
    )

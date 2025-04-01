import datetime
import hashlib
import logging
import uuid
from email.policy import default
from enum import Enum

from cryptography.fernet import Fernet
from django.conf import settings
# from django_mysql.models import ListCharField
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from pyexpat import model
from users.models import Company, User

from .constants import (DATA_TYPE_CO2, DATA_TYPE_ELECTRICITY, DATA_TYPE_FUEL,
                        DATA_TYPE_WATER)


class EnvironmentalType(models.Model):
        id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
        name = models.CharField(max_length=255, unique=True, verbose_name="環境の種類名")
        created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
        updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

        def __str__(self):
                return self.name

        class Meta:
                verbose_name = "m.環境種類"
                verbose_name_plural = 'm.環境種類'

class DeviceType(models.Model):
        id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
        name = models.CharField(max_length=255, verbose_name="デバイスの種類名")
        created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
        updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

        def __str__(self):
                return self.name

        class Meta:
                verbose_name = "m.デバイス種類"
                verbose_name_plural = 'm.デバイス種類'

class Device(models.Model):
        class InputSource(models.IntegerChoices):
                DEVICE = 1, 'DEVICE'
                MANUAL = 2, 'MANUAL'
                CSV = 3, 'CSV'
        id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
        name = models.CharField(null=True, blank=True, max_length=255, verbose_name="デバイス名")
        data_source_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="データ取得対象名")
        device_number = models.IntegerField(null=True, blank=True, verbose_name="デバイス型番")
        device_type_id = models.ForeignKey(DeviceType, null=True, blank=True, on_delete=models.CASCADE, verbose_name="デバイスの種類ID") # 廃止予定
        pushlog_unique_id = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="PUSHLOGのユニークID")
        gateway_id = models.ForeignKey('Gateway', on_delete=models.CASCADE, verbose_name="ゲートウェイID", null=True, blank=True)
        pushlog_api = models.ForeignKey('PushlogApi', on_delete=models.CASCADE, verbose_name="PUSHLOG API", null=True, blank=True)
        m_device_id = models.ForeignKey('MDevice', on_delete=models.CASCADE, verbose_name="マスタデバイスID", null=True, blank=True) # 廃止予定
        input_source = models.IntegerField(choices=InputSource.choices, default=InputSource.DEVICE, verbose_name="入力元")
        unit_id = models.ForeignKey('Unit', on_delete=models.CASCADE, verbose_name="単位ID", null=True, blank=True)
        liquid_type_id = models.ForeignKey('LiquidType', on_delete=models.CASCADE, verbose_name="燃料種類", null=True, blank=True)
        specific_gravity = models.CharField(max_length=100, verbose_name="比重", null=True, blank=True)
        economic_activity_type_id = models.ForeignKey('EconomicActivityType', on_delete=models.CASCADE, verbose_name="経済活動量種別ID", null=True, blank=True)
        enable_data_collection = models.BooleanField(default=False, verbose_name="データ収集を有効にするか")
        entity = models.ForeignKey('Entity', on_delete=models.CASCADE, verbose_name="エンティティID", null=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
        updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

        is_instantaneous = models.BooleanField(default=False, verbose_name="瞬時値（True）/積算値（False）")

        class Meta:
                verbose_name = "m.データ取得対象"
                verbose_name_plural = 'm.データ取得対象'

        def __str__(self):
                return f'{self.name}:{self.data_source_name}({self.id})'

class MDevice(models.Model):
        id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
        name = models.CharField(max_length=255, default='' ,verbose_name="デバイス名")
        device_number = models.IntegerField(verbose_name="デバイス型番")
        device_type_id = models.ForeignKey(DeviceType, default=0, on_delete=models.CASCADE, verbose_name="デバイスの種類ID")
        environmental_type_id = models.ForeignKey(EnvironmentalType, default=0, on_delete=models.CASCADE, verbose_name="環境の種類ID")
        created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
        updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

        def __str__(self):
                return self.name

        class Meta:
                verbose_name = "マスタデバイス"
                verbose_name_plural = 'マスタデバイス'



# 抽象基底クラス定義
class DataModel(models.Model):
        id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
        pushlog_api = models.ForeignKey('PushlogApi', on_delete=models.CASCADE, null=True, blank=True, verbose_name="PUSHLOG API ID")
        electrical_value = models.FloatField(verbose_name="電気/取得値(kW)", validators=[MinValueValidator(0),], blank=True, null=True,)
        electrical_price = models.IntegerField(verbose_name="電気/料金(円)", validators=[MinValueValidator(0),], blank=True, null=True,)
        water_value = models.FloatField(verbose_name="水/取得値(L)", validators=[MinValueValidator(0),], blank=True, null=True,)
        water_price = models.IntegerField(verbose_name="水/料金(円)", validators=[MinValueValidator(0),], blank=True, null=True,)
        fuel_value = models.FloatField(verbose_name="燃料/取得値(L)", validators=[MinValueValidator(0),], blank=True, null=True,)
        fuel_price = models.IntegerField(verbose_name="燃料/料金(円)", validators=[MinValueValidator(0),], blank=True, null=True,)
        co2_value = models.FloatField(verbose_name="CO2/取得値(t-CO2)", validators=[MinValueValidator(0),], blank=True, null=True,)
        co2_price = models.IntegerField(verbose_name="CO2/料金(円)", validators=[MinValueValidator(0),], blank=True, null=True,)
        energy_saving_value = models.FloatField(verbose_name="省エネ創出(t-CO2)", validators=[MinValueValidator(0),], blank=True, null=True,)
        renewal_energy_value = models.FloatField(verbose_name="再エネ創出(t-CO2)", validators=[MinValueValidator(0),], blank=True, null=True,)
        utility_costs = models.IntegerField(verbose_name="光熱費(円)", validators=[MinValueValidator(0),], blank=True, null=True,)
        get_data_date = models.DateTimeField(verbose_name="取得日時", default=datetime.datetime(2023, 1, 1, 0, 0))
        created_at = models.DateTimeField(verbose_name="作成日時", auto_now_add=True)

        def __str__(self):
                return str(self.id)

        class Meta:
                abstract = True


# フィールドが存在するか確認する関数
@classmethod
def model_field_exists(cls, field):
    try:
        cls._meta.get_field(field)
        return True
    except:
        return False
models.Model.field_exists = model_field_exists



# 保存時に、他のモデルにも保存する関数
def save_data(model, self):
        # フィルターの設定
        filter = {}
        # フィールドが存在するか確認
        if model.field_exists('year'):
                filter['year'] = self.year
        if model.field_exists('month'):
                filter['month'] = self.month
        if model.field_exists('date'):
                filter['date'] = self.date
        if model.field_exists('hour'):
                filter['hour'] = self.hour
        if model.field_exists('minute'):
                filter['minute'] = self.minute
        if model.field_exists('device_id'):
                filter['device_id'] = self.device_id
        if model.field_exists('pushlog_api'):
                filter['pushlog_api'] = self.pushlog_api

        data_model = model.objects.filter(**filter)
        if data_model.exists():
                data_model = data_model[0]
        else:
                data_model = model.objects.create(**filter)

        device_unit_price = DeviceUnitPrice.objects.filter(device=self.device_id).first()
        if device_unit_price is None:
               logging.warn(f"device_unit_price is None device_id: {self.device_id}")
        else:
                # valueかpriceが渡ってくる想定のため、片方の値からもう片方の値を計算する
                # 電気は、値がkWh, 単価が円/kWh, 計算結果は小数点第2位
                if self.electrical_value and not self.electrical_price:
                        self.electrical_price = round(float(self.electrical_value) * device_unit_price.electric_unit_price, 2)
                elif not self.electrical_value and self.electrical_price:
                        self.electrical_value = round(self.electrical_price / device_unit_price.electric_unit_price, 2)
                # 水は、値の単位がm3, 単価の単位が 円/m3, 計算結果は小数点第2位
                if self.water_value and not self.water_price:
                        self.water_price = round(float(self.water_value) * device_unit_price.water_unit_price, 2)
                elif not self.water_value and self.water_price:
                        self.water_value = round(self.water_price / device_unit_price.water_unit_price, 2)
                # 燃料は、値の単位がm3, 単価の単位が 円/m3, 計算結果は小数点第2位
                if self.fuel_value and not self.fuel_price:
                        self.fuel_price = round(float(self.fuel_value) * device_unit_price.fuel_unit_price, 2)
                elif not self.fuel_value and self.fuel_price:
                        self.fuel_value = round(self.fuel_price / device_unit_price.fuel_unit_price, 2)

                # 光熱費(電気＋水＋燃料)の計算
                utility_costs = 0
                utility_costs += self.electrical_price if self.electrical_price else 0
                utility_costs += self.water_price if self.water_price else 0
                utility_costs += self.fuel_price if self.fuel_price else 0

                # CO2の計算
                # 電気は、値の単位がkWh, 単価の単位が t-CO2/kWh
                # 燃料は、値の単位がm3, 単価の単位が t-CO2/m3
                # 水は、CO2を出さないため、0
                # 小数点第2位への丸めは合計を求めた後で行う
                co2_value = 0.0
                co2_value += self.electrical_value * device_unit_price.electric_unit_co2 if self.electrical_value else 0.0
                co2_value += self.water_value * device_unit_price.water_unit_co2 if self.water_value else 0.0
                co2_value += self.fuel_value * device_unit_price.fuel_unit_co2 if self.fuel_value else 0.0

                # 同一条件で保存済みのデータがあればそこに加算する
                # 光熱費とCo2
                if not data_model.utility_costs and utility_costs:
                        data_model.utility_costs = utility_costs
                elif data_model.utility_costs and utility_costs:
                        data_model.utility_costs = data_model.utility_costs + utility_costs
                if not data_model.co2_value and co2_value:
                        data_model.co2_value = round(co2_value, 2)
                        data_model.co2_price = round(co2_value * device_unit_price.co2_unit_price, 2)
                elif data_model.co2_value and co2_value:
                        data_model.co2_value = round(data_model.co2_value + co2_value, 2)
                        data_model.co2_price = round(data_model.co2_price + co2_value * device_unit_price.co2_unit_price, 2)

                # 電気
                if not data_model.electrical_value and self.electrical_value:
                        data_model.electrical_value = self.electrical_value
                elif data_model.electrical_value and self.electrical_value:
                        data_model.electrical_value = round(data_model.electrical_value + self.electrical_value, 2)
                if not data_model.electrical_price and self.electrical_price:
                        data_model.electrical_price = self.electrical_price
                elif self.electrical_price:
                        data_model.electrical_price = round(data_model.electrical_price + self.electrical_price, 2)

                # 水
                if not data_model.water_value:
                        data_model.water_value = self.water_value
                elif self.water_value:
                        data_model.water_value = round(data_model.water_value + self.water_value, 2)
                if not data_model.water_price:
                        data_model.water_price = self.water_price
                elif self.water_price:
                        data_model.water_price = round(data_model.water_price + self.water_price, 2)


                # 燃料
                if not data_model.fuel_value:
                        data_model.fuel_value =  self.fuel_value
                elif self.fuel_value:
                        data_model.fuel_value = round(data_model.fuel_value + self.fuel_value, 2)
                if not data_model.fuel_price:
                        data_model.fuel_price = self.fuel_price
                elif self.fuel_price:
                        data_model.fuel_price = round(data_model.fuel_price + self.fuel_price, 2)

                data_model.get_data_date = datetime.datetime(self.year, self.month, self.date, self.hour, self.minute)

                data_model.save()


# 合計値/分単位
class DataPerMinute(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        month = models.IntegerField(verbose_name="月", validators=[MinValueValidator(1), MaxValueValidator(12),],default=1)
        date = models.IntegerField(verbose_name="日", validators=[MinValueValidator(1), MaxValueValidator(31),],default=1)
        hour = models.IntegerField(verbose_name="時間", validators=[MinValueValidator(0), MaxValueValidator(23),],default=0)
        minute = models.IntegerField(verbose_name="分", validators=[MinValueValidator(0), MaxValueValidator(59),],default=0)
        second = models.IntegerField(verbose_name="秒", validators=[MinValueValidator(0), MaxValueValidator(59),],default=0)

        class Meta:
                verbose_name = "1-1. 合計値/分単位"
                verbose_name_plural = '1-1. 合計値/分単位'

class ChannelDataPerMinute(models.Model):
    channel_no = models.CharField(max_length=10)
    data = models.ForeignKey(DataPerMinute, on_delete=models.CASCADE)


# 合計値/時間単位
class DataPerHour(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        month = models.IntegerField(verbose_name="月", validators=[MinValueValidator(1), MaxValueValidator(12),],default=1)
        date = models.IntegerField(verbose_name="日", validators=[MinValueValidator(1), MaxValueValidator(31),],default=1)
        hour = models.IntegerField(verbose_name="時間", validators=[MinValueValidator(0), MaxValueValidator(23),],default=0)
        minute = models.IntegerField(verbose_name="分", validators=[MinValueValidator(0), MaxValueValidator(59),],default=0)

        class Meta:
                verbose_name = "1-1. 合計値/時間単位"
                verbose_name_plural = '1-1. 合計値/時間単位'

class ChannelDataPerHour(models.Model):
    channel_no = models.CharField(max_length=10)
    data = models.ForeignKey(DataPerHour, on_delete=models.CASCADE)

# 合計値/日単位
class DataPerDate(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        month = models.IntegerField(verbose_name="月", validators=[MinValueValidator(1), MaxValueValidator(12),],default=1)
        date = models.IntegerField(verbose_name="日", validators=[MinValueValidator(1), MaxValueValidator(31),],default=1)


        class Meta:
                verbose_name = "1-2. 合計値/日単位"
                verbose_name_plural = '1-2. 合計値/日単位'

class ChannelDataPerDate(models.Model):
    channel_no = models.CharField(max_length=10)
    data = models.ForeignKey(DataPerDate, on_delete=models.CASCADE)


# 合計値/月単位
class DataPerMonth(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        month = models.IntegerField(verbose_name="月", validators=[MinValueValidator(1), MaxValueValidator(12),],default=1)


        class Meta:
                verbose_name = "1-3. 合計値/月単位"
                verbose_name_plural = '1-3. 合計値/月単位'


# 合計値/年単位
class DataPerYear(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)


        class Meta:
                verbose_name = "1-4. 合計値/年単位"
                verbose_name_plural = '1-4. 合計値/年単位'


# 設備値/時間単位
class DeviceDataPerHour(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        month = models.IntegerField(verbose_name="月", validators=[MinValueValidator(1), MaxValueValidator(12),],default=1)
        date = models.IntegerField(verbose_name="日", validators=[MinValueValidator(1), MaxValueValidator(31),],default=1)
        hour = models.IntegerField(verbose_name="時間", validators=[MinValueValidator(0), MaxValueValidator(23),],default=0)
        minute = models.IntegerField(verbose_name="分", validators=[MinValueValidator(0), MaxValueValidator(59),],default=0)
        device_id = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="設備ID")

        def __str__(self):
                return str(self.id)

        class Meta:
                verbose_name = "2-1. 設備/時間単位"
                verbose_name_plural = '2-1. 設備/時間単位'

        # 時間単位を元にDataPerData と　DeviceDataPerDate, DeviceDataPerMonth, DeviceDataPerYearに保存
        @transaction.atomic
        def save(self, *args, **kwargs):

                # 保存時に、DataPerHourにも保存する関数
                save_data(DataPerHour, self)
                # 保存時に、DataPerDateにも保存する関数
                save_data(DataPerDate, self)
                # 保存時に、DataPerMonthにも保存する関数
                save_data(DataPerMonth, self)
                # 保存時に、DataPerYearにも保存する関数
                save_data(DataPerYear, self)


                # 保存時に、DeviceDataPerDateにも保存する関数
                save_data(DeviceDataPerDate, self)
                # 保存時に、DeviceDataPerMonthにも保存する関数
                save_data(DeviceDataPerMonth, self)
                # 保存時に、DeviceDataPerYearにも保存する関数
                save_data(DeviceDataPerYear, self)


                # 以下はDeviceDataPerHourを保存する処理
                filter = {
                        'pushlog_api': self.pushlog_api,
                        'year': self.year,
                        'month': self.month,
                        'date': self.date,
                        'hour': self.hour,
                        'minute': self.minute,
                        'device_id': self.device_id,
                }
                data_model = None
                if DeviceDataPerHour.objects.filter(**filter).exists():
                        data_model = DeviceDataPerHour.objects.get(**filter)

                device_unit_price = DeviceUnitPrice.objects.filter(device=self.device_id).first()

                if device_unit_price is None:
                        logging.warn(f"device_unit_price is None device_id: {self.device_id}")
                else:
                        # valueかpriceが渡ってくる想定のため、片方の値からもう片方の値を計算する
                        # 電気は、値がkWh, 単価が円/kWh, 計算結果は小数点第2位
                        if self.electrical_value and not self.electrical_price:
                                self.electrical_price = round(float(self.electrical_value) * device_unit_price.electric_unit_price, 2)
                        elif not self.electrical_value and self.electrical_price:
                                self.electrical_value = round(self.electrical_price / device_unit_price.electric_unit_price, 2)
                        # 水は、値の単位がm3, 単価の単位が 円/m3, 計算結果は小数点第2位
                        if self.water_value and not self.water_price:
                                self.water_price = round(float(self.water_value) * device_unit_price.water_unit_price, 2)
                        elif not self.water_value and self.water_price:
                                self.water_value = round(self.water_price / device_unit_price.water_unit_price, 2)
                        # 燃料は、値の単位がm3, 単価の単位が 円/m3, 計算結果は小数点第2位
                        if self.fuel_value and not self.fuel_price:
                                self.fuel_price = round(float(self.fuel_value) * device_unit_price.fuel_unit_price, 2)
                        elif not self.fuel_value and self.fuel_price:
                                self.fuel_value = round(self.fuel_price / device_unit_price.fuel_unit_price, 2)

                        # 光熱費(電気＋水＋燃料)の計算
                        utility_costs = 0
                        utility_costs += self.electrical_price if self.electrical_price else 0
                        utility_costs += self.water_price if self.water_price else 0
                        utility_costs += self.fuel_price if self.fuel_price else 0

                        # CO2の計算
                        # 電気は、値の単位がkWh, 単価の単位が t-CO2/kWh
                        # 燃料は、値の単位がm3, 単価の単位が t-CO2/m3
                        # 水は、CO2を出さないため、0
                        # 小数点第2位への丸めは合計を求めた後で行う
                        co2_value = 0.0
                        co2_value += self.electrical_value * device_unit_price.electric_unit_co2 if self.electrical_value else 0.0
                        co2_value += self.water_value * device_unit_price.water_unit_co2 if self.water_value else 0.0
                        co2_value += self.fuel_value * device_unit_price.fuel_unit_co2 if self.fuel_value else 0.0

                        # 同一条件で保存済みのデータがあればそこに加算する
                        # 光熱費とCo2
                        if data_model is None:
                                self.utility_costs = utility_costs
                                self.co2_value = co2_value
                                self.co2_price = co2_value * device_unit_price.co2_unit_price
                        else:
                                if not data_model.utility_costs and utility_costs:
                                        self.utility_costs = utility_costs
                                elif data_model.utility_costs and utility_costs:
                                        self.utility_costs = data_model.utility_costs + utility_costs
                                if not data_model.co2_value and co2_value:
                                        self.co2_value = co2_value
                                        self.co2_price = co2_value * device_unit_price.co2_unit_price
                                elif data_model.co2_value and co2_value:
                                        self.co2_value = round(data_model.co2_value + co2_value, 2)
                                        self.co2_price = round(data_model.co2_price + co2_value * device_unit_price.co2_unit_price, 2)

                                # 電気
                                if data_model.electrical_value and self.electrical_value:
                                        self.electrical_value = round(data_model.electrical_value + self.electrical_value, 2)
                                if data_model.electrical_price and self.electrical_price:
                                        self.electrical_price = round(data_model.electrical_price + self.electrical_price, 2)

                                # 水
                                if data_model.water_value and self.water_value:
                                        self.water_value = round(data_model.water_value + self.water_value, 2)
                                if data_model.water_price and self.water_price:
                                        self.water_price = round(data_model.water_price + self.water_price, 2)

                                # 燃料
                                if data_model.fuel_value and self.fuel_value:
                                        self.fuel_value = round(data_model.fuel_value + self.fuel_value, 2)
                                if data_model.fuel_price and self.fuel_price:
                                        self.fuel_price = round(data_model.fuel_price + self.fuel_price, 2)

                        self.get_data_date = datetime.datetime(self.year, self.month, self.date, self.hour, self.minute)
                        if DeviceDataPerHour.objects.filter(**filter).exists():
                                DeviceDataPerHour.objects.filter(**filter).delete()
                        super().save(*args, **kwargs)
                        logging.info(f"DeviceDataPerHour saved. {self.id}")



# 設備値/日単位
class DeviceDataPerDate(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        month = models.IntegerField(verbose_name="月", validators=[MinValueValidator(1), MaxValueValidator(12),],default=1)
        date = models.IntegerField(verbose_name="日", validators=[MinValueValidator(1), MaxValueValidator(31),],default=1)
        device_id = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="設備ID")

        def __str__(self):
                return str(self.id)

        class Meta:
                verbose_name = "2-2. 設備/日単位"
                verbose_name_plural = '2-2. 設備/日単位'

# 設備値/月単位
class DeviceDataPerMonth(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        month = models.IntegerField(verbose_name="月", validators=[MinValueValidator(1), MaxValueValidator(12),],default=1)
        device_id = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="設備ID")

        def __str__(self):
                return str(self.id)

        class Meta:
                verbose_name = "2-3. 設備/月単位"
                verbose_name_plural = '2-3. 設備/月単位'

# 設備値/年単位
class DeviceDataPerYear(DataModel):
        year = models.IntegerField(verbose_name="年", validators=[MinValueValidator(2020), MaxValueValidator(2100),],default=2023)
        device_id = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="設備ID")

        def __str__(self):
                return str(self.id)

        class Meta:
                verbose_name = "2-4. 設備/年単位"
                verbose_name_plural = '2-4. 設備/年単位'


# Jクレジット申請
class JCreditApplication(DataModel):
        application_date = models.DateField( verbose_name="会員基本情報:入会申込日" , default="2020-4-1" ) # 2020/4/1
        member_name = models.CharField( verbose_name="会員基本情報:会員名" ,max_length=255 , default="○○温泉" ) # ○○温泉
        member_postal_code = models.CharField( verbose_name="会員基本情報:会員郵便番号(任意)" ,max_length=10 , default="000-0000" ) # 000-0000
        member_address = models.CharField( verbose_name="会員基本情報:会員住所 (任意)" ,max_length=255, default="群馬県○○市△△xx-xx" ) # 群馬県○○市△△xx-xx
        member_phone_number = models.CharField( verbose_name="会員基本情報:会員電話番号(任意)" ,max_length=20, default="xx-xxxx-1111" ) # xx-xxxx-1111
        installation_postal_code = models.CharField( verbose_name="会員基本情報:設置場所郵便番号(任意)" ,max_length=10, default="000-0000" ) # 000-0000
        installation_address = models.CharField( verbose_name="会員基本情報:設置場所住所 (必ず都道府県名から記載)" ,max_length=255, default="群馬県○○市△△xx-xx" ) # 群馬県○○市△△xx-xx
        keidanren_carbon_neutral_participation = models.BooleanField( verbose_name="会員基本情報:経団連カーボンニュートラル行動計画への参加" , default=False ) # 無
        energy_conservation_law_specified_business_number = models.CharField( verbose_name="会員基本情報:省エネ法特定事業者番号" ,max_length=255, default="11111" ) #
        global_warming_countermeasures_specified_emitter_code = models.CharField( verbose_name="会員基本情報:温対法特定排出者コード" ,max_length=255, default="00000" ) #
        base_manufacturer_name = models.CharField( verbose_name="ベースライン設備情報:メーカー名" ,max_length=255, default="〇〇工業" ) # 〇〇工業
        base_model = models.CharField( verbose_name="ベースライン設備情報:型式" ,max_length=255, default="abcde" ) # abcde
        base_quantity = models.IntegerField( verbose_name="ベースライン設備情報:台数" , default=1 ) # 1
        base_output = models.CharField( verbose_name="ベースライン設備情報:出力" , max_length=255, default="200kW" ) # 200ｋW
        base_unit_heat_gen_of_fossil_fuel_in_base_boiler = models.CharField( verbose_name="ベースライン設備情報:ベースラインのボイラーで使用する化石燃料の単位発熱量（GJ/ｔ）" ,max_length=255, default="高位発熱量基準" ) # 高位発熱量基準
        base_efficiency_percentage = models.FloatField( verbose_name="ベースライン設備情報:効率（％）" , default=89.0  ) # 89.0
        base_efficiency_of_standard_equipment_percentage = models.FloatField( verbose_name="ベースライン設備情報:標準的な設備の効率（％）" , default=90.0  ) # 90.0
        base_fuel_type = models.CharField( verbose_name="ベースライン設備情報:燃料種" ,max_length=255, default="灯油" ) # 灯油
        base_legal_service_life_years = models.IntegerField( verbose_name="ベースライン設備情報:法定耐用年数（年）" , default=15  ) # 15
        base_installation_date = models.DateField( verbose_name="ベースライン設備情報:導入日" , default="2008-6-25" ) # 2008/6/25
        base_operation_end_date = models.DateField( verbose_name="ベースライン設備情報:稼動終了日" , default="2019-7-24" ) # 2019/7/24
        base_years_of_operation = models.IntegerField( verbose_name="ベースライン設備情報:稼動年数" , default=11  ) # 11
        updated_manufacturer_name = models.CharField( verbose_name="更新後の設備情報:メーカー" ,max_length=255, default="△△機械" ) # △△機械
        updated_model = models.CharField( verbose_name="更新後の設備情報:型式" ,max_length=255, default="abcde" ) # abcde
        updated_quantity = models.IntegerField( verbose_name="更新後の設備情報:台数" , default=1 ) # 1
        updated_unique_number = models.CharField( verbose_name="更新後の設備情報:固有番号 (製造番号等)" ,max_length=255, default="abcde-12345" ) # abcde-12345
        updated_output = models.CharField( verbose_name="更新後の設備情報:出力" ,  max_length=255, default="200ｋW" ) # 200ｋW
        updated_unit_heat_gen_of_fossil_fuel_in_base_boiler = models.CharField( verbose_name="更新後の設備情報:ベースラインのボイラーで使用する化石燃料の単位発熱量（GJ/ｔ）" ,max_length=255, default="高位発熱量基準" ) # 高位発熱量基準
        updated_efficiency_percentage = models.FloatField( verbose_name="更新後の設備情報:効率（％）" , default=95.0 ) # 95.0
        updated_fuel_type = models.CharField( verbose_name="更新後の設備情報:燃料種" ,max_length=255, default="都市ガス" ) # 都市ガス
        eval_investment_recovery_years = models.FloatField( verbose_name="追加性評価:投資回収年数（年）" , default=21.7  ) # 21.7
        eval_total_investment_amount = models.FloatField( verbose_name="追加性評価:総投資額（円）" , default= 25000000  ) #  25,000,000
        eval_subsidy_amount = models.FloatField( verbose_name="追加性評価:補助金額（円）" , default= 20000000  ) #  20,000,000
        eval_net_investment_amount = models.FloatField( verbose_name="追加性評価:純投資額（円）" , default= 5000000  ) #  5,000,000
        eval_running_cost_before_implementation = models.FloatField( verbose_name="追加性評価:実施前ランニングコスト（円）" , default= 1670684  ) #  1,670,684
        eval_running_cost_after_implementation = models.FloatField( verbose_name="追加性評価:実施後ランニングコスト（円）" , default= 1440000  ) #  1,440,000
        eval_baseline_fuel_unit_price_per_month = models.FloatField( verbose_name="追加性評価:ベースライン燃料単価（円/Nm3等/月）" , default= 15000  ) #  15,000
        eval_post_implementation_fuel_unit_price_per_month = models.FloatField( verbose_name="追加性評価:ＰJ実施後燃料単価（円/Nm3等/月）" , default= 120000  ) #  120,000
        eval_existing_maintenance_cost_per_year = models.FloatField( verbose_name="追加性評価:既設メンテナンス費（円/年）" , default=10000000 ) #
        eval_post_implementation_maintenance_cost_per_year = models.FloatField( verbose_name="追加性評価:PJ実施後メンテナンス費（円/年）" , default=8000000 ) #
        eval_documentation = models.CharField( verbose_name="追加性評価:確認書類" ,max_length=255, default="補助金交付決定通知書" ) # 補助金交付決定通知書
        eval_subsidy_name = models.CharField( verbose_name="追加性評価:補助金名称" ,max_length=255, default="・・・" ) # ・・・　
        eval_granting_organization_of_subsidy = models.CharField( verbose_name="追加性評価:補助金交付団体" ,max_length=255, default="・・・" ) # ・・・
        eval_domestically_implemented_in_japan = models.BooleanField( verbose_name="追加性評価:○：環境省ではない又は補助金を利用していない。×：環境省" , default=True ) # ○
        operating_start_date = models.DateField( verbose_name="基準日:稼動開始日" , default="2020-4-1" ) # 2020/4/1
        certify_start_date = models.DateField( verbose_name="基準日:開始日" , default="2020-4-1" ) # 2020/4/1
        certify_end_date = models.DateField( verbose_name="基準日:終了日" , default="2028-3-31" ) # 2028/3/31
        requirement_implemented_in_japan = models.BooleanField( verbose_name="プロジェクト登録要件の可否:日本国内で実施される" , default=True ) # ○
        requirement_project_execution_date = models.BooleanField( verbose_name="プロジェクト登録要件の可否:プロジェクト実施日" , default=True ) # ○
        requirement_certification_start_date = models.BooleanField( verbose_name="プロジェクト登録要件の可否:認証開始日" , default=True ) # ○
        requirement_equipment_efficiency_higher_than_standard = models.BooleanField( verbose_name="プロジェクト登録要件の可否:PJ実施後設備が標準的な設備効率より良いか" , default=True ) # ○
        requirement_additivity = models.BooleanField( verbose_name="プロジェクト登録要件の可否:追加性" , default=True ) # ○
        unit_heat_gen_of_fossil_fuels_in_base_boiler = models.CharField( verbose_name=":ベースラインのボイラーで使用する化石燃料の単位発熱量（GJ/ｔ,GJ/千Nm3等）" ,max_length=255, default="38.9" ) # 38.9
        co2_per_unit_heat_ge_fuels_in_base_boiler = models.FloatField( verbose_name=":ベースラインのボイラーで使用する化石燃料の単位発熱量当たりのCO2排出係数（ｔCO2/GJ）" , default=0.0686 ) # 0.0686
        unit_heat_gen_of_fuel_used_in_boiler_after_project_exec = models.CharField( verbose_name=":プロジェクト実施後のボイラーで使用する燃料の単位発熱量（GJ/ｔ,GJ/千Nm3等）" ,max_length=255, default="45.1"  ) # 45.1
        co2_per_unit_heat_ge_fuels_used_in_boiler_after_exec = models.FloatField( verbose_name=":プロジェクト実施後のボイラーで使用する化石燃料の単位発熱量当たりのCO2排出係数（ｔCO2/GJ）" , default=0.0513  ) # 0.0513
        monitoring_period_in_months = models.FloatField( verbose_name="モニタリング測定結果:モニタリング期間（ヶ月）" , default=12.0000  ) # 12.0000
        monitoring_measurement_value_of_fuel_consumption = models.CharField( verbose_name="モニタリング測定結果:モニタリング測定値（燃料使用量）（t、kl、千Nm3）" ,max_length=255, default="100.0"  ) # 100.0
        monitoring_classification = models.CharField( verbose_name="モニタリング測定結果:分類" ,max_length=255, default="分類C：概算" ) # 分類C：概算
        monitoring_measurement_error_rate_in_c = models.CharField( verbose_name="モニタリング測定結果:分類Cにおいて計量器を用いた場合の誤差率（%）" ,max_length=255, default="10.0"  ) # 10.0
        monitoring_final_value = models.CharField( verbose_name="モニタリング測定結果:最終的なモニタリング値" ,max_length=255, default="90.0"  ) # 90.0

        created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
        updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

        def __str__(self):
                return str(self.member_phone_number)

        class Meta:
                verbose_name = "Jクレジット申請"
                verbose_name_plural = "Jクレジット申請"

class DeviceUnitPrice(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, verbose_name="デバイス")
    electric_unit_price = models.FloatField(default=0, verbose_name="電気(円/kWh)")
    water_unit_price = models.FloatField(default=0, verbose_name="水(円/m3)")
    fuel_unit_price = models.FloatField(default=0, verbose_name="燃料(円/m3)")
    co2_unit_price = models.FloatField(default=0, verbose_name="CO2(円/t-CO2)")

    electric_unit_co2 = models.FloatField(default=0, verbose_name="電気(t-CO2/kWh)")
    water_unit_co2 = models.FloatField(default=0, verbose_name="水(t-CO2/m3)")
    fuel_unit_co2 = models.FloatField(default=0, verbose_name="燃料(t-CO2/m3)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "m.単価情報"
        verbose_name_plural = 'm.単価情報'

class MonthlyCostTarget(models.Model):
    class TargetType(models.TextChoices):
        ELECTRIC = 'electric', '電気'
        WATER = 'water', '水'
        FUEL = 'fuel', '燃料'
        CO2 = 'co2', 'CO2'

    user_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, verbose_name="ユーザーID")
    company = models.ForeignKey(Company, null=True, on_delete=models.CASCADE, verbose_name="企業ID")
    year = models.IntegerField(verbose_name="年")
    month = models.IntegerField(verbose_name="月")
    target_type = models.CharField(max_length=10, choices=TargetType.choices, verbose_name="目標タイプ")
    target_value = models.FloatField(verbose_name="目標値")
    target_price = models.IntegerField(verbose_name="目標金額")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "月次目標"
        verbose_name_plural = "月次目標"
        unique_together = ("company", "year", "month", "target_type")

    def clean(self):
        if self.year < 0:
            raise ValidationError("年は0以上で入力してください。")

        if self.month < 1 or self.month > 12:
            raise ValidationError("月は1から12の範囲で入力してください。")

class Gateway(models.Model):
    id = models.CharField(max_length=50, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=50)
    is_activated = models.BooleanField(default=False)
    firmware_version = models.CharField(max_length=50)
    pushlog_api = models.ForeignKey('PushLogApi', on_delete=models.CASCADE, null=True, blank=True, verbose_name="PushLog API")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "m.エッジデバイス(ゲートウェイ)"
        verbose_name_plural = "m.エッジデバイス(ゲートウェイ)"

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=100)
    environmental_type_id = models.ForeignKey(EnvironmentalType, on_delete=models.CASCADE, verbose_name="環境タイプID", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "m.単位"
        verbose_name_plural = "m.単位"

    def __str__(self):
        return f'{self.name} ({self.environmental_type_id.name if self.environmental_type_id else "null"})'

class EconomicActivityUnit(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "m.経済活動量単位"
        verbose_name_plural = "m.経済活動量単位"

    def __str__(self):
        return self.name

class EconomicActivityType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE, verbose_name="ユーザーID")
    company = models.ForeignKey(Company, null=True, on_delete=models.CASCADE, verbose_name="会社ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "m.経済活動量種別"
        verbose_name_plural = "m.経済活動量種別"

    def __str__(self):
        return self.name

class LiquidType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "m.燃料種類"
        verbose_name_plural = "m.燃料種類"

    def __str__(self):
        return self.name

class DailyEconomicActivityAmount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    activity_type_id = models.ForeignKey(EconomicActivityType, null=True, blank=True, on_delete=models.CASCADE, verbose_name="経済活動量種別ID")
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, verbose_name="会社ID")
    value = models.IntegerField(verbose_name="活動量")
    activity_date = models.DateField(verbose_name="活動日")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "経済活動量"
        verbose_name_plural = "経済活動量"
        unique_together = [['activity_type_id', 'activity_date']]

    def __str__(self):
        return f'{self.company} ({self.activity_date})'


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

class PushLogApi(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    # company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="会社ID")
    key = EncryptedCharField(max_length=512, unique=True, blank=True, null=True)
    hashed_key = models.CharField(max_length=512, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "m.APIキー"
        verbose_name_plural = "m.APIキー"

    def __str__(self):
        return f'{self.id}'

    def save(self, *args, **kwargs):
        # keyが設定されている場合、そのハッシュ値をhashed_keyに保存
        if self.key:
            pepper = settings.ENCRYPTION_KEY
            hashed_key = hashlib.sha256((self.key + pepper).encode()).hexdigest()
            self.hashed_key = hashed_key
        elif self.key is None:
            self.hashed_key = None

        super().save(*args, **kwargs)

class Entity(models.Model):
    class Meta:
        verbose_name = "エンティティ"
        verbose_name_plural = "エンティティ"

    def __str__(self):
        return self.name

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100, verbose_name="名称")
    # 初期登録時には、CompanyはNull、GatewayRegistrationに設定する際に、Companyも付与
    # この方式では、企業が変わった場合に、データを削除する必要がある
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, verbose_name="会社ID", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

class DataType(models.Model):
    class Meta:
        verbose_name = "データタイプ"
        verbose_name_plural = "データタイプ"

    def __str__(self):
        return self.name

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100, verbose_name="名称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

class Data(models.Model):
    class Meta:
        verbose_name = "データ"
        verbose_name_plural = "データ"

    def __str__(self):
        return f'{self.date_type}, {self.data_type.name if self.data_type else "_"}, {self.entity.name}, {self.get_data_at}'

    class DateType(models.TextChoices):
        YEAR = 'year', '年'
        MONTH = 'month', '月'
        DATE = 'date', '日'
        HOUR = 'hour', '時間'
        MINUTE = 'minute', '分'

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    date_type = models.CharField(max_length=10, choices=DateType.choices, verbose_name="日付タイプ")
    value = models.FloatField(verbose_name="値", validators=[MinValueValidator(0),], blank=True, null=True,)
    price = models.FloatField(verbose_name="金額", validators=[MinValueValidator(0),], blank=True, null=True,)
    data_type = models.ForeignKey(DataType, on_delete=models.CASCADE, verbose_name="データタイプID", null=True, blank=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, verbose_name="エンティティID")
    get_data_at = models.DateTimeField(verbose_name="取得日時", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    @classmethod
    def save_all_hierarchical_data(cls, **kwargs):
        cls.save_all_type_data(**kwargs)
        entity = kwargs.pop("entity")
        ancestor_entities = map(
            lambda d: d.ancestor,
            DataStructure.objects.filter(descendant=entity).exclude(ancestor=entity),
        )
        for e in ancestor_entities:
            cls.save_all_type_data(entity=e, **kwargs)

    @classmethod
    def save_minute_hierarchical_data(cls, **kwargs):
        kwargs.pop('date_type', None)
        cls.save_data(cls.DateType.MINUTE, **kwargs)
        entity = kwargs.pop("entity")
        ancestor_entities = map(
            lambda d: d.ancestor,
            DataStructure.objects.filter(descendant=entity).exclude(ancestor=entity),
        )
        for e in ancestor_entities:
            cls.save_data(cls.DateType.MINUTE, entity=e, **kwargs)

    @classmethod
    def save_all_type_data(cls, **kwargs):
        kwargs.pop('date_type', None)
        cls.save_data(cls.DateType.HOUR, **kwargs)
        cls.save_data(cls.DateType.DATE, **kwargs)
        cls.save_data(cls.DateType.MONTH, **kwargs)
        cls.save_data(cls.DateType.YEAR, **kwargs)

    @classmethod
    def save_data(cls, date_type, **kwargs):
        device = kwargs.pop('device', None)
        instance = cls(**kwargs)
        instance.date_type = date_type
        # # if instance.data_type.name == DATA_TYPE_CO2:
        # if instance.data_type is None or instance.data_type.name != DATA_TYPE_ELECTRICITY:
        #     instance.save()
        #     return
        if device is None:
            # 例外を投げる
            raise Exception('CO2以外のDataのsaveにはdeviceが必須です')

        instance.date_type = date_type
        existing_instance = None
        round_no = 10
        if instance.date_type == instance.DateType.YEAR:
            existing_instance = Data.objects.filter(
                date_type = instance.date_type,
                data_type = instance.data_type,
                entity = instance.entity,
                get_data_at__year = instance.get_data_at.year,
            ).first()
        elif instance.date_type == instance.DateType.MONTH:
            existing_instance = Data.objects.filter(
                    date_type = instance.date_type,
                    data_type = instance.data_type,
                    entity = instance.entity,
                    get_data_at__year = instance.get_data_at.year,
                    get_data_at__month = instance.get_data_at.month,
            ).first()
        elif instance.date_type == instance.DateType.DATE:
            existing_instance = Data.objects.filter(
                    date_type = instance.date_type,
                    data_type = instance.data_type,
                    entity = instance.entity,
                    get_data_at__year = instance.get_data_at.year,
                    get_data_at__month = instance.get_data_at.month,
                    get_data_at__day = instance.get_data_at.day,
            ).first()
        elif instance.date_type == instance.DateType.HOUR:
            existing_instance = Data.objects.filter(
                    date_type = instance.date_type,
                    data_type = instance.data_type,
                    entity = instance.entity,
                    get_data_at__year = instance.get_data_at.year,
                    get_data_at__month = instance.get_data_at.month,
                    get_data_at__day = instance.get_data_at.day,
                    get_data_at__hour = instance.get_data_at.hour,
                    get_data_at__minute = instance.get_data_at.minute,
            ).first()
        elif instance.date_type == instance.DateType.MINUTE:
            existing_instance = Data.objects.filter(
                    date_type = instance.date_type,
                    data_type = instance.data_type,
                    entity = instance.entity,
                    get_data_at__year = instance.get_data_at.year,
                    get_data_at__month = instance.get_data_at.month,
                    get_data_at__day = instance.get_data_at.day,
                    get_data_at__hour = instance.get_data_at.hour,
                    get_data_at__minute = instance.get_data_at.minute,
                    get_data_at__second = instance.get_data_at.second,
            ).first()
            round_no = 12
        if existing_instance is not None and instance.date_type == instance.DateType.HOUR and device.entity.id == instance.entity.id:
            raise Exception('同一日時のデータが既に存在します')
        elif existing_instance is not None and instance.date_type == instance.DateType.MINUTE and device.entity.id == instance.entity.id:
            raise Exception('同一日時分秒のデータが既に存在します')

        # device_unit_price = DeviceUnitPrice.objects.filter(
        #     device_id=device.id
        # ).first()
        # if device_unit_price is None:
        #     logging.warn(f"device_unit_price is None device_id: {device.id}")
        # else:
        #     # valueかpriceが渡ってくる想定のため、片方の値からもう片方の値を計算する
        #     if instance.data_type.name == DATA_TYPE_ELECTRICITY:
        #         # 電気は、値がkWh, 単価が円/kWh, 計算結果は小数点第2位まで
        #         if instance.value and not instance.price:
        #             instance.price = round(
        #                 float(instance.value) * device_unit_price.electric_unit_price, round_no
        #             )
        #         elif not instance.value and instance.price:
        #             instance.value = round(
        #                 instance.price / device_unit_price.electric_unit_price, round_no
        #             )
        #         elif instance.value == 0:
        #             instance.price = 0
        #     elif instance.data_type.name == DATA_TYPE_WATER:
        #         # 水は、値の単位がm3, 単価の単位が 円/m3, 計算結果は小数点第2位
        #         if instance.value and not instance.price:
        #             instance.price = round(
        #                 float(instance.value) * device_unit_price.water_unit_price, round_no
        #             )
        #         elif not instance.value and instance.price:
        #             instance.value = round(
        #                 instance.price / device_unit_price.water_unit_price, round_no
        #             )
        #         elif instance.value == 0:
        #             instance.price = 0
        #     elif instance.data_type.name == DATA_TYPE_FUEL:
        #         # 燃料は、値の単位がm3, 単価の単位が 円/m3, 計算結果は小数点第2位
        #         if instance.value and not instance.price:
        #             instance.price = round(
        #                 float(instance.value) * device_unit_price.fuel_unit_price, round_no
        #             )
        #         elif not instance.value and instance.price:
        #             instance.value = round(
        #                 instance.price / device_unit_price.fuel_unit_price, round_no
        #             )
        #         elif instance.value == 0:
        #             instance.price = 0

        #     # CO2の計算
        #     # 電気は、値の単位がkWh, CO2の単位が t-CO2/kWh
        #     # 燃料は、値の単位がm3, CO2の単位が t-CO2/m3
        #     # 水は、CO2を出さないため、0
        #     co2_value = 0.0
        #     if instance.data_type.name == DATA_TYPE_ELECTRICITY and instance.value is not None:
        #         co2_value = instance.value * device_unit_price.electric_unit_co2
        #     elif instance.data_type.name == DATA_TYPE_WATER and instance.value is not None:
        #         co2_value = instance.value * device_unit_price.water_unit_co2
        #     elif instance.data_type.name == DATA_TYPE_FUEL and instance.value is not None:
        #         co2_value = instance.value * device_unit_price.fuel_unit_co2
        #     # 同一条件で保存済みのデータがあればそこに加算する
        #     # 光熱費とCo2

        # # NOTE: utility_costsはデータ構造の変更時に削除したが、必要なら以下を参考に実装する
        # #     if not data_model.utility_costs and utility_costs:
        # #         data_model.utility_costs = utility_costs
        # #     elif data_model.utility_costs and utility_costs:
        # #         data_model.utility_costs = data_model.utility_costs + utility_costs

        #     # Co2の対応
        #     co2_data_type = DataType.objects.filter(name=DATA_TYPE_CO2).first()
        #     if co2_data_type is None:
        #         raise Exception('DataTypeにCO2が登録されていません')
        #     co2_existing_instance = None
        #     if instance.date_type == instance.DateType.YEAR:
        #         co2_existing_instance = Data.objects.filter(
        #                 date_type = instance.date_type,
        #                 data_type = co2_data_type,
        #                 entity = instance.entity,
        #                 get_data_at__year = instance.get_data_at.year,
        #         ).first()
        #     elif instance.date_type == instance.DateType.MONTH:
        #         co2_existing_instance = Data.objects.filter(
        #                 date_type = instance.date_type,
        #                 data_type = co2_data_type,
        #                 entity = instance.entity,
        #                 get_data_at__year = instance.get_data_at.year,
        #                 get_data_at__month = instance.get_data_at.month,
        #         ).first()
        #     elif instance.date_type == instance.DateType.DATE:
        #         co2_existing_instance = Data.objects.filter(
        #                 date_type = instance.date_type,
        #                 data_type = co2_data_type,
        #                 entity = instance.entity,
        #                 get_data_at__year = instance.get_data_at.year,
        #                 get_data_at__month = instance.get_data_at.month,
        #                 get_data_at__day = instance.get_data_at.day,
        #         ).first()
        #     elif instance.date_type == instance.DateType.HOUR:
        #         co2_existing_instance = Data.objects.filter(
        #                 date_type = instance.date_type,
        #                 data_type = co2_data_type,
        #                 entity = instance.entity,
        #                 get_data_at__year = instance.get_data_at.year,
        #                 get_data_at__month = instance.get_data_at.month,
        #                 get_data_at__day = instance.get_data_at.day,
        #                 get_data_at__hour = instance.get_data_at.hour,
        #                 get_data_at__minute = instance.get_data_at.minute,
        #         ).first()
        #     elif instance.date_type == instance.DateType.MINUTE:
        #         co2_existing_instance = Data.objects.filter(
        #                 date_type = instance.date_type,
        #                 data_type = co2_data_type,
        #                 entity = instance.entity,
        #                 get_data_at__year = instance.get_data_at.year,
        #                 get_data_at__month = instance.get_data_at.month,
        #                 get_data_at__day = instance.get_data_at.day,
        #                 get_data_at__hour = instance.get_data_at.hour,
        #                 get_data_at__minute = instance.get_data_at.minute,
        #                 get_data_at__second = instance.get_data_at.second,
        #         ).first()
        #     if co2_existing_instance is not None and instance.date_type == instance.DateType.HOUR and device.entity.id == instance.entity.id:
        #         raise Exception('同一日時のCO2データが既に存在します')
        #     elif existing_instance is not None and instance.date_type == instance.DateType.MINUTE and device.entity.id == instance.entity.id:
        #         raise Exception('同一日時分秒のデータが既に存在します')

        #     if co2_existing_instance is None:
        #         cls.save_data(
        #             date_type = instance.date_type,
        #             data_type = co2_data_type,
        #             entity = instance.entity,
        #             get_data_at = instance.get_data_at,
        #             value = co2_value,
        #             price = co2_value * device_unit_price.co2_unit_price,
        #         ) if co2_value else None
        #     else:
        #         if not co2_existing_instance.value and co2_value:
        #             co2_existing_instance.value = co2_value
        #         elif co2_existing_instance.value and co2_value:
        #             co2_existing_instance.value = round(co2_existing_instance.value + co2_value, round_no)

        #         if not co2_existing_instance.price and co2_value:
        #             co2_existing_instance.price = co2_value * device_unit_price.co2_unit_price
        #         elif co2_existing_instance.price and co2_value:
        #             co2_existing_instance.price = round(
        #                 co2_existing_instance.price + co2_value * device_unit_price.co2_unit_price,
        #                 round_no,
        #             )
        #         co2_existing_instance.get_data_at = instance.get_data_at
        #         co2_existing_instance.save() if co2_value else None

        #     if existing_instance is None:
        #         instance.save()
        #         return

        #     if not existing_instance.value and instance.value:
        #         existing_instance.value = instance.value
        #     elif existing_instance.value and instance.value:
        #         existing_instance.value = round(existing_instance.value + instance.value, round_no)

        #     if not existing_instance.price and instance.price:
        #         existing_instance.price = instance.price
        #     elif existing_instance.price and instance.price:
        #         existing_instance.price = round(existing_instance.price + instance.price, round_no)

        #     existing_instance.get_data_at = instance.get_data_at
        #     existing_instance.save()

        if existing_instance is None:
            instance.save()
            return

        if not existing_instance.value and instance.value:
            existing_instance.value = instance.value
        elif existing_instance.value and instance.value:
            existing_instance.value = round(existing_instance.value + instance.value, round_no)

        if not existing_instance.price and instance.price:
            existing_instance.price = instance.price
        elif existing_instance.price and instance.price:
            existing_instance.price = round(existing_instance.price + instance.price, round_no)

        existing_instance.get_data_at = instance.get_data_at
        existing_instance.save()


    # @classmethod
    # # 分単位のデータを保存する
    # # 取得した数値をそのまま保存する
    # # 単位変換や金額計算、CO2計算は行わない
    # def save_data_minute(cls, **kwargs):
    #     device = kwargs.pop('device', None)
    #     instance = cls(**kwargs)
    #     if device is None:
    #         # 例外を投げる
    #         raise Exception('CO2以外のDataのsaveにはdeviceが必須です')

    #     existing_instance = None
    #     if instance.date_type == instance.DateType.MINUTE:
    #         existing_instance = Data.objects.filter(
    #                 date_type = instance.date_type,
    #                 data_type = instance.data_type,
    #                 entity = instance.entity,
    #                 get_data_at__year = instance.get_data_at.year,
    #                 get_data_at__month = instance.get_data_at.month,
    #                 get_data_at__day = instance.get_data_at.day,
    #                 get_data_at__hour = instance.get_data_at.hour,
    #                 get_data_at__minute = instance.get_data_at.minute,
    #         ).first()
    #         if existing_instance is not None and device.entity.id == instance.entity.id:
    #             raise Exception('同一日時のデータが既に存在します')

    #         if existing_instance is None:
    #             instance.save()
    #             return


    # データ削除の際に関連するオブジェクトの数値を調整（減算）するためのクラスメソッド
    # 与えられたオブジェクトから取得した値を、関連オブジェクトから減算する
    @classmethod
    def sub_all_hierarchical_data(cls, instance):
        # 時間情報に関して上位を辿る：時→日→月→年
        cls.sub_all_type_data(instance.entity, instance)

        # # entityを全て取得
        # entity = instance.entity
        # ancestor_entities = map(
        #     lambda d: d.ancestor,
        #     DataStructure.objects.filter(descendant=entity).exclude(ancestor=entity),
        # )
        # # 全ての上位entityに対して、時間を辿って削除する
        # for e in ancestor_entities:
        #     cls.sub_all_type_data(e, instance)

    @classmethod
    # 時間を辿る：時→日→月→年
    def sub_all_type_data(cls, entity, instance):
        if instance.date_type == cls.DateType.HOUR:
            cls.sub_data(cls.DateType.DATE, entity, instance)
            cls.sub_data(cls.DateType.MONTH, entity, instance)
            cls.sub_data(cls.DateType.YEAR, entity, instance)
        elif instance.date_type == cls.DateType.DATE:
            cls.sub_data(cls.DateType.MONTH, entity, instance)
            cls.sub_data(cls.DateType.YEAR, entity, instance)
        elif instance.date_type == cls.DateType.MONTH:
            cls.sub_data(cls.DateType.YEAR, entity, instance)

    @classmethod
    # 減算処理の実体
    def sub_data(cls, date_type, entity, instance):
        # まずは、減算対象のデータを取得する
        existing_instance = None
        if date_type == instance.DateType.YEAR:
            existing_instance = Data.objects.filter(
                date_type = date_type,
                data_type = instance.data_type,
                entity = entity,
                get_data_at__year = instance.get_data_at.year,
            ).first()
        elif date_type == instance.DateType.MONTH:
            existing_instance = Data.objects.filter(
                    date_type = date_type,
                    data_type = instance.data_type,
                    entity = entity,
                    get_data_at__year = instance.get_data_at.year,
                    get_data_at__month = instance.get_data_at.month,
            ).first()
        elif date_type == instance.DateType.DATE:
            existing_instance = Data.objects.filter(
                    date_type = date_type,
                    data_type = instance.data_type,
                    entity = entity,
                    get_data_at__year = instance.get_data_at.year,
                    get_data_at__month = instance.get_data_at.month,
                    get_data_at__day = instance.get_data_at.day,
            ).first()

        # 減算する。減算対象がない場合は、何もしない
        if existing_instance is not None:
            if not existing_instance.value and instance.value:
                existing_instance.value = 0
            elif existing_instance.value and instance.value:
                val = round(existing_instance.value - instance.value, 2)
                existing_instance.value = val if val > 0.0 else 0.0

            if not existing_instance.price and instance.price:
                existing_instance.price = 0
            elif existing_instance.price and instance.price:
                val = round(existing_instance.price - instance.price, 2)
                existing_instance.price = val if val > 0.0 else 0.0

            existing_instance.save()
    # 削除用のクラスメソッド：ここまで



class DataStructure(models.Model):
    class Meta:
        verbose_name = "データ構造"
        verbose_name_plural = "データ構造"

    def __str__(self):
        return f'{self.ancestor} <- {self.descendant} ({self.depth})'

    ancestor = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='ancestor', verbose_name="先祖エンティティID")
    descendant = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='descendant', verbose_name="子孫エンティティID")
    depth = models.IntegerField(verbose_name="先祖から子孫までの深さ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")


# # 標準単価の項目設定
# # PRICE_TYPE_YEN_ELECTRICITY = ("電気", "円/kWh")
# # PRICE_TYPE_YEN_WATER = ("水", "円/m3")
# # PRICE_TYPE_YEN_FUEL = ("燃料", "円/m3")
# # PRICE_TYPE_YEN_CO2 = ("CO2", "円/t-CO2")
# # PRICE_TYPE_CO2_ELECTRICITY = ("電気", "t-CO2/kWh")
# # PRICE_TYPE_CO2_FUEL = ("燃料", "t-CO2/m3")
# class PriceType(models.Model):
#     class Meta:
#         verbose_name = "m.単価タイプ"
#         verbose_name_plural = "m.単価タイプ"

#     def __str__(self):
#         return self.type+f"({self.unit})"

#     id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
#     type = models.CharField(max_length=20, verbose_name="名称", choices=[(tag,tag) for tag in ("電気", "水", "燃料", "CO2")])
#     unit = models.CharField(max_length=20, verbose_name="単位", choices=[(tag,tag) for tag in ("円/kWh", "円/m3", "円/t-CO2", "t-CO2/kWh", "t-CO2/m3")])
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")


# 単価変更履歴
class UnitPriceHistory(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    field = models.CharField(max_length=30, verbose_name="フィールド名", default="")
    # name = models.ForeignKey(PriceType, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, verbose_name="名前")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="会社ID")
    before = models.FloatField(verbose_name="変更前の値")
    after = models.FloatField(verbose_name="変更後の値")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="変更日時")

    class Meta:
        verbose_name = "m.単価変更履歴"
        verbose_name_plural = "m.単価変更履歴"

    def __str__(self):
        return str(self.name)

class UserEntityPermission(models.Model):
    class Meta:
        verbose_name = "ユーザーエンティティ権限"
        verbose_name_plural = "ユーザーエンティティ権限"
        unique_together = ('user', 'entity')

    def __str__(self):
        return f'{self.user} - {self.entity}'

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザーID")
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, verbose_name="エンティティID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

# チャンネル接続器＝Gateway＋CH
class ChannelAdapter(models.Model):
    class Meta:
        verbose_name = "グラフ接続情報"
        verbose_name_plural = "グラフ接続情報"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="企業")
    # entity_id = models.ForeignKey(Entity, null=True, on_delete=models.SET_NULL, verbose_name="CHエンティティ")

    channel_no = models.IntegerField(default=0, verbose_name="グラフ番号")
    channel_name = models.CharField(max_length=30, verbose_name="グラフ名", null=True, blank=True)

    device_number = models.ForeignKey(Device, on_delete=models.SET_NULL, verbose_name="デバイス型番", null=True, blank=True)

    equation_str = models.CharField(max_length=30, verbose_name="計算式")
    utility_cost_price = models.FloatField(default=0, verbose_name="光熱費単価")
    co2_emissions_current = models.FloatField(default=0, verbose_name="CO2排出量:現状")
    co2_emissions_baseline = models.FloatField(default=0, verbose_name="CO2排出量:再エネのベースライン", null=True, blank=True)
    co2_emissions_improvement_rate = models.FloatField(default=0, verbose_name="CO2排出量:対ベースライン改善割合", null=True, blank=True)

    is_co2_emissions_baseline = models.BooleanField(default=True, verbose_name="CO2排出量:再エネのベースラインを使用するか")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.channel_no} {self.channel_name}: {self.company_id} {self.device_number}'

def get_current_date():
    return timezone.now().date()

# ユーザー画面でのGatewayへの利用開始日への設定
class GatewayStartdate(models.Model):
    class Meta:
        verbose_name = "ゲートウェイの利用開始日"
        verbose_name_plural = "ゲートウェイの利用開始日"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="企業")
    gateway_id = models.ForeignKey(Gateway, null=True, on_delete=models.CASCADE, verbose_name="ゲートウェイ")

    started_at = models.DateField(default=get_current_date, verbose_name="利用開始日")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.company_id} ({self.gateway_id})'

# ユーザー画面での年間計画値の設定
class AnnualPlanValues(models.Model):
    class Meta:
        verbose_name = "年間計画値"
        verbose_name_plural = "年間計画値"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company_id = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name="企業")

    utility_cost = models.FloatField(default=0.0, verbose_name="光熱費（円）")
    utility_cost_reduce = models.FloatField(default=0.0, verbose_name="光熱費削減量（円）")
    electric = models.FloatField(default=0.0, verbose_name="電力量（kWh）")
    electric_reduce = models.FloatField(default=0.0, verbose_name="電力削減量（kWh）")
    co2_emissions = models.FloatField(default=0.0, verbose_name="CO2排出量（t-CO2）")
    co2_emissions_reduce = models.FloatField(default=0.0, verbose_name="CO2削減量（t-CO2）")
    carbon_credit = models.FloatField(default=0.0, verbose_name="カーボンクレジット料（円）")
    carbon_credit_price = models.FloatField(default=0.0, verbose_name="カーボンクレジット価格（円/t-CO2）")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.company_id} (CO2: {self.carbon_credit}, {self.carbon_credit_price})'

# 登録上限数一覧（ユーザー、ゲートウェイ）
class RegisteredLimit(models.Model):
    class Meta:
        verbose_name = "登録数上限一覧"
        verbose_name_plural = "登録上限数一覧"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company_id = models.OneToOneField(Company, on_delete=models.CASCADE, verbose_name="企業")

    user_limit = models.IntegerField(default=0, verbose_name="ユーザー登録上限数")
    gateway_limit = models.IntegerField(default=0, verbose_name="ゲートウェイ登録上限数")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.company_id} (ユーザー上限数: {self.user_limit}, ゲートウェイ上限数: {self.gateway_limit})'

# ゲートウェイマスタ：PushlogApiKeyに紐づく全てのGateway
# PushlogApiKeyの設定に基づいて登録される→管理画面での登録
class GatewayMaster(models.Model):
    class Meta:
        verbose_name = "ゲートウェイマスタ"
        verbose_name_plural = "ゲートウェイマスタ"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    gateway_type = models.CharField(max_length=30, verbose_name="ゲートウェイ種別") # PUSHLOG
    gateway_id = models.OneToOneField(Gateway, on_delete=models.CASCADE, verbose_name="ゲートウェイ")

    connected = models.BooleanField(default=False, verbose_name="接続状態")

    license_type = models.CharField(max_length=30, verbose_name="ライセンス種別", null=True, blank=True)
    license_limit = models.DateField(verbose_name="利用可能期限", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.gateway_id} ({self.license_type}:{self.license_limit})'

# ゲートウェイ追加画面：ゲートウェイ一覧：CompanyのUser管理者が登録したもの
#   ゲートウェイと企業の紐付けはここで行われる。PushlogApiKeyでの紐付けは無くなった。
#   企業に登録する際に名前（別名）がつけられる。企業が管理しやすい名前をつける。
class GatewayRegistration(models.Model):
    class Meta:
        verbose_name = "ゲートウェイ登録情報"
        verbose_name_plural = "ゲートウェイ登録情報"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="企業")
    alt_name = models.CharField(max_length=100, verbose_name="ゲートウェイ名:企業に紐付け", null=True, blank=True)
    gateway_master = models.OneToOneField(GatewayMaster, on_delete=models.CASCADE, verbose_name="ゲートウェイマスタ")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.company_id} ({self.gateway_master.gateway_id.name})'


class CarbonFootprint(models.Model):
    class Meta:
        verbose_name = "カーボンフットプリント"
        verbose_name_plural = "カーボンフットプリント"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="企業")

    process_name = models.CharField(max_length=100, verbose_name="工程名", default="工程")
    channel_name = models.CharField(max_length=100, verbose_name="チャンネル名")
    start_date = models.DateTimeField(verbose_name="取得開始日時", null=True, blank=True)
    end_date = models.DateTimeField(verbose_name="取得終了日時", null=True, blank=True)
    electric_value = models.FloatField(default=0.0, verbose_name="電力量")
    co2_emissions = models.FloatField(default=0.0, verbose_name="CO2排出量")
    scope_no = models.IntegerField(default=1, verbose_name="Scope区分")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.company_id} ({self.process_name})'

class Co2EmissionsFactor(models.Model):
    class Meta:
        verbose_name = "CO2排出係数"
        verbose_name_plural = "CO2排出係数"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=30, verbose_name="名前")
    no = models.IntegerField(default=0, verbose_name="番号")
    factor = models.FloatField(default=0.0, verbose_name="係数")
    region_name = models.CharField(max_length=30, verbose_name="地名", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f'{self.no} : {self.name} ({self.factor})'

class CsvUploadHistory(models.Model):
    class Meta:
        verbose_name = "CSVアップロード履歴"
        verbose_name_plural = "CSVアップロード履歴"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="企業")
    file_name = models.CharField(max_length=255, verbose_name="ファイル名")
    size_bytes = models.PositiveBigIntegerField(verbose_name="ファイルサイズ（バイト）")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="アップロード日時")

    def __str__(self):
        return f"{self.file_name} ({self.size_bytes} bytes)"
# main/models.py
from django.db import models
from django.contrib.auth.models import User

class HouseInfo(models.Model):
    """Полная информация о доме (автоматически из DaData)"""
    
    # === Базовые поля (заполняются автоматически) ===
    address_full = models.CharField(max_length=300, verbose_name='Полный адрес')
    address_source = models.CharField(max_length=300, blank=True, verbose_name='Исходный адрес')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='Индекс')
    country = models.CharField(max_length=50, blank=True, verbose_name='Страна')
    federal_district = models.CharField(max_length=50, blank=True, verbose_name='Федеральный округ')
    timezone = models.CharField(max_length=20, blank=True, verbose_name='Часовой пояс')
    
    # === Регион ===
    region = models.CharField(max_length=100, blank=True, verbose_name='Регион')
    region_type = models.CharField(max_length=20, blank=True, verbose_name='Тип региона')
    area = models.CharField(max_length=100, blank=True, verbose_name='Район')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    city_district = models.CharField(max_length=100, blank=True, verbose_name='Район города')
    settlement = models.CharField(max_length=100, blank=True, verbose_name='Населенный пункт')
    
    # === Улица ===
    street = models.CharField(max_length=150, blank=True, verbose_name='Улица')
    street_type = models.CharField(max_length=20, blank=True, verbose_name='Тип улицы')
    
    # === Дом ===
    house = models.CharField(max_length=20, blank=True, verbose_name='Номер дома')
    house_type = models.CharField(max_length=20, blank=True, verbose_name='Тип дома')
    block = models.CharField(max_length=20, blank=True, verbose_name='Корпус/строение')
    flat = models.CharField(max_length=20, blank=True, verbose_name='Квартира')
    flat_area = models.FloatField(null=True, blank=True, verbose_name='Площадь квартиры (м²)')
    
    # === Характеристики дома ===
    building_year = models.IntegerField(null=True, blank=True, verbose_name='Год постройки')
    floors = models.IntegerField(null=True, blank=True, verbose_name='Количество этажей')
    flat_count = models.IntegerField(null=True, blank=True, verbose_name='Количество квартир')
    material = models.CharField(max_length=50, blank=True, verbose_name='Материал стен')
    cadastral_number = models.CharField(max_length=100, blank=True, verbose_name='Кадастровый номер')
    
    # === Цены ===
    flat_price = models.BigIntegerField(null=True, blank=True, verbose_name='Цена квартиры (руб)')
    square_meter_price = models.IntegerField(null=True, blank=True, verbose_name='Цена за м² (руб)')
    
    # === Координаты ===
    geo_lat = models.FloatField(null=True, blank=True, verbose_name='Широта')
    geo_lon = models.FloatField(null=True, blank=True, verbose_name='Долгота')
    geo_quality = models.IntegerField(null=True, blank=True, verbose_name='Качество геокодирования')
    
    # === Метро ===
    metro = models.JSONField(default=dict, blank=True, verbose_name='Ближайшее метро')
    
    # === Идентификаторы ФИАС ===
    fias_id = models.CharField(max_length=50, blank=True, verbose_name='ФИАС-код')
    house_fias_id = models.CharField(max_length=50, blank=True, verbose_name='ФИАС-код дома')
    street_fias_id = models.CharField(max_length=50, blank=True, verbose_name='ФИАС-код улицы')
    
    # === Статус проверки ===
    qc = models.IntegerField(null=True, blank=True, verbose_name='Код проверки')
    qc_geo = models.IntegerField(null=True, blank=True, verbose_name='Код проверки координат')
    
    # === Поля, заполняемые вручную (нет в открытом API) ===
    managing_company = models.CharField(max_length=200, blank=True, verbose_name='Управляющая компания')
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон аварийной службы')
    entrances = models.IntegerField(null=True, blank=True, verbose_name='Количество подъездов')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Информация о доме'
        verbose_name_plural = 'Информация о домах'
    
    def __str__(self):
        return self.address_full

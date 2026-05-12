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


class Profile(models.Model):
    """Профиль жильца"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    apartment_number = models.CharField(max_length=10, verbose_name='Номер квартиры')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    personal_account = models.CharField(max_length=20, blank=True, verbose_name='Лицевой счет')
    house = models.ForeignKey(HouseInfo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Информация о доме')
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - кв.{self.apartment_number}"
    
    class Meta:
        verbose_name = 'Профиль жильца'
        verbose_name_plural = 'Профили жильцов'


class News(models.Model):
    """Новости и объявления"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name='Изображение')
    is_important = models.BooleanField(default=False, verbose_name='Важное')
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-date_posted']


class Service(models.Model):
    """Услуги ЖКХ"""
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    unit = models.CharField(max_length=20, verbose_name='Единица измерения', default='кВт/ч')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Тариф (руб)')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class MeterReading(models.Model):
    """Показания счетчиков"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Жилец')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    value = models.FloatField(verbose_name='Показание')
    date_submitted = models.DateTimeField(auto_now_add=True, verbose_name='Дата передачи')
    month = models.CharField(max_length=7, verbose_name='Месяц')
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name}: {self.value}"
    
    class Meta:
        verbose_name = 'Показание'
        verbose_name_plural = 'Показания'


class Request(models.Model):
    """Заявки в диспетчерскую службу"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
    ]
    CATEGORY_CHOICES = [
        ('plumbing', 'Сантехника'),
        ('electrical', 'Электрика'),
        ('heating', 'Отопление'),
        ('other', 'Другое'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Жилец')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    photo = models.ImageField(upload_to='requests/', blank=True, null=True, verbose_name='Фото')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    admin_comment = models.TextField(blank=True, verbose_name='Комментарий администратора')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']


class Notification(models.Model):
    """Уведомления для пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Пользователь')
    message = models.TextField(verbose_name='Сообщение')
    link = models.CharField(max_length=200, blank=True, verbose_name='Ссылка')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"


class RequestReview(models.Model):
    """Отзывы на выполненные заявки"""
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='review', verbose_name='Заявка')
    rating = models.IntegerField(verbose_name='Оценка')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
    
    def __str__(self):
        return f"{self.request.title} - {self.rating}★"

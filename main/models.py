from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    apartment_number = models.CharField(max_length=10, verbose_name='Номер квартиры')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    personal_account = models.CharField(max_length=20, blank=True, verbose_name='Лицевой счет')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - кв.{self.apartment_number}"
    
    class Meta:
        verbose_name = 'Профиль жильца'
        verbose_name_plural = 'Профили жильцов'


class News(models.Model):
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
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    unit = models.CharField(max_length=20, verbose_name='Единица измерения', default='кВт/ч')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Тариф (руб)')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class MeterReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Жилец')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    value = models.FloatField(validators=[MinValueValidator(0)], verbose_name='Показание')
    date_submitted = models.DateTimeField(auto_now_add=True, verbose_name='Дата передачи')
    month = models.CharField(max_length=7, verbose_name='Месяц')
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name}: {self.value}"
    
    class Meta:
        verbose_name = 'Показание'
        verbose_name_plural = 'Показания'
        unique_together = ['user', 'service', 'month']


class Request(models.Model):
    STATUS_CHOICES = [
        ('new', '🟡 Новая'),
        ('in_progress', '🔵 В работе'),
        ('completed', '✅ Выполнена'),
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


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Жилец')
    month = models.CharField(max_length=7, verbose_name='Месяц')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачено')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')
    
    def __str__(self):
        return f"{self.user.username} - {self.month}: {self.amount}"
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'


class Document(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    document_type = models.CharField(max_length=50, verbose_name='Тип')
    file = models.FileField(upload_to='documents/', verbose_name='Файл')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_public = models.BooleanField(default=True, verbose_name='Публичный')
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-date_posted']


class Notification(models.Model):
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
    request = models.OneToOneField('main.Request', on_delete=models.CASCADE, related_name='review', verbose_name='Заявка')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Оценка')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
    
    def __str__(self):
        return f"{self.request.title} - {self.rating}★"


class ShutdownSchedule(models.Model):
    SERVICE_TYPES = [
        ('hot_water', 'Горячая вода'),
        ('cold_water', 'Холодная вода'),
        ('electricity', 'Электричество'),
        ('heating', 'Отопление'),
        ('gas', 'Газ'),
    ]
    
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name='Тип услуги')
    start_date = models.DateTimeField(verbose_name='Начало отключения')
    end_date = models.DateTimeField(verbose_name='Окончание отключения')
    address = models.CharField(max_length=200, verbose_name='Адрес', blank=True, help_text='Оставьте пустым для всего дома')
    description = models.TextField(verbose_name='Причина', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'График отключений'
        verbose_name_plural = 'График отключений'
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.start_date.strftime('%d.%m.%Y')}"
    
    def is_current(self):
        from django.utils import timezone
        return self.start_date <= timezone.now() <= self.end_date


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    name = models.CharField(max_length=100, verbose_name='Имя')
    position = models.CharField(max_length=100, verbose_name='Должность')
    photo = models.ImageField(upload_to='employees/', blank=True, null=True, verbose_name='Фото')
    rating = models.FloatField(default=0, verbose_name='Рейтинг')
    total_reviews = models.IntegerField(default=0, verbose_name='Количество отзывов')
    is_active = models.BooleanField(default=True, verbose_name='Работает')
    description = models.TextField(blank=True, verbose_name='Описание')
    experience = models.IntegerField(default=0, verbose_name='Стаж (лет)')
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
    
    def __str__(self):
        return f"{self.name} - {self.position}"
    
    def update_rating(self):
        reviews = EmployeeReview.objects.filter(employee=self)
        if reviews.exists():
            self.total_reviews = reviews.count()
            self.rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
            self.save()


class EmployeeReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews', verbose_name='Сотрудник')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    request = models.ForeignKey('main.Request', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Заявка')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Оценка')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    
    class Meta:
        verbose_name = 'Отзыв о сотруднике'
        verbose_name_plural = 'Отзывы о сотрудниках'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.employee.update_rating()
    
    def __str__(self):
        return f"{self.employee.name} - {self.rating}★"


class HouseInfo(models.Model):
    address = models.CharField(max_length=300, unique=True, verbose_name='Адрес дома')
    building_year = models.IntegerField(null=True, blank=True, verbose_name='Год постройки')
    floors = models.IntegerField(null=True, blank=True, verbose_name='Количество этажей')
    entrances = models.IntegerField(null=True, blank=True, verbose_name='Количество подъездов')
    flat_count = models.IntegerField(null=True, blank=True, verbose_name='Количество квартир')
    total_area = models.FloatField(null=True, blank=True, verbose_name='Общая площадь (м²)')
    managing_company = models.CharField(max_length=200, blank=True, verbose_name='Управляющая компания')
    chief_engineer = models.CharField(max_length=200, blank=True, verbose_name='Главный инженер')
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон диспетчерской')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    def __str__(self):
        return self.address
    
    class Meta:
        verbose_name = 'Информация о доме'
        verbose_name_plural = 'Информация о домах'

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Profile, Service, MeterReading, Payment
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'Создает 5 тестовых жильцов с показаниями и долгами'

    def handle(self, *args, **kwargs):
        current_month = datetime.now().strftime('%m.%Y')
        
        users_data = [
            {
                'username': 'ivanov',
                'password': 'user123',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'email': 'ivanov@example.com',
                'apartment': '12',
                'phone': '+7(900)111-22-33',
                'readings': {'Электроэнергия': 150, 'Холодная вода': 8, 'Горячая вода': 5}
            },
            {
                'username': 'petrov',
                'password': 'user123',
                'first_name': 'Петр',
                'last_name': 'Петров',
                'email': 'petrov@example.com',
                'apartment': '34',
                'phone': '+7(900)222-33-44',
                'readings': {'Электроэнергия': 200, 'Холодная вода': 12, 'Горячая вода': 7}
            },
            {
                'username': 'sidorov',
                'password': 'user123',
                'first_name': 'Сидор',
                'last_name': 'Сидоров',
                'email': 'sidorov@example.com',
                'apartment': '56',
                'phone': '+7(900)333-44-55',
                'readings': {'Электроэнергия': 100, 'Холодная вода': 6, 'Горячая вода': 3}
            },
            {
                'username': 'kuznetsova',
                'password': 'user123',
                'first_name': 'Анна',
                'last_name': 'Кузнецова',
                'email': 'kuznetsova@example.com',
                'apartment': '78',
                'phone': '+7(900)444-55-66',
                'readings': {'Электроэнергия': 250, 'Холодная вода': 15, 'Горячая вода': 10}
            },
            {
                'username': 'morozov',
                'password': 'user123',
                'first_name': 'Дмитрий',
                'last_name': 'Морозов',
                'email': 'morozov@example.com',
                'apartment': '91',
                'phone': '+7(900)555-66-77',
                'readings': {'Электроэнергия': 80, 'Холодная вода': 5, 'Горячая вода': 2}
            },
        ]
        
        created_count = 0
        reading_count = 0
        payment_count = 0
        
        for data in users_data:
            # Создаем пользователя
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                }
            )
            
            if created:
                user.set_password(data['password'])
                user.save()
                created_count += 1
                
                # Создаем профиль
                Profile.objects.create(
                    user=user,
                    apartment_number=data['apartment'],
                    phone=data['phone'],
                    personal_account=f'ЛС-{user.id:05d}'
                )
                
                # Создаем показания и платежи
                for service_name, value in data['readings'].items():
                    try:
                        service = Service.objects.get(name=service_name)
                        
                        # Показание
                        reading = MeterReading.objects.create(
                            user=user,
                            service=service,
                            value=value,
                            month=current_month
                        )
                        reading_count += 1
                        
                        # Платеж
                        amount = value * float(service.price)
                        payment, p_created = Payment.objects.get_or_create(
                            user=user,
                            month=current_month,
                            defaults={'amount': amount, 'is_paid': False}
                        )
                        if p_created:
                            payment_count += 1
                            
                    except Service.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Услуга "{service_name}" не найдена, создайте ее сначала'))
                
                self.stdout.write(self.style.SUCCESS(f'✅ Создан жилец: {data["username"]} - кв.{data["apartment"]}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 ИТОГО: Создано {created_count} жильцов, {reading_count} показаний, {payment_count} платежей'))
from django.core.management.base import BaseCommand
from main.models import Service

class Command(BaseCommand):
    help = 'Создает 5 стандартных услуг ЖКХ'

    def handle(self, *args, **kwargs):
        services_data = [
            {'name': 'Электроэнергия', 'unit': 'кВт/ч', 'price': 4.50},
            {'name': 'Холодная вода', 'unit': 'м³', 'price': 35.00},
            {'name': 'Горячая вода', 'unit': 'м³', 'price': 120.00},
            {'name': 'Отопление', 'unit': 'Гкал', 'price': 1800.00},
            {'name': 'Содержание жилья', 'unit': 'м²', 'price': 25.50},
        ]
        
        created_count = 0
        existing_count = 0
        
        for data in services_data:
            service, created = Service.objects.get_or_create(
                name=data['name'],
                defaults={
                    'unit': data['unit'],
                    'price': data['price']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Создана услуга: {service.name}'))
            else:
                existing_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Создано: {created_count}, уже было: {existing_count}'))

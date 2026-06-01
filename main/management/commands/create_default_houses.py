from django.core.management.base import BaseCommand
from main.models import HouseInfo

class Command(BaseCommand):
    help = 'Создает стандартные дома'

    def handle(self, *args, **kwargs):
        houses_data = [
            {
                'address': 'г. Орск, ул. Ленина, 10',
                'year_built': 1985,
                'floors': 5,
                'entrances': 4,
                'apartments': 80,
                'total_area': 5200.0,
                'management_company': 'ООО "ЖЭУ-1"',
                'chief_engineer': 'Петров Иван Сергеевич',
                'phone': '+7(3537)25-25-25',
                'description': 'Дом оборудован пандусами, видеонаблюдение'
            },
            {
                'address': 'г. Орск, ул. Гагарина, 25',
                'year_built': 1992,
                'floors': 9,
                'entrances': 3,
                'apartments': 108,
                'total_area': 7800.0,
                'management_company': 'ООО "ЖЭУ-2"',
                'chief_engineer': 'Сидорова Анна Сергеевна',
                'phone': '+7(3537)26-26-26',
                'description': 'Лифты, мусоропровод, детская площадка'
            },
            {
                'address': 'г. Орск, пр. Мира, 42',
                'year_built': 1978,
                'floors': 5,
                'entrances': 6,
                'apartments': 120,
                'total_area': 7100.0,
                'management_company': 'ООО "ЖЭУ-3"',
                'chief_engineer': 'Козлов Дмитрий Николаевич',
                'phone': '+7(3537)27-27-27',
                'description': 'Пандусы, спортивная площадка'
            },
            {
                'address': 'г. Орск, ул. Комарова, 15',
                'year_built': 2005,
                'floors': 10,
                'entrances': 2,
                'apartments': 60,
                'total_area': 4500.0,
                'management_company': 'ООО "ЖЭУ-1"',
                'chief_engineer': 'Петров Иван Сергеевич',
                'phone': '+7(3537)25-25-25',
                'description': 'Новостройка, домофон, видеонаблюдение'
            },
            {
                'address': 'г. Орск, ул. Строителей, 8',
                'year_built': 1995,
                'floors': 6,
                'entrances': 4,
                'apartments': 96,
                'total_area': 6800.0,
                'management_company': 'ООО "ЖЭУ-2"',
                'chief_engineer': 'Сидорова Анна Сергеевна',
                'phone': '+7(3537)26-26-26',
                'description': 'Мусоропровод, лифты'
            },
            {
                'address': 'г. Орск, ул. Нефтяников, 3',
                'year_built': 1980,
                'floors': 5,
                'entrances': 8,
                'apartments': 160,
                'total_area': 9800.0,
                'management_company': 'ООО "ЖЭУ-3"',
                'chief_engineer': 'Козлов Дмитрий Николаевич',
                'phone': '+7(3537)27-27-27',
                'description': 'Крупный жилой комплекс'
            },
            {
                'address': 'г. Орск, ул. Металлургов, 22',
                'year_built': 2000,
                'floors': 7,
                'entrances': 3,
                'apartments': 84,
                'total_area': 6200.0,
                'management_company': 'ООО "ЖЭУ-1"',
                'chief_engineer': 'Петров Иван Сергеевич',
                'phone': '+7(3537)25-25-25',
                'description': 'Пандусы, детская площадка'
            },
            {
                'address': 'г. Орск, ул. Заводская, 11',
                'year_built': 1988,
                'floors': 4,
                'entrances': 2,
                'apartments': 48,
                'total_area': 3500.0,
                'management_company': 'ООО "ЖЭУ-2"',
                'chief_engineer': 'Сидорова Анна Сергеевна',
                'phone': '+7(3537)26-26-26',
                'description': 'Тихий двор, парковка'
            },
            {
                'address': 'г. Орск, ул. Шевченко, 7',
                'year_built': 2010,
                'floors': 12,
                'entrances': 4,
                'apartments': 144,
                'total_area': 10500.0,
                'management_company': 'ООО "ЖЭУ-3"',
                'chief_engineer': 'Козлов Дмитрий Николаевич',
                'phone': '+7(3537)27-27-27',
                'description': 'Современный дом, подземный паркинг'
            },
            {
                'address': 'г. Орск, ул. Деповская, 5',
                'year_built': 1975,
                'floors': 4,
                'entrances': 4,
                'apartments': 64,
                'total_area': 4200.0,
                'management_company': 'ООО "ЖЭУ-1"',
                'chief_engineer': 'Петров Иван Сергеевич',
                'phone': '+7(3537)25-25-25',
                'description': 'Близко к ж/д вокзалу'
            },
            {
                'address': 'г. Орск, ул. Краматорская, 9',
                'year_built': 1998,
                'floors': 6,
                'entrances': 3,
                'apartments': 72,
                'total_area': 5300.0,
                'management_company': 'ООО "ЖЭУ-2"',
                'chief_engineer': 'Сидорова Анна Сергеевна',
                'phone': '+7(3537)26-26-26',
                'description': 'Закрытый двор, шлагбаум'
            },
            {
                'address': 'г. Орск, ул. Победы, 1',
                'year_built': 2015,
                'floors': 16,
                'entrances': 5,
                'apartments': 200,
                'total_area': 15200.0,
                'management_company': 'ООО "ЖЭУ-3"',
                'chief_engineer': 'Козлов Дмитрий Николаевич',
                'phone': '+7(3537)27-27-27',
                'description': 'ЖК "Победа", современные планировки'
            },
            {
                'address': 'г. Орск, ул. Дружбы, 14',
                'year_built': 1983,
                'floors': 5,
                'entrances': 5,
                'apartments': 100,
                'total_area': 6800.0,
                'management_company': 'ООО "ЖЭУ-1"',
                'chief_engineer': 'Петров Иван Сергеевич',
                'phone': '+7(3537)25-25-25',
                'description': 'Рядом школа и детский сад'
            },
            {
                'address': 'г. Орск, ул. Мичурина, 17',
                'year_built': 2002,
                'floors': 8,
                'entrances': 2,
                'apartments': 64,
                'total_area': 4900.0,
                'management_company': 'ООО "ЖЭУ-2"',
                'chief_engineer': 'Сидорова Анна Сергеевна',
                'phone': '+7(3537)26-26-26',
                'description': 'Тихий район, парк рядом'
            },
            {
                'address': 'г. Орск, ул. Южная, 6',
                'year_built': 2018,
                'floors': 9,
                'entrances': 3,
                'apartments': 108,
                'total_area': 7800.0,
                'management_company': 'ООО "ЖЭУ-3"',
                'chief_engineer': 'Козлов Дмитрий Николаевич',
                'phone': '+7(3537)27-27-27',
                'description': 'Новостройка, остеклённые балконы'
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for data in houses_data:
            house, created = HouseInfo.objects.get_or_create(
                address=data['address'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Добавлен дом: {house.address}'))
            else:
                existing_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Добавлено {created_count} домов, уже было {existing_count}'))

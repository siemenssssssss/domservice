from django.core.management.base import BaseCommand
from main.models import News
from datetime import datetime

class Command(BaseCommand):
    help = 'Создает 3 стандартные новости'

    def handle(self, *args, **kwargs):
        news_data = [
            {
                'title': 'Плановое отключение горячей воды',
                'content': 'Уважаемые жильцы! С 20 по 25 мая будет плановое отключение горячей воды. Приносим извинения за временные неудобства. Рекомендуем заблаговременно сделать запасы воды.',
                'is_important': True,
            },
            {
                'title': 'Субботник во дворе',
                'content': 'Приглашаем всех жильцов на субботник, который состоится 28 мая в 10:00 у подъезда №1. Будет организован инвентарь и горячий чай. Приходите, сделаем наш двор чище!',
                'is_important': True,
            },
            {
                'title': 'Новые тарифы с 1 июня',
                'content': 'Уважаемые жильцы! С 1 июня 2026 года меняются тарифы на коммунальные услуги. С актуальными тарифами можно ознакомиться в разделе "Документы" или в нашей админ-панели.',
                'is_important': False,
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for data in news_data:
            news, created = News.objects.get_or_create(
                title=data['title'],
                defaults={
                    'content': data['content'],
                    'is_important': data['is_important'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Создана новость: {news.title}'))
            else:
                existing_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 ИТОГО: создано {created_count} новостей, уже существовало {existing_count}'))
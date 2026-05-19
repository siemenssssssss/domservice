from django.core.management.base import BaseCommand
from main.models import Document
from datetime import datetime

class Command(BaseCommand):
    help = 'Создает 2 стандартных документа'

    def handle(self, *args, **kwargs):
        documents_data = [
            {
                'title': 'Устав УК "ДомСервис"',
                'document_type': 'protocol',
                'description': 'Устав управляющей компании "ДомСервис". Утвержден общим собранием учредителей. Регулирует основные направления деятельности УК.',
                'is_public': True,
            },
            {
                'title': 'Тарифы на коммунальные услуги на 2026 год',
                'document_type': 'tariff',
                'description': 'Утвержденные тарифы на коммунальные услуги с 1 января 2026 года. Включает тарифы на электроэнергию, холодную и горячую воду, отопление и содержание жилья.',
                'is_public': True,
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for data in documents_data:
            document, created = Document.objects.get_or_create(
                title=data['title'],
                defaults={
                    'document_type': data['document_type'],
                    'description': data['description'],
                    'is_public': data['is_public'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Создан документ: {document.title}'))
            else:
                existing_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 ИТОГО: создано {created_count} документов, уже существовало {existing_count}'))
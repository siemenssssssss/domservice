from django.core.management.base import BaseCommand
from main.utils import check_debt_notifications

class Command(BaseCommand):
    help = 'Check debts and create notifications'

    def handle(self, *args, **options):
        check_debt_notifications()
        self.stdout.write(self.style.SUCCESS('Debt check completed'))
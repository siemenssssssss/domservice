from .models import Notification
from django.utils import timezone
from datetime import timedelta

def create_notification(user, message, link=''):
    """Создает уведомление для пользователя"""
    Notification.objects.create(
        user=user,
        message=message,
        link=link,
        is_read=False,
        created_at=timezone.now()
    )

def check_debt_notifications():
    """Проверяет задолженности и создает уведомления (при каждом запросе)"""
    from .models import Payment
    
    # Находим все неоплаченные платежи
    unpaid_payments = Payment.objects.filter(is_paid=False)
    
    for payment in unpaid_payments:
        user = payment.user
        
        # Проверяем, есть ли НЕПРОЧИТАННОЕ уведомление об этом платеже
        existing_unread = Notification.objects.filter(
            user=user,
            message__contains=f'задолженность за {payment.month}',
            is_read=False
        ).exists()
        
        # Если нет непрочитанного уведомления — создаем
        if not existing_unread:
            create_notification(
                user,
                f'⚠️ У вас задолженность за {payment.month} в размере {payment.amount} руб. Просим оплатить.',
                '/payments/'
            )
from .models import Notification
from .utils import check_debt_notifications

def notifications(request):
    """Добавляет уведомления в контекст всех шаблонов"""
    if request.user.is_authenticated:
        # Проверяем задолженности при КАЖДОМ запросе
        check_debt_notifications()
        
        notifications = Notification.objects.filter(user=request.user)[:50]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'notifications': notifications,
            'unread_notifications_count': unread_count
        }
    return {'notifications': [], 'unread_notifications_count': 0}
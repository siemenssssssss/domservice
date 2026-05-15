from django.contrib import admin
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment
import csv
from io import StringIO

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=payments_export.csv'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Пользователь', 'Месяц', 'Сумма', 'Оплачено', 'Дата оплаты'])
        
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.user.username,
                obj.month,
                obj.amount,
                'Да' if obj.is_paid else 'Нет',
                obj.paid_at or ''
            ])
        return response
    export_as_csv.short_description = "📤 Экспорт выбранных платежей в CSV"

def send_invoices_to_selected(modeladmin, request, queryset):
    count = 0
    for payment in queryset.filter(is_paid=False):
        if payment.user.email:
            try:
                send_mail(
                    subject=f'💳 Квитанция на оплату за {payment.month}',
                    message=f"""
Здравствуйте, {payment.user.get_full_name() or payment.user.username}!

Вам выставлен счет за {payment.month}.

💰 Сумма к оплате: {payment.amount} руб.

Оплатить можно в личном кабинете: https://domservice.onrender.com/payments/

С уважением,
Управляющая компания
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@domservice.onrender.com',
                    recipient_list=[payment.user.email],
                    fail_silently=False,
                )
                count += 1
            except Exception as e:
                print(f'Ошибка отправки {payment.user.email}: {e}')
    modeladmin.message_user(request, f'✅ Счета отправлены {count} жильцам')
send_invoices_to_selected.short_description = "📧 Отправить счета выбранным плательщикам"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ['user', 'month', 'amount', 'is_paid', 'paid_at']
    list_filter = ['is_paid', 'month', 'user']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    actions = [export_as_csv, send_invoices_to_selected]
    list_editable = ['is_paid']

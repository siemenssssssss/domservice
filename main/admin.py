from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
import xml.etree.ElementTree as ET
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import Sum
from django.utils.safestring import mark_safe

from .models import (
    Profile, News, Service, MeterReading, Request, Payment,
    HouseInfo, Document, Notification, RequestReview,
    ShutdownSchedule, Employee, EmployeeReview
)
from .utils import create_notification


def export_residents_xml(request):
    """Экспорт всех жильцов с их показаниями и долгами в XML"""
    users = User.objects.filter(is_superuser=False, is_staff=False)
    root = ET.Element('residents')
    
    for user in users:
        try:
            profile = Profile.objects.get(user=user)
            apartment = profile.apartment_number
            phone = profile.phone
            personal_account = profile.personal_account
        except:
            apartment = ''
            phone = ''
            personal_account = f'ЛС-{user.id:06d}'
        
        total_debt = Payment.objects.filter(user=user, is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
        unpaid_payments = Payment.objects.filter(user=user, is_paid=False)
        
        # Получаем показания пользователя
        readings = MeterReading.objects.filter(user=user).order_by('-month')
        
        resident = ET.SubElement(root, 'resident', id=str(user.id))
        ET.SubElement(resident, 'username').text = user.username
        ET.SubElement(resident, 'first_name').text = user.first_name or ''
        ET.SubElement(resident, 'last_name').text = user.last_name or ''
        ET.SubElement(resident, 'email').text = user.email or ''
        ET.SubElement(resident, 'apartment').text = apartment
        ET.SubElement(resident, 'phone').text = phone
        ET.SubElement(resident, 'personal_account').text = personal_account
        ET.SubElement(resident, 'total_debt').text = str(float(total_debt))
        ET.SubElement(resident, 'date_joined').text = user.date_joined.strftime('%Y-%m-%d')
        
        # Добавляем показания в XML
        readings_elem = ET.SubElement(resident, 'meter_readings')
        for reading in readings:
            r_elem = ET.SubElement(readings_elem, 'reading')
            ET.SubElement(r_elem, 'service').text = reading.service.name
            ET.SubElement(r_elem, 'value').text = str(reading.value)
            ET.SubElement(r_elem, 'month').text = reading.month
        
        # Добавляем неоплаченные платежи
        payments_elem = ET.SubElement(resident, 'unpaid_payments')
        for payment in unpaid_payments:
            p_elem = ET.SubElement(payments_elem, 'payment')
            ET.SubElement(p_elem, 'month').text = payment.month
            ET.SubElement(p_elem, 'amount').text = str(float(payment.amount))
    
    response = HttpResponse(ET.tostring(root, encoding='utf-8', xml_declaration=True), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="residents_with_debts.xml"'
    return response


def import_residents_xml(request):
    """Импорт XML и автоматическое создание платежей"""
    if request.method == 'POST' and request.FILES.get('xml_file'):
        try:
            tree = ET.parse(request.FILES['xml_file'])
            root = tree.getroot()
            created_count = 0
            error_count = 0
            
            for resident in root.findall('resident'):
                try:
                    username = resident.find('username').text
                    user = User.objects.get(username=username)
                    
                    payments_elem = resident.find('unpaid_payments')
                    if payments_elem is not None:
                        for payment_elem in payments_elem.findall('payment'):
                            month = payment_elem.find('month').text
                            amount = Decimal(payment_elem.find('amount').text)
                            
                            payment, created = Payment.objects.get_or_create(
                                user=user, month=month,
                                defaults={'amount': amount, 'is_paid': False, 'paid_at': None}
                            )
                            
                            if created:
                                created_count += 1
                                create_notification(
                                    user, 
                                    f'💰 Выставлен счет за {month} на сумму {amount} руб.',
                                    '/payments/'
                                )
                            else:
                                if payment.amount != amount:
                                    payment.amount = amount
                                    payment.save()
                                    create_notification(
                                        user,
                                        f'💰 Обновлен счет за {month} на сумму {amount} руб.',
                                        '/payments/'
                                    )
                except Exception as e:
                    error_count += 1
            
            messages.success(request, f'✅ Создано/обновлено {created_count} счетов. Ошибок: {error_count}')
        except Exception as e:
            messages.error(request, f'❌ Ошибка: {str(e)}')
        return HttpResponseRedirect('../')
    
    return render(request, 'admin/import_xml_form.html')


def calculate_debts_from_readings(request):
    """Автоматический расчет долгов из переданных показаний за текущий месяц"""
    from datetime import datetime
    current_month = datetime.now().strftime('%m.%Y')
    readings = MeterReading.objects.filter(month=current_month)
    created_count = 0
    updated_count = 0
    
    for reading in readings:
        amount = reading.value * float(reading.service.price)
        payment, created = Payment.objects.get_or_create(
            user=reading.user,
            month=current_month,
            defaults={'amount': amount, 'is_paid': False, 'paid_at': None}
        )
        if created:
            created_count += 1
        else:
            if payment.amount != amount:
                payment.amount = amount
                payment.save()
                updated_count += 1
    
    messages.success(request, f'✅ Рассчитано: создано {created_count} платежей, обновлено {updated_count}')
    return HttpResponseRedirect('../')


# ========== НАСТРОЙКИ АДМИНКИ С КНОПКАМИ СВЕРХУ ==========

class PaymentAdmin(admin.ModelAdmin):
    change_list_template = "admin/payments_change_list.html"
    list_display = ['user', 'month', 'amount', 'is_paid', 'paid_at']
    list_filter = ['is_paid', 'month']
    list_editable = ['is_paid']
    search_fields = ['user__username', 'user__email']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-xml/', self.admin_site.admin_view(export_residents_xml), name='export_residents_xml'),
            path('import-xml/', self.admin_site.admin_view(import_residents_xml), name='import_residents_xml'),
            path('calculate-debts/', self.admin_site.admin_view(calculate_debts_from_readings), name='calculate_debts'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_url'] = 'export-xml/'
        extra_context['import_url'] = 'import-xml/'
        extra_context['calculate_url'] = 'calculate-debts/'
        return super().changelist_view(request, extra_context=extra_context)


# Регистрируем модели
admin.site.register(Payment, PaymentAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'apartment_number', 'phone']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_posted', 'is_important']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'price']

@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'value', 'month']

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'created_at']
    list_editable = ['status']

@admin.register(HouseInfo)
class HouseInfoAdmin(admin.ModelAdmin):
    list_display = ['address', 'year_built', 'floors']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'date_posted']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']

@admin.register(RequestReview)
class RequestReviewAdmin(admin.ModelAdmin):
    list_display = ['request', 'rating', 'created_at']

@admin.register(ShutdownSchedule)
class ShutdownScheduleAdmin(admin.ModelAdmin):
    list_display = ['service_type', 'start_date', 'end_date']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'rating']

@admin.register(EmployeeReview)
class EmployeeReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'user', 'rating']

from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib import messages
import xml.etree.ElementTree as ET
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import Sum

# Импортируем модели из main.models
from main.models import Payment, Profile
from main.utils import create_notification


# Расширяем существующий PaymentAdmin, а не создаем новый
def export_residents_xml(modeladmin, request, queryset=None):
    """Экспорт жильцов с долгами в XML"""
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
        total_debt = float(total_debt)
        unpaid_payments = Payment.objects.filter(user=user, is_paid=False)
        
        resident = ET.SubElement(root, 'resident', id=str(user.id))
        ET.SubElement(resident, 'username').text = user.username
        ET.SubElement(resident, 'first_name').text = user.first_name or ''
        ET.SubElement(resident, 'last_name').text = user.last_name or ''
        ET.SubElement(resident, 'email').text = user.email or ''
        ET.SubElement(resident, 'apartment').text = apartment
        ET.SubElement(resident, 'phone').text = phone
        ET.SubElement(resident, 'personal_account').text = personal_account
        ET.SubElement(resident, 'total_debt').text = str(total_debt)
        ET.SubElement(resident, 'date_joined').text = user.date_joined.strftime('%Y-%m-%d')
        
        payments_elem = ET.SubElement(resident, 'unpaid_payments')
        for payment in unpaid_payments:
            p_elem = ET.SubElement(payments_elem, 'payment')
            ET.SubElement(p_elem, 'month').text = payment.month
            ET.SubElement(p_elem, 'amount').text = str(float(payment.amount))
    
    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    response = HttpResponse(xml_str, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="residents_with_debts.xml"'
    return response

export_residents_xml.short_description = "📤 Экспорт жильцов с долгами в XML"


def import_residents_xml_page(modeladmin, request, queryset=None):
    """Страница для загрузки XML файла"""
    context = {
        'title': 'Загрузить XML с жильцами и выставить счета',
        'opts': modeladmin.model._meta,
    }
    return TemplateResponse(request, 'admin/import_residents_xml.html', context)

import_residents_xml_page.short_description = "📥 Загрузить XML и выставить счета"


def import_residents_xml(modeladmin, request):
    """Обработка загруженного XML файла и создание платежей"""
    if request.method == 'POST' and request.FILES.get('xml_file'):
        xml_file = request.FILES['xml_file']
        
        try:
            tree = ET.parse(xml_file)
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
                                user=user,
                                month=month,
                                defaults={
                                    'amount': amount,
                                    'is_paid': False,
                                    'paid_at': None,
                                }
                            )
                            
                            if created:
                                created_count += 1
                                create_notification(
                                    user,
                                    f'💰 Вам выставлен новый счет за {month} на сумму {amount} руб.',
                                    '/payments/'
                                )
                    else:
                        total_debt = resident.find('total_debt')
                        if total_debt is not None and float(total_debt.text) > 0:
                            from datetime import datetime
                            current_month = datetime.now().strftime('%m.%Y')
                            amount = Decimal(total_debt.text)
                            
                            payment, created = Payment.objects.get_or_create(
                                user=user,
                                month=current_month,
                                defaults={
                                    'amount': amount,
                                    'is_paid': False,
                                    'paid_at': None,
                                }
                            )
                            
                            if created:
                                created_count += 1
                                create_notification(
                                    user,
                                    f'💰 Вам выставлен счет за {current_month} на сумму {amount} руб.',
                                    '/payments/'
                                )
                        
                except User.DoesNotExist:
                    error_count += 1
                except Exception as e:
                    error_count += 1
            
            messages.success(
                request, 
                f'✅ Создано {created_count} новых счетов. Ошибок: {error_count}'
            )
            
        except Exception as e:
            messages.error(request, f'❌ Ошибка при обработке XML: {str(e)}')
    
    return HttpResponseRedirect('../')


# Добавляем actions в существующий PaymentAdmin через monkey patch
# Находим уже зарегистрированный PaymentAdmin и добавляем в него действия
from django.contrib.admin import site
from main.admin import PaymentAdmin  # Импортируем существующий

if hasattr(PaymentAdmin, 'actions'):
    PaymentAdmin.actions += [export_residents_xml, import_residents_xml_page]
else:
    PaymentAdmin.actions = [export_residents_xml, import_residents_xml_page]

# Добавляем URL для импорта
original_get_urls = PaymentAdmin.get_urls
def get_urls_with_custom(self):
    urls = original_get_urls(self)
    custom_urls = [
        path('import-residents-xml/', self.admin_site.admin_view(import_residents_xml), name='import_residents_xml'),
    ]
    return custom_urls + urls
PaymentAdmin.get_urls = get_urls_with_custom

# Перерегистрируем модель с обновленным админом
site.unregister(Payment)
site.register(Payment, PaymentAdmin)

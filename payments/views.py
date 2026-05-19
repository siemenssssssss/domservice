from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from decimal import Decimal
from main.models import Payment, Profile
from main.utils import create_notification
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
import os

# Регистрируем русский шрифт (используем встроенный шрифт, который точно есть)
try:
    # Пробуем загрузить шрифт DejaVu
    font_path = os.path.join(os.path.dirname(__file__), '..', 'DejaVuSans.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        RUSSIAN_FONT = 'DejaVu'
    else:
        # Используем встроенный шрифт для кириллицы
        pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica'))
        RUSSIAN_FONT = 'Helvetica'
except:
    RUSSIAN_FONT = 'Helvetica'

def pay(request):
    """Симуляция оплаты"""
    
    amount_str = request.GET.get('amount', '0')
    month = request.GET.get('month')
    
    try:
        amount = Decimal(str(amount_str))
    except:
        try:
            amount = Decimal(amount_str.replace(',', '.'))
        except:
            amount = Decimal('0')
    
    payment = None
    if amount > 0 and month:
        try:
            payment = Payment.objects.get(
                user=request.user,
                month=month,
                amount=amount,
                is_paid=False
            )
        except Payment.DoesNotExist:
            messages.error(request, f'Платеж за {month} на сумму {amount} руб. не найден или уже оплачен')
            return redirect('payments')
    
    if request.method == 'POST':
        amount_str = request.POST.get('amount', '0')
        month = request.POST.get('month')
        download_receipt = request.POST.get('download_receipt', 'no')
        
        try:
            amount = Decimal(str(amount_str))
        except:
            try:
                amount = Decimal(amount_str.replace(',', '.'))
            except:
                amount = Decimal('0')
        
        try:
            payment = Payment.objects.get(
                user=request.user,
                month=month,
                amount=amount,
                is_paid=False
            )
            payment.is_paid = True
            payment.paid_at = timezone.now()
            payment.save()
            
            create_notification(
                request.user,
                f'✅ Оплата за {month} в размере {amount} руб. успешно проведена. Спасибо!',
                '/payments/'
            )
            
            messages.success(request, f'✅ Оплата за {month} в размере {amount} руб. успешно выполнена!')
            
            if download_receipt == 'yes':
                return generate_receipt(request.user, payment)
            else:
                return redirect('payments')
            
        except Payment.DoesNotExist:
            messages.error(request, 'Платеж не найден или уже оплачен')
            return redirect('payments')
    
    context = {
        'amount': amount,
        'month': month,
        'payment': payment
    }
    return render(request, 'payments/pay.html', context)

def generate_receipt(user, payment):
    """Генерирует PDF квитанцию об оплате с русским текстом"""
    
    # Получаем профиль пользователя
    try:
        profile = Profile.objects.get(user=user)
        apartment = profile.apartment_number
        phone = profile.phone
        personal_account = profile.personal_account
    except:
        apartment = 'Не указан'
        phone = 'Не указан'
        personal_account = f'ЛС-{user.id:06d}'
    
    # Создаем буфер для PDF
    buffer = io.BytesIO()
    
    # Создаем документ
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Стили с русским шрифтом (используем стандартный шрифт)
    styles = getSampleStyleSheet()
    
    # Создаем стили для русского текста со стандартным шрифтом
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName=RUSSIAN_FONT
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=12,
        fontName=RUSSIAN_FONT
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=6,
        fontName=RUSSIAN_FONT
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=6,
        fontName=RUSSIAN_FONT
    )
    
    # Содержимое
    story = []
    
    # Заголовок
    story.append(Paragraph("КВИТАНЦИЯ ОБ ОПЛАТЕ", title_style))
    story.append(Spacer(1, 20))
    
    # Данные плательщика
    story.append(Paragraph("ДАННЫЕ ПЛАТЕЛЬЩИКА", header_style))
    story.append(Paragraph(f"ФИО: {user.get_full_name() or user.username}", normal_style))
    story.append(Paragraph(f"Лицевой счет: {personal_account}", normal_style))
    story.append(Paragraph(f"Квартира: {apartment}", normal_style))
    story.append(Paragraph(f"Телефон: {phone}", normal_style))
    story.append(Paragraph(f"Email: {user.email or 'Не указан'}", normal_style))
    story.append(Spacer(1, 20))
    
    # Данные платежа
    story.append(Paragraph("ДАННЫЕ ПЛАТЕЖА", header_style))
    
    # Таблица с услугами
    data = [
        ['Наименование услуги', 'Период', 'Сумма'],
        ['Коммунальные услуги', f'{payment.month}', f'{float(payment.amount):,.2f} руб.'],
    ]
    
    table = Table(data, colWidths=[250, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e4a6e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('FONTNAME', (0, 1), (-1, -1), RUSSIAN_FONT),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Итого
    story.append(Paragraph(f"ИТОГО К ОПЛАТЕ: {float(payment.amount):,.2f} руб.", bold_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"ДАТА ОПЛАТЫ: {payment.paid_at.strftime('%d.%m.%Y %H:%M') if payment.paid_at else 'Не указана'}", normal_style))
    story.append(Spacer(1, 30))
    
    # Подпись
    story.append(Paragraph("Оплата произведена через систему онлайн-платежей", normal_style))
    story.append(Paragraph("Управляющая компания 'ДомСервис'", normal_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Спасибо за своевременную оплату!", normal_style))
    
    # Строим документ
    doc.build(story)
    
    # Получаем PDF из буфера
    pdf = buffer.getvalue()
    buffer.close()
    
    # Отправляем PDF как ответ
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="kvitanciya_{payment.month}.pdf"'
    response.write(pdf)
    return response

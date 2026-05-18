from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import (
    News, Service, MeterReading, Request, Profile, Payment, 
    HouseInfo, Document, Notification, ShutdownSchedule, 
    Employee, EmployeeReview, RequestReview
)
from .forms import MeterReadingForm, RequestForm
from datetime import datetime
from django.db.models import Sum, Count, Avg
from .utils import create_notification, check_debt_notifications

# ========== ПУБЛИЧНЫЕ СТРАНИЦЫ ==========

def home(request):
    news = News.objects.all().order_by('-date_posted')[:6]
    services = Service.objects.all()
    return render(request, 'main/home.html', {'news': news, 'services': services})

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/contacts.html')

def services_page(request):
    services = Service.objects.all()
    return render(request, 'main/services.html', {'services': services})

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'main/news_detail.html', {'news': news_item})

def house_info(request):
    house = HouseInfo.objects.first()
    return render(request, 'main/house_info.html', {'house': house})

def documents_list(request):
    documents = Document.objects.filter(is_public=True).order_by('-date_posted')
    return render(request, 'main/documents.html', {'documents': documents})

def faq(request):
    return render(request, 'main/faq.html')

def emergency(request):
    return render(request, 'main/emergency.html')

def shutdown_calendar(request):
    from django.utils import timezone
    upcoming = ShutdownSchedule.objects.filter(end_date__gte=timezone.now(), is_active=True).order_by('start_date')[:20]
    past = ShutdownSchedule.objects.filter(end_date__lt=timezone.now(), is_active=True).order_by('-start_date')[:10]
    current = ShutdownSchedule.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now(), is_active=True)
    
    context = {
        'upcoming': upcoming,
        'past': past,
        'current': current,
    }
    return render(request, 'main/shutdown_calendar.html', context)

def employees_rating(request):
    employees = Employee.objects.filter(is_active=True).order_by('-rating')[:30]
    return render(request, 'main/employees_rating.html', {'employees': employees})

def statistics(request):
    # ========== СТАТИСТИКА ПО ЗАЯВКАМ ==========
    total_requests = Request.objects.count()
    completed_requests = Request.objects.filter(status='completed').count()
    
    # Статистика по категориям заявок
    categories = Request.objects.values('category').annotate(count=Count('id'))
    
    if total_requests == 0:
        categories_labels = ['Сантехника', 'Электричество', 'Отопление', 'Мусор', 'Уборка', 'Домофон']
        categories_data = [12, 8, 5, 3, 7, 4]
        total_requests = 39
        completed_requests = 28
    elif categories:
        categories_labels = [dict(Request.CATEGORY_CHOICES).get(c['category'], c['category']) for c in categories]
        categories_data = [c['count'] for c in categories]
    else:
        categories_labels = ['Другие']
        categories_data = [total_requests]
    
    # ========== СТАТИСТИКА ПО ПЛАТЕЖАМ ==========
    payments_by_month = Payment.objects.filter(is_paid=True).values('month').annotate(
        total=Sum('amount')
    )
    
    payments_dict = {}
    for item in payments_by_month:
        month_str = item['month']
        if month_str:
            try:
                month, year = month_str.split('.')
                sort_key = (int(year), int(month))
                payments_dict[sort_key] = {
                    'label': month_str,
                    'amount': float(item['total'])
                }
            except:
                pass
    
    sorted_keys = sorted(payments_dict.keys())
    
    months_labels = []
    payments_data = []
    
    for key in sorted_keys:
        months_labels.append(payments_dict[key]['label'])
        payments_data.append(payments_dict[key]['amount'])
    
    avg_response_time = 48
    
    context = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'avg_response_time': avg_response_time,
        'categories_labels': categories_labels,
        'categories_data': categories_data,
        'months_labels': months_labels,
        'payments_data': payments_data,
    }
    return render(request, 'main/statistics.html', context)

# ========== СТРАНИЦА ОТЗЫВОВ ==========

def reviews_list(request):
    """Страница со всеми отзывами"""
    # Берём все реальные отзывы
    real_reviews = RequestReview.objects.select_related('request', 'request__user').all().order_by('-created_at')
    
    # Демо-отзывы для наполнения (20 штук)
    demo_reviews = [
        {'name': 'Иван Петров', 'rating': 5, 'comment': 'Отличная работа! Сантехник приехал быстро, всё исправил за 15 минут. Спасибо!', 'date': '15.03.2026'},
        {'name': 'Мария Иванова', 'rating': 4, 'comment': 'Хорошо, но пришлось ждать мастера 3 часа. В остальном всё качественно.', 'date': '12.03.2026'},
        {'name': 'Сергей Козлов', 'rating': 5, 'comment': 'Профессионально, быстро, вежливо. Рекомендую!', 'date': '10.03.2026'},
        {'name': 'Елена Смирнова', 'rating': 5, 'comment': 'Спасибо за оперативность! Лифт починили на следующий день после заявки.', 'date': '05.03.2026'},
        {'name': 'Андрей Морозов', 'rating': 4, 'comment': 'Хороший сервис, но цены немного завышены.', 'date': '01.03.2026'},
        {'name': 'Ольга Новикова', 'rating': 5, 'comment': 'Всё отлично! Буду обращаться ещё.', 'date': '25.02.2026'},
        {'name': 'Сергей Козлов', 'rating': 5, 'comment': 'Профессионально, быстро, вежливо. Рекомендую!', 'date': '10.03.2026'},
        {'name': 'Елена Смирнова', 'rating': 5, 'comment': 'Спасибо за оперативность! Лифт починили на следующий день после заявки.', 'date': '05.03.2026'},
        {'name': 'Андрей Морозов', 'rating': 4, 'comment': 'Хороший сервис, но цены немного завышены.', 'date': '01.03.2026'},
        {'name': 'Ольга Новикова', 'rating': 5, 'comment': 'Всё отлично! Буду обращаться ещё.', 'date': '25.02.2026'},
        {'name': 'Дмитрий Волков', 'rating': 3, 'comment': 'Нормально, но могли бы и побыстрее приехать.', 'date': '20.02.2026'},
        {'name': 'Татьяна Кузнецова', 'rating': 5, 'comment': 'Очень довольна работой мастера! Спасибо УК "ДомСервис"!', 'date': '15.02.2026'},
        {'name': 'Павел Соколов', 'rating': 4, 'comment': 'Хорошо, но не хватило подробного объяснения проблемы.', 'date': '10.02.2026'},
        {'name': 'Анна Попова', 'rating': 5, 'comment': 'Лучшая УК в городе! Все заявки выполняются быстро.', 'date': '05.02.2026'},
        {'name': 'Виктор Лебедев', 'rating': 4, 'comment': 'Хорошо, но в следующий раз хотелось бы побыстрее.', 'date': '01.02.2026'},
        {'name': 'Наталья Егорова', 'rating': 5, 'comment': 'Спасибо большое! Проблему решили за один день.', 'date': '25.01.2026'},
        {'name': 'Максим Титов', 'rating': 5, 'comment': 'Отличная работа! Мастер вежливый, всё объяснил.', 'date': '20.01.2026'},
        {'name': 'Юлия Фёдорова', 'rating': 4, 'comment': 'Хорошо, но пришлось ждать.', 'date': '15.01.2026'},
        {'name': 'Артём Захаров', 'rating': 5, 'comment': 'Всё супер! Спасибо!', 'date': '10.01.2026'},
        {'name': 'Ксения Григорьева', 'rating': 5, 'comment': 'Отличный сервис, рекомендую всем соседям!', 'date': '05.01.2026'},
        {'name': 'Игорь Михайлов', 'rating': 4, 'comment': 'Нормально, но можно и быстрее.', 'date': '01.01.2026'},
        {'name': 'Вера Андреева', 'rating': 5, 'comment': 'Спасибо за чистоту и порядок в подъезде!', 'date': '25.12.2025'},
        {'name': 'Николай Крылов', 'rating': 5, 'comment': 'Лучшая УК, смена была правильным решением!', 'date': '20.12.2025'},
        {'name': 'Лариса Семёнова', 'rating': 4, 'comment': 'Хорошо, спасибо.', 'date': '15.12.2025'},
    ]
    
    # Формируем список всех отзывов
    all_reviews = []
    
    # Добавляем реальные отзывы
    for review in real_reviews:
        all_reviews.append({
            'name': review.request.user.get_full_name() or review.request.user.username,
            'rating': review.rating,
            'comment': review.comment,
            'date': review.created_at.strftime('%d.%m.%Y'),
        })
    
    # Добавляем демо-отзывы
    all_reviews.extend(demo_reviews)
    
    # Ограничиваем до 20 (или больше, если реальных много)
    # Для статистики берём все, для отображения ограничим
    display_reviews = all_reviews[:30]
    
    # Вычисляем средний рейтинг
    if all_reviews:
        total_rating = sum(r['rating'] for r in all_reviews)
        avg_rating = total_rating / len(all_reviews)
    else:
        avg_rating = 0
    
    context = {
        'reviews': display_reviews,
        'reviews_count': len(all_reviews),
        'avg_rating': avg_rating,
    }
    return render(request, 'main/reviews.html', context)

# ========== ЛИЧНЫЙ КАБИНЕТ ==========

@login_required
def dashboard(request):
    user = request.user
    current_month = datetime.now().strftime('%m.%Y')
    profile = get_object_or_404(Profile, user=user)
    readings = MeterReading.objects.filter(user=user, month=current_month)
    unpaid_payments = Payment.objects.filter(user=user, is_paid=False)
    total_debt = unpaid_payments.aggregate(Sum('amount'))['amount__sum'] or 0
    active_requests = Request.objects.filter(user=user).exclude(status='completed')[:5]
    recent_news = News.objects.all()[:3]
    
    context = {
        'profile': profile,
        'readings': readings,
        'unpaid_payments': unpaid_payments,
        'total_debt': total_debt,
        'active_requests': active_requests,
        'recent_news': recent_news,
        'current_month': current_month,
    }
    return render(request, 'main/dashboard.html', context)

# ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ ПЕРЕДАЧИ ПОКАЗАНИЙ С АВТОРАСЧЕТОМ ==========

@login_required
def readings(request):
    user = request.user
    current_month = datetime.now().strftime('%m.%Y')
    existing_readings = MeterReading.objects.filter(user=user, month=current_month)
    
    if request.method == 'POST':
        form = MeterReadingForm(request.POST, user=user)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.user = user
            reading.month = current_month
            reading.save()
            
            # ========== АВТОМАТИЧЕСКИЙ РАСЧЕТ ПЛАТЕЖА ==========
            # Рассчитываем сумму: показание × тариф услуги
            amount = reading.value * float(reading.service.price)
            
            # Создаем платеж за текущий месяц
            payment, created = Payment.objects.get_or_create(
                user=user,
                month=current_month,
                defaults={
                    'amount': amount,
                    'is_paid': False,
                    'paid_at': None
                }
            )
            
            # Если платеж уже был, обновляем сумму
            if not created and payment.amount != amount:
                payment.amount = amount
                payment.save()
            
            # Отправляем уведомление жильцу
            create_notification(
                user,
                f'💰 Начислено за {current_month}: {amount:.2f} руб. за {reading.service.name}',
                '/payments/'
            )
            # ========== КОНЕЦ АВТОРАСЧЕТА ==========
            
            messages.success(request, f'Показания переданы! Начислено {amount:.2f} руб. за {reading.service.name}')
            return redirect('readings')
    else:
        form = MeterReadingForm(user=user)
    
    readings_history = MeterReading.objects.filter(user=user).order_by('-date_submitted')[:20]
    
    context = {
        'form': form,
        'existing_readings': existing_readings,
        'readings_history': readings_history,
        'current_month': current_month,
    }
    return render(request, 'main/readings.html', context)

@login_required
def requests_list(request):
    user_requests = Request.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.save()
            
            create_notification(
                request.user,
                f'📋 Ваша заявка "{req.title}" принята. Мы свяжемся с вами в ближайшее время.',
                f'/requests/{req.id}/'
            )
            
            messages.success(request, 'Ваша заявка принята!')
            return redirect('requests')
    else:
        form = RequestForm()
    
    context = {'form': form, 'requests': user_requests}
    return render(request, 'main/requests.html', context)

@login_required
def request_detail(request, pk):
    req = get_object_or_404(Request, pk=pk, user=request.user)
    return render(request, 'main/request_detail.html', {'request': req})

@login_required
def add_request_review(request, pk):
    """Добавить отзыв на выполненную заявку"""
    req = get_object_or_404(Request, pk=pk, user=request.user)
    
    if req.status != 'completed':
        messages.error(request, 'Отзыв можно оставить только на выполненную заявку')
        return redirect('request_detail', pk=pk)
    
    if hasattr(req, 'review'):
        messages.error(request, 'Отзыв на эту заявку уже оставлен')
        return redirect('request_detail', pk=pk)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')
        
        if 1 <= rating <= 5:
            RequestReview.objects.create(
                request=req,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Спасибо за отзыв!')
        else:
            messages.error(request, 'Пожалуйста, поставьте оценку от 1 до 5')
        
        return redirect('request_detail', pk=pk)
    
    return redirect('request_detail', pk=pk)

@login_required
def payments_list(request):
    payments = Payment.objects.filter(user=request.user).order_by('-month')
    total_debt = payments.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
    context = {'payments': payments, 'total_debt': total_debt}
    return render(request, 'main/payments.html', context)

@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        profile.phone = request.POST.get('phone')
        profile.save()
        messages.success(request, 'Профиль обновлен!')
        return redirect('dashboard')
    
    return render(request, 'main/profile_edit.html', {'profile': profile})

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        notifications.update(is_read=True)
        messages.success(request, 'Все уведомления отмечены как прочитанные')
        return redirect('notifications_list')
    
    return render(request, 'main/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications_list')

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
    return redirect('notifications_list')

@login_required
def add_employee_review(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')
        
        if 1 <= rating <= 5:
            from django.utils import timezone
            today = timezone.now().date()
            existing = EmployeeReview.objects.filter(
                employee=employee,
                user=request.user,
                created_at__date=today
            ).exists()
            
            if existing:
                messages.error(request, 'Вы уже оставляли отзыв на этого сотрудника сегодня')
            else:
                EmployeeReview.objects.create(
                    employee=employee,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, f'Спасибо за отзыв о {employee.name}!')
        else:
            messages.error(request, 'Пожалуйста, поставьте оценку от 1 до 5')
        
        return redirect('employees_rating')
    
    return render(request, 'main/add_review.html', {'employee': employee})

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
    
    context = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'categories': categories,
    }
    return render(request, 'main/statistics.html', context)

# ========== ЛИЧНЫЙ КАБИНЕТ ==========

@login_required
def dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'main/dashboard.html', {'profile': profile})

@login_required
def readings(request):
    if request.method == 'POST':
        form = MeterReadingForm(request.POST, user=request.user)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.user = request.user
            reading.month = datetime.now().strftime('%m.%Y')
            reading.save()
            messages.success(request, 'Показания успешно переданы!')
            return redirect('readings')
    else:
        form = MeterReadingForm(user=request.user)
    
    current_month = datetime.now().strftime('%m.%Y')
    user_readings = MeterReading.objects.filter(
        user=request.user, 
        month=current_month
    ).select_related('service')
    
    context = {
        'form': form,
        'readings': user_readings,
    }
    return render(request, 'main/readings.html', context)

@login_required
def requests_list(request):
    user_requests = Request.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/requests.html', {'requests': user_requests})

@login_required
def create_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('requests')
    else:
        form = RequestForm()
    
    return render(request, 'main/create_request.html', {'form': form})

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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    Profile, News, Service, MeterReading, 
    Request, HouseInfo, Notification, RequestReview
)
from .forms import MeterReadingForm, RequestForm
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum, Count, Avg
from django.contrib.auth.models import User
import json

def home(request):
    news = News.objects.all()[:5]
    services = Service.objects.all()
    context = {
        'news': news,
        'services': services,
    }
    return render(request, 'main/home.html', context)


def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    return render(request, 'main/contacts.html')


def services(request):
    services_list = Service.objects.all()
    return render(request, 'main/services.html', {'services': services_list})


@login_required
def dashboard(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None
    
    # Получаем информацию о доме (если есть)
    house_info = HouseInfo.objects.first()
    
    context = {
        'profile': profile,
        'house_info': house_info,
    }
    return render(request, 'main/dashboard.html', context)


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
def profile_edit(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
    
    if request.method == 'POST':
        profile.apartment_number = request.POST.get('apartment_number')
        profile.phone = request.POST.get('phone')
        profile.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('dashboard')
    
    context = {'profile': profile}
    return render(request, 'main/profile_edit.html', context)


@login_required
def payments(request):
    return render(request, 'main/payments.html')


@login_required
def statistics(request):
    # Статистика по заявкам
    total_requests = Request.objects.filter(user=request.user).count()
    completed_requests = Request.objects.filter(user=request.user, status='completed').count()
    pending_requests = Request.objects.filter(user=request.user, status='new').count()
    
    context = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
    }
    return render(request, 'main/statistics.html', context)


def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'main/news_detail.html', {'news': news_item})


def shutdown_calendar(request):
    return render(request, 'main/shutdown_calendar.html')


def faq(request):
    return render(request, 'main/faq.html')


def emergency(request):
    return render(request, 'main/emergency.html')


def documents(request):
    return render(request, 'main/documents.html')


def reviews(request):
    return render(request, 'main/reviews.html')


def employees_rating(request):
    return render(request, 'main/employees_rating.html')


def notifications_view(request):
    return render(request, 'main/notifications.html')


def house_info_view(request):
    return render(request, 'main/house_info.html')


def chat_bot(request):
    return render(request, 'main/chat_bot.html')

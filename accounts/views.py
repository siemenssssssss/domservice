from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.management import call_command
from django.db import connection
from .forms import UserRegisterForm
from main.models import Profile, HouseInfo

def register(request):
    # Проверяем, есть ли поле house в таблице main_profile
    column_exists = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(main_profile)")
            columns = cursor.fetchall()
            column_exists = any(col[1] == 'house_id' for col in columns)
    except Exception as e:
        column_exists = False
    
    # Если поля нет — выполняем миграцию один раз
    if not column_exists:
        try:
            call_command('makemigrations', 'main')
            call_command('migrate')
            messages.info(request, 'База данных обновлена.')
        except Exception as e:
            pass
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            selected_house = form.cleaned_data.get('house')
            Profile.objects.create(
                user=user,
                apartment_number=form.cleaned_data.get('apartment_number'),
                phone=form.cleaned_data.get('phone'),
                personal_account=f"ЛС-{user.id:06d}",
                house=selected_house
            )
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    houses = HouseInfo.objects.all()
    return render(request, 'registration/register.html', {
        'form': form,
        'houses': houses,
    })

def custom_logout(request):
    logout(request)
    return redirect('home')

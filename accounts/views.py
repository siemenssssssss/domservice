# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from main.forms import UserRegisterForm
from main.models import Profile, HouseInfo
from main.services.dadata import get_full_house_info
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            address = form.cleaned_data.get('address')
            
            # Получаем максимально полную информацию о доме
            house_data = get_full_house_info(address)
            
            if house_data and house_data.get('address_full'):
                # Проверяем, нет ли уже такого дома в базе
                house, created = HouseInfo.objects.get_or_create(
                    address_full=house_data['address_full'],
                    defaults=house_data
                )
            else:
                # Если не нашли через API — создаём с минимальными данными
                house = HouseInfo.objects.create(
                    address_full=address,
                    address_source=address
                )
            
            # Создаём профиль жильца
            Profile.objects.create(
                user=user,
                house=house,
                apartment_number=form.cleaned_data.get('apartment_number'),
                phone=form.cleaned_data.get('phone'),
                personal_account=f"ЛС-{user.id:06d}"
            )
            
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name or user.username}!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

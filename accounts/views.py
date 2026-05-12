from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from main.forms import UserRegisterForm
from main.models import Profile, HouseInfo

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            address = form.cleaned_data.get('address')
            if address:
                house, created = HouseInfo.objects.get_or_create(address=address)
            
            Profile.objects.create(
                user=user,
                apartment_number=form.cleaned_data.get('apartment_number'),
                phone=form.cleaned_data.get('phone'),
                personal_account=f"ЛС-{user.id:06d}"
            )
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

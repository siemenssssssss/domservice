from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ResidentRegistrationForm

def register(request):
    if request.method == 'POST':
        form = ResidentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = ResidentRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

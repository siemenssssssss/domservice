from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ResidentProfile

class ResidentRegistrationForm(UserCreationForm):
    apartment_number = forms.CharField(max_length=10, label='Номер квартиры')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    first_name = forms.CharField(max_length=30, label='Имя')
    last_name = forms.CharField(max_length=30, label='Фамилия')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'apartment_number', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            ResidentProfile.objects.create(
                user=user,
                apartment_number=self.cleaned_data['apartment_number'],
                phone=self.cleaned_data['phone']
            )
        return user
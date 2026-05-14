from django import forms
from .models import MeterReading, Request
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ['service', 'value']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from datetime import datetime
        if self.user:
            current_month = datetime.now().strftime('%m.%Y')
            existing_services = MeterReading.objects.filter(
                user=self.user, month=current_month
            ).values_list('service_id', flat=True)
            self.fields['service'].queryset = self.fields['service'].queryset.exclude(id__in=existing_services)

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['category', 'title', 'description', 'photo']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Кратко опишите проблему'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserRegisterForm(UserCreationForm):
    apartment_number = forms.CharField(max_length=10, label='Номер квартиры', widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, label='Телефон', widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, label='Имя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'apartment_number', 'phone', 'password1', 'password2']
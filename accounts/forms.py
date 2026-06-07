import random
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import HouseInfo

class UserRegisterForm(UserCreationForm):
    # Личные данные
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    
    # Адресные данные
    apartment_number = forms.CharField(max_length=10, required=True, label='Номер квартиры')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    house = forms.ModelChoiceField(
        queryset=HouseInfo.objects.all(),
        required=True,
        label='Выберите дом',
        empty_label='---------'
    )
    
    # Каптча
    captcha_answer = forms.IntegerField(
        label='Сколько будет 2 + 2?',
        required=True,
        widget=forms.NumberInput(attrs={'style': 'width: 80px;', 'placeholder': '?'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 
                  'apartment_number', 'phone', 'house', 'captcha_answer']
    
    def clean_captcha_answer(self):
        answer = self.cleaned_data.get('captcha_answer')
        if answer != 4:
            raise forms.ValidationError('Неверный ответ. Попробуйте ещё раз.')
        return answer

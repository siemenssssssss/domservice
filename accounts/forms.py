import random
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import HouseInfo

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    apartment_number = forms.CharField(max_length=10, required=True, label='Номер квартиры')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    house = forms.ModelChoiceField(
        queryset=HouseInfo.objects.all(),
        required=True,
        label='Выберите дом',
        empty_label='---------'
    )
    
    # Каптча с рандомными числами
    captcha_answer = forms.IntegerField(
        label='Проверка',
        required=True,
        widget=forms.NumberInput(attrs={'style': 'width: 80px;', 'placeholder': '?'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num1 = random.randint(1, 20)
        self.num2 = random.randint(1, 20)
        self.fields['captcha_answer'].label = f'{self.num1} + {self.num2} = ?'
    
    def clean_captcha_answer(self):
        answer = self.cleaned_data.get('captcha_answer')
        if answer != self.num1 + self.num2:
            raise forms.ValidationError('Неверный ответ. Попробуйте ещё раз.')
        return answer

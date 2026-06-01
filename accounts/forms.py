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
    
    # Скрытые поля для хранения чисел каптчи
    captcha_num1 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    captcha_num2 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    # Поле для ответа
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
        
        if not self.is_bound:
            # Генерируем числа при загрузке формы
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            self.initial['captcha_num1'] = num1
            self.initial['captcha_num2'] = num2
            self.fields['captcha_answer'].label = f'{num1} + {num2} = ?'
        else:
            # При отправке используем числа из данных, если они есть
            num1 = self.data.get('captcha_num1')
            num2 = self.data.get('captcha_num2')
            if num1 is not None and num2 is not None:
                self.fields['captcha_answer'].label = f'{int(num1)} + {int(num2)} = ?'
    
    def clean_captcha_answer(self):
        answer = self.cleaned_data.get('captcha_answer')
        num1 = self.cleaned_data.get('captcha_num1')
        num2 = self.cleaned_data.get('captcha_num2')
        
        # Если скрытые поля не пришли, пытаемся взять их из self.initial
        if num1 is None or num2 is None:
            num1 = self.initial.get('captcha_num1')
            num2 = self.initial.get('captcha_num2')
        
        if num1 is None or num2 is None:
            raise forms.ValidationError('Ошибка каптчи. Попробуйте обновить страницу.')
        
        if answer != num1 + num2:
            raise forms.ValidationError('Неверный ответ. Попробуйте ещё раз.')
        return answer

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ResidentProfile

class ResidentProfileInline(admin.StackedInline):
    model = ResidentProfile
    can_delete = False
    verbose_name_plural = 'Профиль жильца'

class CustomUserAdmin(UserAdmin):
    inlines = [ResidentProfileInline]
    list_display = ['username', 'get_full_name', 'email', 'get_apartment', 'get_phone', 'get_debt', 'is_staff']
    list_filter = ['is_staff', 'is_active']
    
    def get_apartment(self, obj):
        return obj.profile.apartment_number if hasattr(obj, 'profile') else '—'
    get_apartment.short_description = 'Квартира'
    
    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else '—'
    get_phone.short_description = 'Телефон'
    
    def get_debt(self, obj):
        return f"{obj.profile.total_debt} ₽" if hasattr(obj, 'profile') else '0 ₽'
    get_debt.short_description = 'Задолженность'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

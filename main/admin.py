from django.contrib import admin
from .models import (
    Profile, News, Service, MeterReading, 
    Request, HouseInfo, Notification, RequestReview
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'apartment_number', 'phone', 'personal_account']
    list_filter = ['apartment_number']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'apartment_number']
    readonly_fields = ['personal_account']
    fields = ['user', 'apartment_number', 'phone', 'personal_account', 'house']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_posted', 'is_important']
    list_filter = ['is_important', 'date_posted']
    search_fields = ['title', 'content']
    date_hierarchy = 'date_posted'
    fields = ['title', 'content', 'image', 'is_important']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'price']
    list_filter = ['unit']
    search_fields = ['name']
    fields = ['name', 'unit', 'price']


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'value', 'month', 'date_submitted']
    list_filter = ['month', 'service']
    search_fields = ['user__username', 'service__name']
    date_hierarchy = 'date_submitted'
    readonly_fields = ['date_submitted']
    fields = ['user', 'service', 'value', 'month', 'date_submitted']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    fields = ['user', 'category', 'title', 'description', 'photo', 'status', 'admin_comment', 'created_at']
    readonly_fields = ['created_at']


@admin.register(HouseInfo)
class HouseInfoAdmin(admin.ModelAdmin):
    list_display = ['address_full', 'building_year', 'floors', 'city']
    search_fields = ['address_full', 'city', 'street']
    list_filter = ['building_year', 'floors']
    fieldsets = (
        ('Адрес', {
            'fields': ('address_full', 'address_source', 'postal_code', 'country', 'federal_district', 'timezone')
        }),
        ('Регион и город', {
            'fields': ('region', 'region_type', 'area', 'city', 'city_district', 'settlement')
        }),
        ('Улица и дом', {
            'fields': ('street', 'street_type', 'house', 'house_type', 'block', 'flat', 'flat_area')
        }),
        ('Характеристики дома', {
            'fields': ('building_year', 'floors', 'flat_count', 'material', 'cadastral_number')
        }),
        ('Координаты', {
            'fields': ('geo_lat', 'geo_lon', 'geo_quality')
        }),
        ('Данные вручную', {
            'fields': ('managing_company', 'emergency_phone', 'entrances')
        }),
    )
    readonly_fields = ['fias_id', 'house_fias_id', 'street_fias_id', 'qc', 'qc_geo', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['created_at']
    fields = ['user', 'message', 'link', 'is_read', 'created_at']


@admin.register(RequestReview)
class RequestReviewAdmin(admin.ModelAdmin):
    list_display = ['request', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['request__title', 'comment']
    readonly_fields = ['created_at']
    fields = ['request', 'rating', 'comment', 'created_at']

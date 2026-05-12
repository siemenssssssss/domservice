from django.contrib import admin
from .models import (
    Profile, News, Service, MeterReading, 
    Request, Payment, HouseInfo, Document, 
    Notification, RequestReview, ShutdownSchedule,
    Employee, EmployeeReview
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'apartment_number', 'phone', 'personal_account']
    list_filter = ['apartment_number']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'apartment_number']
    readonly_fields = ['personal_account']
    fields = ['user', 'apartment_number', 'phone', 'personal_account']


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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'amount', 'is_paid', 'paid_at']
    list_filter = ['month', 'is_paid']
    search_fields = ['user__username']
    fields = ['user', 'month', 'amount', 'is_paid', 'paid_at']
    readonly_fields = ['paid_at']


@admin.register(HouseInfo)
class HouseInfoAdmin(admin.ModelAdmin):
    list_display = ['address', 'building_year', 'floors', 'flat_count', 'emergency_phone']
    list_filter = ['building_year', 'floors']
    search_fields = ['address', 'managing_company']
    fieldsets = (
        ('Основная информация', {
            'fields': ('address', 'building_year', 'floors', 'entrances', 'flat_count', 'total_area')
        }),
        ('Контактная информация', {
            'fields': ('managing_company', 'chief_engineer', 'emergency_phone', 'description')
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'date_posted', 'is_public']
    list_filter = ['document_type', 'is_public', 'date_posted']
    search_fields = ['title', 'description']
    date_hierarchy = 'date_posted'
    fields = ['title', 'document_type', 'file', 'description', 'is_public']


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


@admin.register(ShutdownSchedule)
class ShutdownScheduleAdmin(admin.ModelAdmin):
    list_display = ['service_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['service_type', 'is_active']
    search_fields = ['address', 'description']
    date_hierarchy = 'start_date'
    fields = ['service_type', 'start_date', 'end_date', 'address', 'description', 'is_active']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'rating', 'is_active']
    list_filter = ['position', 'is_active']
    search_fields = ['name', 'position']
    fields = ['user', 'name', 'position', 'photo', 'rating', 'is_active', 'description', 'experience']


@admin.register(EmployeeReview)
class EmployeeReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['employee__name', 'comment']
    readonly_fields = ['created_at']
    fields = ['employee', 'user', 'request', 'rating', 'comment', 'created_at']

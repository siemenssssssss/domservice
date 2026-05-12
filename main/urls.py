from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('services/', views.services_page, name='services'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('readings/', views.readings, name='readings'),
    path('requests/', views.requests_list, name='requests'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('request/<int:pk>/add-review/', views.add_request_review, name='add_request_review'),
    path('payments/', views.payments_list, name='payments'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('employees/', views.employees_rating, name='employees_rating'),
    path('employees/<int:employee_id>/review/', views.add_employee_review, name='add_employee_review'),
    path('house-info/', views.house_info, name='house_info'),
    path('documents/', views.documents_list, name='documents'),
    path('faq/', views.faq, name='faq'),
    path('emergency/', views.emergency, name='emergency'),
    path('shutdown-calendar/', views.shutdown_calendar, name='shutdown_calendar'),
    path('statistics/', views.statistics, name='statistics'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
]

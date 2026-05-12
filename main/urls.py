from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('services/', views.services, name='services'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('readings/', views.readings, name='readings'),
    path('requests/', views.requests_list, name='requests'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('payments/', views.payments, name='payments'),
    path('statistics/', views.statistics, name='statistics'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('shutdown-calendar/', views.shutdown_calendar, name='shutdown_calendar'),
    path('faq/', views.faq, name='faq'),
    path('emergency/', views.emergency, name='emergency'),
    path('documents/', views.documents, name='documents'),
    path('reviews/', views.reviews, name='reviews'),
    path('employees-rating/', views.employees_rating, name='employees_rating'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('house-info/', views.house_info_view, name='house_info'),
    path('chat-bot/', views.chat_bot, name='chat_bot'),
]

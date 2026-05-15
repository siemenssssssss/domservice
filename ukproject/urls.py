from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.management import call_command

def setup_all(request):
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        
        call_command('loaddata', 'initial_data.json')
        
        return HttpResponse('✅ ГОТОВО! Админ: admin / admin123. Данные загружены.')
    except Exception as e:
        return HttpResponse(f'❌ Ошибка: {e}')

urlpatterns = [
    path('setup/', setup_all),
    path('go/', setup_all),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

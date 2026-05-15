from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.management import call_command

# --- ВРЕМЕННЫЕ ФУНКЦИИ (удали после загрузки данных) ---
def create_admin(request):
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            return HttpResponse('✅ Админ создан! Логин: admin, Пароль: admin123')
        else:
            return HttpResponse('⚠️ Админ уже существует')
    except Exception as e:
        return HttpResponse(f'❌ Ошибка: {e}')

def load_data(request):
    try:
        call_command('loaddata', 'initial_data.json')
        return HttpResponse('✅ Данные успешно загружены!')
    except Exception as e:
        return HttpResponse(f'❌ Ошибка: {e}')
# -------------------------------------------------------

urlpatterns = [
    # --- ВРЕМЕННЫЕ URL (удали после загрузки) ---
    path('create-admin/', create_admin),
    path('load-data/', load_data),
    # -------------------------------------------
    
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

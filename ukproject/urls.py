from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.core.management import call_command

# ========== ВРЕМЕННЫЙ ЭНДПОИНТ ДЛЯ МИГРАЦИИ ==========
def run_migrations(request):
    try:
        call_command('makemigrations', 'main')
        call_command('migrate')
        return HttpResponse('✅ Миграции выполнены успешно! Поле house добавлено.')
    except Exception as e:
        return HttpResponse(f'❌ Ошибка: {e}')
# =====================================================

urlpatterns = [
    path('migrate/', run_migrations),  # ВРЕМЕННЫЙ URL - УДАЛИ ПОТОМ
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

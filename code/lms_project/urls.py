from django.contrib import admin
from django.urls import path, include

# Import settings dan static/media handlers (penting untuk Docker)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin page
    path('admin/', admin.site.urls),
    
    # URL Autentikasi Bawaan Django (login, logout, password change, dll.)
    # Ini akan menyediakan name='login' dan name='logout'
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Core App URLs
    path('', include('core.urls')),
]

# Tambahkan URL untuk file MEDIA dan STATIC saat DEVELOPMENT (Pentig untuk Docker)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

"""
URL configuration for petcare_core project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.usuarios.views import dashboard_view

# Personalización del Admin de Django
admin.site.site_header = "🐾 PetCare - Sistema de Gestión Veterinaria"
admin.site.site_title = "PetCare Administración"
admin.site.index_title = "Panel de Control Clínico y Gestión"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('usuarios/', include('apps.usuarios.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('citas/', include('apps.citas.urls')),
    path('fichas/', include('apps.fichas.urls')),
    path('recordatorios/', include('apps.recordatorios.urls')),
    path('api/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

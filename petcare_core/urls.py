"""
URL configuration for petcare_core project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
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


def redirect_to_dashboard(request, *args, **kwargs):
    """Redirige cualquier ruta no encontrada hacia el dashboard principal."""
    return redirect('dashboard')


def error_404_handler(request, exception=None):
    """Manejador de error 404 cuando se invoca Http404 o get_object_or_404."""
    return redirect('dashboard')


# Handler 404 para Django
handler404 = error_404_handler

# Catch-all re_path: captura cualquier ruta inexistente y la redirige al Dashboard
urlpatterns += [
    re_path(r'^.*$', redirect_to_dashboard, name='catch_all_redirect'),
]

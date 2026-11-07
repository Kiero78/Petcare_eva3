from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Tutores
    path('tutores/', views.tutor_lista, name='tutor_lista'),
    path('tutores/nuevo/', views.tutor_crear, name='tutor_crear'),
    path('tutores/<int:pk>/', views.tutor_detalle, name='tutor_detalle'),
    path('tutores/<int:pk>/editar/', views.tutor_editar, name='tutor_editar'),
    path('tutores/<int:pk>/eliminar/', views.tutor_eliminar, name='tutor_eliminar'),

    # Mascotas
    path('mascotas/', views.mascota_lista, name='mascota_lista'),
    path('mascotas/nueva/', views.mascota_crear, name='mascota_crear'),
    path('mascotas/<int:pk>/', views.mascota_detalle, name='mascota_detalle'),
    path('mascotas/<int:pk>/editar/', views.mascota_editar, name='mascota_editar'),

    # Endpoints asíncronos para frontend
    path('api/tutor/<int:tutor_id>/mascotas/', views.api_mascotas_por_tutor, name='api_mascotas_por_tutor'),
    path('api/especie/<int:especie_id>/razas/', views.api_razas_por_especie, name='api_razas_por_especie'),
]

from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('calendario/', views.calendario_citas, name='calendario'),
    path('lista/', views.citas_lista, name='citas_lista'),
    path('nueva/', views.cita_crear, name='cita_crear'),
    path('<int:pk>/', views.cita_detalle, name='cita_detalle'),
    path('<int:pk>/estado/<str:nuevo_estado>/', views.cita_cambiar_estado, name='cita_cambiar_estado'),

    # APIs para calendario y validación
    path('api/eventos/', views.api_citas_eventos, name='api_citas_eventos'),
    path('api/verificar-solapamiento/', views.api_verificar_solapamiento, name='api_verificar_solapamiento'),

    # Horarios de disponibilidad por profesional
    path('disponibilidad/', views.disponibilidad_lista, name='disponibilidad_lista'),
    path('disponibilidad/nueva/', views.disponibilidad_crear, name='disponibilidad_crear'),
]

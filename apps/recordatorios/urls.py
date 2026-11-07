from django.urls import path
from . import views

app_name = 'recordatorios'

urlpatterns = [
    path('panel/', views.panel_recordatorios, name='panel'),
    path('vacunacion/nueva/', views.vacunacion_registrar, name='vacunacion_registrar'),
    path('nuevo/', views.recordatorio_crear, name='recordatorio_crear'),
    path('<int:pk>/estado/<str:nuevo_estado>/', views.recordatorio_cambiar_estado, name='recordatorio_cambiar_estado'),
    path('<int:pk>/whatsapp/', views.recordatorio_enviar_whatsapp, name='recordatorio_enviar_whatsapp'),
]

from django.urls import path
from . import views

app_name = 'fichas'

urlpatterns = [
    path('mascota/<int:mascota_id>/', views.ficha_detalle, name='ficha_detalle'),
    path('mascota/<int:mascota_id>/editar/', views.ficha_editar, name='ficha_editar'),
    path('mascota/<int:mascota_id>/atencion/nueva/', views.atencion_crear, name='atencion_crear'),
    path('cita/<int:cita_id>/atencion/nueva/', views.atencion_crear_desde_cita, name='atencion_crear_desde_cita'),
    path('atencion/<int:pk>/', views.atencion_detalle, name='atencion_detalle'),

    # Recetas y Exámenes
    path('atencion/<int:atencion_id>/receta/nueva/', views.receta_agregar, name='receta_agregar'),
    path('receta/<int:pk>/eliminar/', views.receta_eliminar, name='receta_eliminar'),
    path('atencion/<int:atencion_id>/receta/imprimir/', views.receta_imprimir, name='receta_imprimir'),
    path('atencion/<int:atencion_id>/examen/nuevo/', views.examen_agregar, name='examen_agregar'),
]

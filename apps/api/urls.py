from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TutorViewSet, MascotaViewSet, CitaViewSet,
    FichaClinicaViewSet, AtencionClinicaViewSet,
    RecordatorioViewSet, RegistroVacunacionViewSet
)

router = DefaultRouter()
router.register(r'tutores', TutorViewSet, basename='api-tutores')
router.register(r'mascotas', MascotaViewSet, basename='api-mascotas')
router.register(r'citas', CitaViewSet, basename='api-citas')
router.register(r'fichas', FichaClinicaViewSet, basename='api-fichas')
router.register(r'atenciones', AtencionClinicaViewSet, basename='api-atenciones')
router.register(r'recordatorios', RecordatorioViewSet, basename='api-recordatorios')
router.register(r'vacunaciones', RegistroVacunacionViewSet, basename='api-vacunaciones')

urlpatterns = [
    path('', include(router.urls)),
]

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.clientes.models import Tutor, Mascota, Especie, Raza
from apps.citas.models import Cita, HorarioDisponibilidad
from apps.fichas.models import FichaClinica, AtencionClinica, RecetaMedica, ExamenClinico
from apps.recordatorios.models import TipoVacuna, RegistroVacunacion, Recordatorio

from .serializers import (
    TutorSerializer, MascotaSerializer, EspecieSerializer, RazaSerializer,
    CitaSerializer, FichaClinicaSerializer, AtencionClinicaSerializer,
    RecetaMedicaSerializer, ExamenClinicoSerializer,
    RecordatorioSerializer, RegistroVacunacionSerializer
)


class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all().prefetch_related('mascotas')
    serializer_class = TutorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['rut', 'nombres', 'apellidos', 'telefono_principal', 'correo']


class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all().select_related('tutor', 'especie', 'raza')
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'numero_microchip', 'tutor__nombres', 'tutor__apellidos', 'tutor__rut']


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all().select_related('tutor', 'mascota', 'veterinario')
    serializer_class = CitaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['mascota__nombre', 'tutor__nombres', 'tutor__apellidos', 'motivo']


class FichaClinicaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FichaClinica.objects.all().select_related('mascota').prefetch_related('atenciones__recetas', 'atenciones__examenes')
    serializer_class = FichaClinicaSerializer
    permission_classes = [permissions.IsAuthenticated]


class AtencionClinicaViewSet(viewsets.ModelViewSet):
    queryset = AtencionClinica.objects.all().select_related('ficha__mascota', 'veterinario')
    serializer_class = AtencionClinicaSerializer
    permission_classes = [permissions.IsAuthenticated]


class RecordatorioViewSet(viewsets.ModelViewSet):
    queryset = Recordatorio.objects.all().select_related('mascota', 'tutor')
    serializer_class = RecordatorioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'descripcion', 'mascota__nombre', 'tutor__nombres', 'tutor__apellidos']


class RegistroVacunacionViewSet(viewsets.ModelViewSet):
    queryset = RegistroVacunacion.objects.all().select_related('mascota', 'tipo_vacuna', 'veterinario')
    serializer_class = RegistroVacunacionSerializer
    permission_classes = [permissions.IsAuthenticated]

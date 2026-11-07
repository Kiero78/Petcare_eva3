from rest_framework import serializers
from apps.clientes.models import Tutor, Mascota, Especie, Raza
from apps.citas.models import Cita, HorarioDisponibilidad
from apps.fichas.models import FichaClinica, AtencionClinica, RecetaMedica, ExamenClinico
from apps.recordatorios.models import TipoVacuna, RegistroVacunacion, Recordatorio
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class EspecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = '__all__'


class RazaSerializer(serializers.ModelSerializer):
    especie_nombre = serializers.ReadOnlyField(source='especie.nombre')

    class Meta:
        model = Raza
        fields = ['id', 'especie', 'especie_nombre', 'nombre']


class MascotaSerializer(serializers.ModelSerializer):
    especie_nombre = serializers.ReadOnlyField(source='especie.nombre')
    raza_nombre = serializers.ReadOnlyField(source='raza.nombre')
    tutor_nombre = serializers.ReadOnlyField(source='tutor.nombre_completo')
    edad_texto = serializers.ReadOnlyField(source='edad')

    class Meta:
        model = Mascota
        fields = [
            'id', 'tutor', 'tutor_nombre', 'nombre', 'especie', 'especie_nombre',
            'raza', 'raza_nombre', 'sexo', 'esterilizado', 'fecha_nacimiento',
            'edad_texto', 'color', 'numero_microchip', 'peso_actual_kg',
            'alergias_conocidas', 'condiciones_preexistentes', 'fallecido'
        ]


class TutorSerializer(serializers.ModelSerializer):
    mascotas = MascotaSerializer(many=True, read_only=True)

    class Meta:
        model = Tutor
        fields = [
            'id', 'rut', 'nombres', 'apellidos', 'nombre_completo',
            'correo', 'telefono_principal', 'telefono_secundario',
            'direccion', 'comuna', 'activo', 'observaciones', 'mascotas'
        ]


class CitaSerializer(serializers.ModelSerializer):
    tutor_nombre = serializers.ReadOnlyField(source='tutor.nombre_completo')
    mascota_nombre = serializers.ReadOnlyField(source='mascota.nombre')
    veterinario_nombre = serializers.ReadOnlyField(source='veterinario.get_full_name')

    class Meta:
        model = Cita
        fields = [
            'id', 'tutor', 'tutor_nombre', 'mascota', 'mascota_nombre',
            'veterinario', 'veterinario_nombre', 'fecha', 'hora_inicio',
            'hora_fin', 'tipo_cita', 'estado', 'motivo', 'observaciones'
        ]

    def validate(self, attrs):
        # Validación de solapamiento en DRF
        hora_inicio = attrs.get('hora_inicio')
        hora_fin = attrs.get('hora_fin')
        fecha = attrs.get('fecha')
        veterinario = attrs.get('veterinario')

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError({"hora_fin": "La hora de fin debe ser mayor a la hora de inicio."})

        # Consulta de solapamiento
        instancia_id = self.instance.id if self.instance else None
        solapadas = Cita.objects.filter(
            veterinario=veterinario,
            fecha=fecha
        ).exclude(estado='CANCELADA').filter(
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        )
        if instancia_id:
            solapadas = solapadas.exclude(id=instancia_id)

        if solapadas.exists():
            conflicto = solapadas.first()
            raise serializers.ValidationError({
                "non_field_errors": [
                    f"Conflicto de horario: El veterinario ya tiene la Cita #{conflicto.id} ({conflicto.mascota.nombre}) de {conflicto.hora_inicio} a {conflicto.hora_fin}."
                ]
            })
        return attrs


class RecetaMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecetaMedica
        fields = '__all__'


class ExamenClinicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenClinico
        fields = '__all__'


class AtencionClinicaSerializer(serializers.ModelSerializer):
    recetas = RecetaMedicaSerializer(many=True, read_only=True)
    examenes = ExamenClinicoSerializer(many=True, read_only=True)
    veterinario_nombre = serializers.ReadOnlyField(source='veterinario.get_full_name')

    class Meta:
        model = AtencionClinica
        fields = '__all__'


class FichaClinicaSerializer(serializers.ModelSerializer):
    atenciones = AtencionClinicaSerializer(many=True, read_only=True)
    mascota_nombre = serializers.ReadOnlyField(source='mascota.nombre')

    class Meta:
        model = FichaClinica
        fields = '__all__'


class RecordatorioSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.ReadOnlyField(source='mascota.nombre')
    tutor_nombre = serializers.ReadOnlyField(source='tutor.nombre_completo')
    esta_vencido = serializers.ReadOnlyField()
    dias_restantes = serializers.ReadOnlyField()

    class Meta:
        model = Recordatorio
        fields = '__all__'


class RegistroVacunacionSerializer(serializers.ModelSerializer):
    vacuna_nombre = serializers.ReadOnlyField(source='tipo_vacuna.nombre')
    mascota_nombre = serializers.ReadOnlyField(source='mascota.nombre')

    class Meta:
        model = RegistroVacunacion
        fields = '__all__'

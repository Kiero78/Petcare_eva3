from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.clientes.models import Tutor, Mascota


class HorarioDisponibilidad(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    veterinario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='horarios_disponibilidad',
        verbose_name='Médico Veterinario'
    )
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, verbose_name='Día de la Semana')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio de Jornada')
    hora_fin = models.TimeField(verbose_name='Hora de Fin de Jornada')
    duracion_bloque_minutos = models.PositiveIntegerField(
        default=30,
        verbose_name='Duración Promedio de Cita (minutos)'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Horario de Disponibilidad'
        verbose_name_plural = 'Horarios de Disponibilidad'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ('veterinario', 'dia_semana', 'hora_inicio')

    def __str__(self):
        return f"{self.veterinario.get_full_name() or self.veterinario.username} - {self.get_dia_semana_display()} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')})"

    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin de jornada.")


class Cita(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('EN_ATENCION', 'En Atención'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
        ('NO_ASISTIO', 'No Asistió'),
    ]

    TIPOS_CITA = [
        ('CONSULTA', 'Consulta General'),
        ('VACUNACION', 'Vacunación y Desparasitación'),
        ('CONTROL', 'Control Médico Periódico'),
        ('POST_OP', 'Control Post-Operatorio'),
        ('CIRUGIA', 'Procedimiento Quirúrgico'),
        ('URGENCIA', 'Urgencia Médica'),
        ('EXAMENES', 'Toma de Muestras / Exámenes'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='citas', verbose_name='Tutor')
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas', verbose_name='Mascota')
    veterinario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='citas_asignadas',
        verbose_name='Médico Veterinario'
    )
    fecha = models.DateField(verbose_name='Fecha de la Cita')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Término')
    tipo_cita = models.CharField(max_length=20, choices=TIPOS_CITA, default='CONSULTA', verbose_name='Tipo de Cita')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', verbose_name='Estado')
    motivo = models.TextField(verbose_name='Motivo de la Consulta')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones o Notas Internas')
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='citas_creadas', verbose_name='Registrado por'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Agendamiento')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')

    class Meta:
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médicas'
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"Cita #{self.id}: {self.mascota.nombre} con Dr(a). {self.veterinario.last_name or self.veterinario.username} el {self.fecha} a las {self.hora_inicio.strftime('%H:%M')}"

    def clean(self):
        """
        Regla de negocio fundamental: Prevenir solapamiento de citas médicas.
        1. hora_inicio < hora_fin
        2. El veterinario no puede tener otra cita no-cancelada en el mismo intervalo.
        3. La mascota no puede tener otra cita no-cancelada al mismo tiempo.
        """
        if self.hora_inicio and self.hora_fin:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError({
                    'hora_fin': "La hora de término debe ser posterior a la hora de inicio."
                })

            if self.estado != 'CANCELADA' and self.veterinario_id and self.fecha:
                # Verificar solapamiento para el profesional
                citas_solapadas_vet = Cita.objects.filter(
                    veterinario=self.veterinario,
                    fecha=self.fecha
                ).exclude(pk=self.pk).exclude(estado='CANCELADA').filter(
                    hora_inicio__lt=self.hora_fin,
                    hora_fin__gt=self.hora_inicio
                )

                if citas_solapadas_vet.exists():
                    cita_conflicto = citas_solapadas_vet.first()
                    raise ValidationError(
                        f"¡Solapamiento detectado! El Dr(a). {self.veterinario.get_full_name() or self.veterinario.username} "
                        f"ya tiene agendada la Cita #{cita_conflicto.id} ({cita_conflicto.mascota.nombre}) "
                        f"en el horario {cita_conflicto.hora_inicio.strftime('%H:%M')} - {cita_conflicto.hora_fin.strftime('%H:%M')}."
                    )

                # Verificar solapamiento para la misma mascota
                if self.mascota_id:
                    citas_solapadas_mascota = Cita.objects.filter(
                        mascota=self.mascota,
                        fecha=self.fecha
                    ).exclude(pk=self.pk).exclude(estado='CANCELADA').filter(
                        hora_inicio__lt=self.hora_fin,
                        hora_fin__gt=self.hora_inicio
                    )

                    if citas_solapadas_mascota.exists():
                        raise ValidationError(
                            f"La mascota {self.mascota.nombre} ya tiene otra cita agendada en ese mismo rango horario."
                        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

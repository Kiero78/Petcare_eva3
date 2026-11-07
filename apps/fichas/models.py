from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.clientes.models import Mascota
from apps.citas.models import Cita


class FichaClinica(models.Model):
    """
    Ficha digital centralizada por mascota para evitar pérdida de registros en papel.
    """
    mascota = models.OneToOneField(
        Mascota, on_delete=models.CASCADE,
        related_name='ficha_clinica',
        verbose_name='Mascota'
    )
    numero_ficha = models.CharField(max_length=30, unique=True, verbose_name='N° de Ficha Clínica')
    grupo_sanguineo = models.CharField(max_length=30, blank=True, verbose_name='Grupo Sanguíneo')
    antecedentes_quirurgicos = models.TextField(blank=True, verbose_name='Cirugías y Procedimientos Previos')
    enfermedades_cronicas = models.TextField(blank=True, verbose_name='Enfermedades Crónicas / Diagnósticos Base')
    alertas_medicas = models.TextField(
        blank=True,
        verbose_name='Alertas Médicas Críticas',
        help_text='Ej: Alergia a Penicilina, agresivo por dolor, riesgo anestésico alto.'
    )
    fecha_apertura = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Apertura')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Ficha Clínica Digital'
        verbose_name_plural = 'Fichas Clínicas Digitales'

    def __str__(self):
        return f"Ficha {self.numero_ficha} - {self.mascota.nombre} ({self.mascota.especie.nombre})"

    def save(self, *args, **kwargs):
        if not self.numero_ficha:
            # Generar número correlativo automático ej: FC-2026-0001
            ultimo = FichaClinica.objects.all().order_by('id').last()
            siguiente_id = 1 if not ultimo else ultimo.id + 1
            anio = timezone.now().year
            self.numero_ficha = f"FC-{anio}-{siguiente_id:04d}"
        super().save(*args, **kwargs)


class AtencionClinica(models.Model):
    """
    Registro detallado de una consulta o atención médica presencial.
    """
    MUCOSAS_CHOICES = [
        ('ROSADAS', 'Rosadas (Normal)'),
        ('PALIDAS', 'Pálidas (Anemia / Hipovolemia)'),
        ('CIANOTICAS', 'Cianóticas (Hipoxia)'),
        ('ICTERICAS', 'Ictéricas (Afección Hepática)'),
        ('CONGESTIVAS', 'Congestivas / Hiperémicas'),
    ]

    ficha = models.ForeignKey(
        FichaClinica, on_delete=models.CASCADE,
        related_name='atenciones',
        verbose_name='Ficha Clínica'
    )
    cita = models.OneToOneField(
        Cita, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='atencion_clinica',
        verbose_name='Cita Asociada'
    )
    veterinario = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='atenciones_realizadas',
        verbose_name='Médico Veterinario Tratante'
    )
    fecha_atencion = models.DateTimeField(default=timezone.now, verbose_name='Fecha y Hora de Atención')

    # Anamnesis y Motivo
    motivo_consulta = models.CharField(max_length=255, verbose_name='Motivo de Consulta')
    anamnesis = models.TextField(verbose_name='Anamnesis / Historia del Cuadro Clínico')

    # Examen Clínico y Signos Vitales
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Peso (Kg)')
    temperatura_c = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Temperatura (°C)')
    frecuencia_cardiaca_lpm = models.PositiveIntegerField(null=True, blank=True, verbose_name='FC (latidos/min)')
    frecuencia_respiratoria_rpm = models.PositiveIntegerField(null=True, blank=True, verbose_name='FR (respiraciones/min)')
    tiempo_llenado_capilar_seg = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='TLLC (segundos)')
    mucosas = models.CharField(max_length=20, choices=MUCOSAS_CHOICES, default='ROSADAS', verbose_name='Estado de Mucosas')
    examen_fisico = models.TextField(verbose_name='Hallazgos del Examen Físico')

    # Diagnóstico y Tratamiento
    diagnostico_principal = models.TextField(verbose_name='Diagnóstico Presuntivo / Definitivo')
    diagnosticos_diferenciales = models.TextField(blank=True, verbose_name='Diagnósticos Diferenciales')
    tratamiento_aplicado = models.TextField(verbose_name='Tratamiento Aplicado en Clínica')
    indicaciones_tutor = models.TextField(verbose_name='Indicaciones y Cuidados para el Hogar')

    # Control posterior
    requiere_control = models.BooleanField(default=False, verbose_name='¿Requiere Control Posterior?')
    dias_proximo_control = models.PositiveIntegerField(null=True, blank=True, verbose_name='Días para Próximo Control')

    class Meta:
        verbose_name = 'Atención Médica'
        verbose_name_plural = 'Atenciones Médicas'
        ordering = ['-fecha_atencion']

    def __str__(self):
        return f"Atención {self.fecha_atencion.strftime('%d/%m/%Y')} - {self.ficha.mascota.nombre} (Dr(a). {self.veterinario.last_name})"

    def save(self, *args, **kwargs):
        # Al guardar una atención, actualizar peso actual de la mascota
        super().save(*args, **kwargs)
        if self.peso_kg > 0:
            mascota = self.ficha.mascota
            mascota.peso_actual_kg = self.peso_kg
            mascota.save(update_fields=['peso_actual_kg'])


class RecetaMedica(models.Model):
    """
    Prescripción médica emitida durante una atención.
    """
    atencion = models.ForeignKey(
        AtencionClinica, on_delete=models.CASCADE,
        related_name='recetas',
        verbose_name='Atención Médica'
    )
    medicamento = models.CharField(max_length=150, verbose_name='Medicamento / Principio Activo')
    presentacion = models.CharField(max_length=100, blank=True, verbose_name='Presentación (ej. Comprimidos 50mg, Jarabe)')
    dosis = models.CharField(max_length=100, verbose_name='Dosis (ej. 1/2 comprimido, 2.5 ml)')
    frecuencia = models.CharField(max_length=100, verbose_name='Frecuencia (ej. Cada 12 horas)')
    duracion = models.CharField(max_length=100, verbose_name='Duración del Tratamiento (ej. 7 días)')
    indicaciones_especiales = models.TextField(blank=True, verbose_name='Indicaciones Especiales (con alimentos, en ayunas, etc.)')

    class Meta:
        verbose_name = 'Receta Médica'
        verbose_name_plural = 'Recetas Médicas'

    def __str__(self):
        return f"{self.medicamento} - {self.dosis} ({self.frecuencia})"


class ExamenClinico(models.Model):
    """
    Exámenes de laboratorio o imágenes complementarias.
    """
    ESTADOS_EXAMEN = [
        ('SOLICITADO', 'Solicitado'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado / Con Resultados'),
        ('CANCELADO', 'Cancelado'),
    ]

    atencion = models.ForeignKey(
        AtencionClinica, on_delete=models.CASCADE,
        related_name='examenes',
        verbose_name='Atención Médica'
    )
    nombre_examen = models.CharField(max_length=150, verbose_name='Nombre del Examen (ej: Hemograma, Perfil Bioquímico, Ecografía Abdominal)')
    tipo_examen = models.CharField(max_length=80, verbose_name='Categoría (Sangre, Imagen, Orina, Biopsia, etc.)')
    justificacion_clinica = models.TextField(verbose_name='Justificación / Sospecha Clínica')
    estado = models.CharField(max_length=20, choices=ESTADOS_EXAMEN, default='SOLICITADO', verbose_name='Estado del Examen')
    resultado_informe = models.TextField(blank=True, verbose_name='Informe o Conclusión del Examen')
    archivo_adjunto = models.FileField(upload_to='examenes_adjuntos/', blank=True, null=True, verbose_name='Archivo de Resultados (PDF/Imagen)')
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')
    fecha_resultado = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Carga de Resultado')

    class Meta:
        verbose_name = 'Examen Clínico'
        verbose_name_plural = 'Exámenes Clínicos'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.nombre_examen} ({self.get_estado_display()}) - {self.atencion.ficha.mascota.nombre}"

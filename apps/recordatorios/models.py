from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from apps.clientes.models import Mascota, Tutor, Especie


class TipoVacuna(models.Model):
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name='vacunas_disponibles', verbose_name='Especie')
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Vacuna')
    descripcion = models.TextField(blank=True, verbose_name='Descripción y Patógenos Protegidos')
    periodicidad_meses = models.PositiveIntegerField(default=12, verbose_name='Periodicidad de Refuerzo (en meses)')
    obligatoria = models.BooleanField(default=True, verbose_name='¿Es Obligatoria según Esquema Sanitario?')

    class Meta:
        verbose_name = 'Tipo de Vacuna'
        verbose_name_plural = 'Tipos de Vacunas'
        unique_together = ('especie', 'nombre')
        ordering = ['especie__nombre', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.especie.nombre}) - Cada {self.periodicidad_meses} meses"


class RegistroVacunacion(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='vacunaciones', verbose_name='Mascota')
    tipo_vacuna = models.ForeignKey(TipoVacuna, on_delete=models.PROTECT, verbose_name='Vacuna')
    veterinario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Profesional que Administró')
    fecha_aplicacion = models.DateField(default=date.today, verbose_name='Fecha de Aplicación')
    fecha_proxima_dosis = models.DateField(verbose_name='Fecha de Próxima Dosis / Refuerzo')
    numero_lote = models.CharField(max_length=60, blank=True, verbose_name='N° de Lote de Vacuna')
    laboratorio = models.CharField(max_length=100, blank=True, verbose_name='Laboratorio Fabricante')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones o Reacciones Adversas')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Vacunación'
        verbose_name_plural = 'Registros de Vacunación'
        ordering = ['-fecha_aplicacion']

    def __str__(self):
        return f"{self.tipo_vacuna.nombre} aplicada a {self.mascota.nombre} el {self.fecha_aplicacion}"

    def save(self, *args, **kwargs):
        # Si no se definió fecha_proxima_dosis, calcular según la periodicidad
        if not self.fecha_proxima_dosis and self.tipo_vacuna and self.fecha_aplicacion:
            dias_refuerzo = self.tipo_vacuna.periodicidad_meses * 30
            self.fecha_proxima_dosis = self.fecha_aplicacion + timedelta(days=dias_refuerzo)
        super().save(*args, **kwargs)

        # Generar o actualizar automáticamente un recordatorio para el refuerzo
        Recordatorio.objects.update_or_create(
            mascota=self.mascota,
            tipo='VACUNACION',
            fecha_programada=self.fecha_proxima_dosis,
            defaults={
                'tutor': self.mascota.tutor,
                'titulo': f"Refuerzo de {self.tipo_vacuna.nombre} para {self.mascota.nombre}",
                'descripcion': f"Le corresponde a {self.mascota.nombre} su vacuna de refuerzo ({self.tipo_vacuna.nombre}). Contactar al tutor.",
                'estado': 'PENDIENTE',
                'medio_envio': 'WHATSAPP',
            }
        )


class Recordatorio(models.Model):
    TIPOS = [
        ('VACUNACION', 'Refuerzo de Vacunación'),
        ('DESPARASITACION_INT', 'Desparasitación Interna'),
        ('DESPARASITACION_EXT', 'Desparasitación Externa (Antipulgas/Garrapatas)'),
        ('CONTROL_PERIODICO', 'Control Sanitario Anual / Semestral'),
        ('POST_OP', 'Control Post-Quirúrgico'),
        ('EXAMEN_SEGUIMIENTO', 'Repetición de Examen / Laboratorio'),
        ('OTRO', 'Otro Recordatorio Preventivo'),
    ]

    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Notificación'),
        ('ENVIADO', 'Recordatorio Enviado al Tutor'),
        ('CONFIRMADO', 'Cita Agendada / Confirmada'),
        ('VENCIDO', 'Vencido / No Realizado'),
        ('CANCELADO', 'Descartado'),
    ]

    MEDIOS = [
        ('WHATSAPP', 'WhatsApp'),
        ('EMAIL', 'Correo Electrónico'),
        ('TELEFONO', 'Llamada Telefónica'),
        ('SISTEMA', 'Notificación en Sistema'),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='recordatorios', verbose_name='Mascota')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='recordatorios', verbose_name='Tutor')
    tipo = models.CharField(max_length=30, choices=TIPOS, default='VACUNACION', verbose_name='Tipo de Recordatorio')
    titulo = models.CharField(max_length=200, verbose_name='Título del Recordatorio')
    descripcion = models.TextField(verbose_name='Detalle del Recordatorio')
    fecha_programada = models.DateField(verbose_name='Fecha Prevista / Límite')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', verbose_name='Estado')
    medio_envio = models.CharField(max_length=20, choices=MEDIOS, default='WHATSAPP', verbose_name='Canal de Comunicación')
    fecha_envio_real = models.DateTimeField(null=True, blank=True, verbose_name='Fecha y Hora de Envío')
    notas_seguimiento = models.TextField(blank=True, verbose_name='Notas de Respuesta del Tutor')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recordatorio Preventivo'
        verbose_name_plural = 'Recordatorios Preventivos'
        ordering = ['fecha_programada']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.mascota.nombre} ({self.fecha_programada.strftime('%d/%m/%Y')})"

    @property
    def esta_vencido(self):
        return self.fecha_programada < date.today() and self.estado in ['PENDIENTE', 'ENVIADO']

    @property
    def dias_restantes(self):
        delta = self.fecha_programada - date.today()
        return delta.days

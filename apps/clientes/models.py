from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


class Especie(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre de la Especie')
    icono = models.CharField(max_length=50, blank=True, default='fas fa-paw', help_text='Clase FontAwesome o similar')

    class Meta:
        verbose_name = 'Especie'
        verbose_name_plural = 'Especies'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Raza(models.Model):
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name='razas', verbose_name='Especie')
    nombre = models.CharField(max_length=80, verbose_name='Nombre de la Raza')

    class Meta:
        verbose_name = 'Raza'
        verbose_name_plural = 'Razas'
        unique_together = ('especie', 'nombre')
        ordering = ['especie__nombre', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.especie.nombre})"


class Tutor(models.Model):
    usuario = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tutor_perfil', verbose_name='Usuario Asociado (opcional)'
    )
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    rut = models.CharField(max_length=15, unique=True, verbose_name='RUT')
    correo = models.EmailField(verbose_name='Correo Electrónico')
    telefono_principal = models.CharField(max_length=20, verbose_name='Teléfono Principal')
    telefono_secundario = models.CharField(max_length=20, blank=True, verbose_name='Teléfono Secundario (Emergencias)')
    direccion = models.CharField(max_length=255, verbose_name='Dirección')
    comuna = models.CharField(max_length=100, default='Santiago', verbose_name='Comuna / Ciudad')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones del Tutor')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')

    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.rut})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def cantidad_mascotas(self):
        return self.mascotas.filter(fallecido=False).count()


class Mascota(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='mascotas', verbose_name='Tutor Responsable')
    nombre = models.CharField(max_length=80, verbose_name='Nombre de la Mascota')
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name='mascotas', verbose_name='Especie')
    raza = models.ForeignKey(Raza, on_delete=models.SET_NULL, null=True, blank=True, related_name='mascotas', verbose_name='Raza')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name='Sexo')
    esterilizado = models.BooleanField(default=False, verbose_name='¿Está Esterilizado / Castrado?')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento')
    color = models.CharField(max_length=80, blank=True, verbose_name='Color / Pelaje')
    numero_microchip = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name='N° de Microchip')
    peso_actual_kg = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Peso Actual (Kg)')
    alergias_conocidas = models.TextField(blank=True, verbose_name='Alergias Conocidas')
    condiciones_preexistentes = models.TextField(blank=True, verbose_name='Condiciones Preexistentes o Crónicas')
    foto = models.ImageField(upload_to='mascotas/', blank=True, null=True, verbose_name='Foto de la Mascota')
    fallecido = models.BooleanField(default=False, verbose_name='¿Fallecido?')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Ingreso')

    class Meta:
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.especie.nombre}) - Tutor: {self.tutor.nombre_completo}"

    @property
    def edad(self):
        """Calcula la edad en años y meses."""
        if not self.fecha_nacimiento:
            return "Desconocida"
        hoy = date.today()
        anios = hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        meses = (hoy.month - self.fecha_nacimiento.month) % 12
        if anios > 0:
            return f"{anios} año(s)" if meses == 0 else f"{anios} año(s) y {meses} mes(es)"
        return f"{meses} mes(es)"

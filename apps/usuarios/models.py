from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador / Director'),
        ('VETERINARIO', 'Médico Veterinario'),
        ('RECEPCIONISTA', 'Recepcionista / Asistente'),
        ('TUTOR', 'Tutor de Mascota'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='RECEPCIONISTA')
    rut = models.CharField(max_length=15, unique=True, verbose_name='RUT')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
    numero_colegiado = models.CharField(max_length=50, blank=True, verbose_name='N° Registro Médico / Colegiado')
    especialidad = models.CharField(max_length=100, blank=True, verbose_name='Especialidad')
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name='Foto de Perfil')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_rol_display()})"

    @property
    def es_veterinario(self):
        return self.rol == 'VETERINARIO' or self.user.is_superuser

    @property
    def es_admin(self):
        return self.rol == 'ADMIN' or self.user.is_superuser

    @property
    def es_recepcionista(self):
        return self.rol in ['RECEPCIONISTA', 'ADMIN'] or self.user.is_superuser

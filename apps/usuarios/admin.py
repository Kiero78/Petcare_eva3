from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario Extendido'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'perfil__rol')

    @admin.display(description='Rol Asignado')
    def get_rol(self, instance):
        if hasattr(instance, 'perfil'):
            rol_colors = {
                'ADMIN': '#dc3545',
                'VETERINARIO': '#0d6efd',
                'RECEPCIONISTA': '#198754',
                'TUTOR': '#6c757d',
            }
            color = rol_colors.get(instance.perfil.rol, '#333')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
                color, instance.perfil.get_rol_display()
            )
        return "Sin Perfil"


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol_badge', 'rut', 'telefono', 'numero_colegiado', 'especialidad')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rut', 'telefono', 'numero_colegiado')
    ordering = ('user__first_name',)

    @admin.display(description='Rol')
    def rol_badge(self, obj):
        colores = {
            'ADMIN': '#dc3545',
            'VETERINARIO': '#0d6efd',
            'RECEPCIONISTA': '#198754',
            'TUTOR': '#6c757d',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            colores.get(obj.rol, '#333'), obj.get_rol_display()
        )

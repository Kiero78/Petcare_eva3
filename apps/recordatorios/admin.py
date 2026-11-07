from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import TipoVacuna, RegistroVacunacion, Recordatorio


@admin.register(TipoVacuna)
class TipoVacunaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'periodicidad_meses', 'obligatoria_badge')
    list_filter = ('especie', 'obligatoria')
    search_fields = ('nombre', 'descripcion')

    @admin.display(description='Obligatoria')
    def obligatoria_badge(self, obj):
        if obj.obligatoria:
            return format_html('<span style="color: #198754; font-weight: bold;">✓ Obligatoria</span>')
        return format_html('<span style="color: #6c757d;">Opcional</span>')


@admin.register(RegistroVacunacion)
class RegistroVacunacionAdmin(admin.ModelAdmin):
    list_display = ('tipo_vacuna', 'mascota_info', 'tutor_info', 'fecha_aplicacion', 'fecha_proxima_dosis', 'veterinario_info', 'numero_lote')
    list_filter = ('tipo_vacuna__especie', 'tipo_vacuna', 'fecha_aplicacion', 'fecha_proxima_dosis')
    search_fields = ('mascota__nombre', 'mascota__tutor__nombres', 'mascota__tutor__apellidos', 'numero_lote', 'laboratorio')
    date_hierarchy = 'fecha_aplicacion'

    @admin.display(description='Mascota')
    def mascota_info(self, obj):
        return f"{obj.mascota.nombre} ({obj.mascota.especie.nombre})"

    @admin.display(description='Tutor')
    def tutor_info(self, obj):
        return f"{obj.mascota.tutor.nombre_completo} ({obj.mascota.tutor.telefono_principal})"

    @admin.display(description='Veterinario')
    def veterinario_info(self, obj):
        return f"Dr(a). {obj.veterinario.last_name or obj.veterinario.username}"


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'mascota_info', 'tutor_contacto', 'tipo_badge',
        'fecha_programada', 'alerta_vencimiento', 'medio_envio', 'estado_badge'
    )
    list_filter = ('estado', 'tipo', 'medio_envio', 'fecha_programada')
    search_fields = ('titulo', 'descripcion', 'mascota__nombre', 'tutor__nombres', 'tutor__apellidos', 'tutor__telefono_principal')
    date_hierarchy = 'fecha_programada'
    actions = ['marcar_enviado', 'marcar_confirmado', 'marcar_vencido']

    fieldsets = (
        ('Datos del Recordatorio', {
            'fields': (('tipo', 'estado'), 'titulo', 'descripcion')
        }),
        ('Destinatario y Mascota', {
            'fields': (('tutor', 'mascota'), ('fecha_programada', 'medio_envio'))
        }),
        ('Seguimiento', {
            'fields': ('fecha_envio_real', 'notas_seguimiento')
        }),
    )

    @admin.display(description='Mascota')
    def mascota_info(self, obj):
        return f"{obj.mascota.nombre} ({obj.mascota.especie.nombre})"

    @admin.display(description='Tutor / Contacto')
    def tutor_contacto(self, obj):
        return f"{obj.tutor.nombre_completo} 📞 {obj.tutor.telefono_principal}"

    @admin.display(description='Tipo')
    def tipo_badge(self, obj):
        return format_html(
            '<span style="background-color: #e9ecef; color: #495057; padding: 3px 6px; border-radius: 4px; font-size: 11px;">{}</span>',
            obj.get_tipo_display()
        )

    @admin.display(description='Alerta Plazo')
    def alerta_vencimiento(self, obj):
        dias = obj.dias_restantes
        if obj.estado in ['CONFIRMADO', 'CANCELADO']:
            return format_html('<span style="color: #6c757d;">Resuelto</span>')
        if dias < 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 7px; border-radius: 8px; font-weight: bold; font-size: 11px;">⚠️ Vencido hace {} día(s)</span>',
                abs(dias)
            )
        elif dias == 0:
            return format_html(
                '<span style="background-color: #fd7e14; color: white; padding: 2px 7px; border-radius: 8px; font-weight: bold; font-size: 11px;">🔥 ¡Vence hoy!</span>'
            )
        elif dias <= 7:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 2px 7px; border-radius: 8px; font-weight: bold; font-size: 11px;">⏳ En {} días</span>',
                dias
            )
        return format_html('<span style="color: #198754;">En {} días</span>', dias)

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        colores = {
            'PENDIENTE': '#ffc107',
            'ENVIADO': '#0dcaf0',
            'CONFIRMADO': '#198754',
            'VENCIDO': '#dc3545',
            'CANCELADO': '#6c757d',
        }
        color = colores.get(obj.estado, '#6c757d')
        texto_color = '#000' if obj.estado in ['PENDIENTE', 'ENVIADO'] else '#fff'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, texto_color, obj.get_estado_display()
        )

    @admin.action(description='Marcar seleccionados como ENVIADOS (notificación emitida)')
    def marcar_enviado(self, request, queryset):
        queryset.update(estado='ENVIADO', fecha_envio_real=timezone.now())

    @admin.action(description='Marcar seleccionados como CONFIRMADOS / AGENDADOS')
    def marcar_confirmado(self, request, queryset):
        queryset.update(estado='CONFIRMADO')

    @admin.action(description='Marcar seleccionados como VENCIDOS')
    def marcar_vencido(self, request, queryset):
        queryset.update(estado='VENCIDO')

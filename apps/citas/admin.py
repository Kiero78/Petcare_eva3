from django.contrib import admin
from django.utils.html import format_html
from .models import HorarioDisponibilidad, Cita


@admin.register(HorarioDisponibilidad)
class HorarioDisponibilidadAdmin(admin.ModelAdmin):
    list_display = ('veterinario', 'dia_semana_nombre', 'hora_inicio', 'hora_fin', 'duracion_bloque_minutos', 'activo')
    list_filter = ('dia_semana', 'activo', 'veterinario')
    search_fields = ('veterinario__first_name', 'veterinario__last_name', 'veterinario__username')

    @admin.display(description='Día')
    def dia_semana_nombre(self, obj):
        return obj.get_dia_semana_display()


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fecha', 'hora_rango', 'mascota_info', 'tutor_info',
        'veterinario_info', 'tipo_badge', 'estado_badge'
    )
    list_filter = ('estado', 'tipo_cita', 'fecha', 'veterinario')
    search_fields = (
        'mascota__nombre', 'tutor__nombres', 'tutor__apellidos', 'tutor__rut',
        'veterinario__first_name', 'veterinario__last_name', 'motivo'
    )
    date_hierarchy = 'fecha'
    actions = ['marcar_confirmada', 'marcar_en_atencion', 'marcar_finalizada', 'marcar_cancelada']

    fieldsets = (
        ('Información de la Cita', {
            'fields': (('fecha', 'tipo_cita', 'estado'), ('hora_inicio', 'hora_fin'))
        }),
        ('Participantes', {
            'fields': (('tutor', 'mascota'), 'veterinario')
        }),
        ('Detalles y Diagnóstico Preliminar', {
            'fields': ('motivo', 'observaciones')
        }),
        ('Auditoría', {
            'fields': (('creado_por', 'fecha_creacion', 'fecha_modificacion'),),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')

    @admin.display(description='Horario')
    def hora_rango(self, obj):
        return f"{obj.hora_inicio.strftime('%H:%M')} - {obj.hora_fin.strftime('%H:%M')}"

    @admin.display(description='Mascota')
    def mascota_info(self, obj):
        return f"{obj.mascota.nombre} ({obj.mascota.especie.nombre})"

    @admin.display(description='Tutor')
    def tutor_info(self, obj):
        return f"{obj.tutor.nombre_completo} ({obj.tutor.telefono_principal})"

    @admin.display(description='Veterinario')
    def veterinario_info(self, obj):
        return f"Dr(a). {obj.veterinario.get_full_name() or obj.veterinario.username}"

    @admin.display(description='Tipo')
    def tipo_badge(self, obj):
        return format_html(
            '<span style="background-color: #e2e3e5; color: #383d41; padding: 3px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            obj.get_tipo_cita_display()
        )

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        colores = {
            'PENDIENTE': '#ffc107',
            'CONFIRMADA': '#0dcaf0',
            'EN_ATENCION': '#0d6efd',
            'FINALIZADA': '#198754',
            'CANCELADA': '#dc3545',
            'NO_ASISTIO': '#6c757d',
        }
        color = colores.get(obj.estado, '#6c757d')
        texto_color = '#000' if obj.estado in ['PENDIENTE', 'CONFIRMADA'] else '#fff'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, texto_color, obj.get_estado_display()
        )

    # Acciones masivas de administración
    @admin.action(description='Marcar seleccionadas como CONFIRMADAS')
    def marcar_confirmada(self, request, queryset):
        queryset.update(estado='CONFIRMADA')

    @admin.action(description='Marcar seleccionadas como EN ATENCIÓN')
    def marcar_en_atencion(self, request, queryset):
        queryset.update(estado='EN_ATENCION')

    @admin.action(description='Marcar seleccionadas como FINALIZADAS')
    def marcar_finalizada(self, request, queryset):
        queryset.update(estado='FINALIZADA')

    @admin.action(description='Marcar seleccionadas como CANCELADAS')
    def marcar_cancelada(self, request, queryset):
        queryset.update(estado='CANCELADA')

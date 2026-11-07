from django.contrib import admin
from django.utils.html import format_html
from .models import FichaClinica, AtencionClinica, RecetaMedica, ExamenClinico


class AtencionClinicaInline(admin.StackedInline):
    model = AtencionClinica
    extra = 0
    show_change_link = True
    fields = (
        'fecha_atencion', 'veterinario', 'motivo_consulta',
        ('peso_kg', 'temperatura_c', 'mucosas'),
        'diagnostico_principal', 'tratamiento_aplicado'
    )


@admin.register(FichaClinica)
class FichaClinicaAdmin(admin.ModelAdmin):
    list_display = ('numero_ficha', 'mascota_nombre', 'especie_nombre', 'tutor_nombre', 'total_atenciones', 'fecha_apertura', 'fecha_actualizacion')
    search_fields = ('numero_ficha', 'mascota__nombre', 'mascota__tutor__nombres', 'mascota__tutor__apellidos', 'mascota__tutor__rut')
    inlines = [AtencionClinicaInline]
    readonly_fields = ('numero_ficha', 'fecha_apertura', 'fecha_actualizacion')

    @admin.display(description='Mascota')
    def mascota_nombre(self, obj):
        return obj.mascota.nombre

    @admin.display(description='Especie')
    def especie_nombre(self, obj):
        return obj.mascota.especie.nombre

    @admin.display(description='Tutor')
    def tutor_nombre(self, obj):
        return obj.mascota.tutor.nombre_completo

    @admin.display(description='Consultas')
    def total_atenciones(self, obj):
        total = obj.atenciones.count()
        return format_html(
            '<span style="background-color: #0d6efd; color: white; padding: 2px 7px; border-radius: 10px; font-weight: bold;">🩺 {}</span>',
            total
        )


class RecetaMedicaInline(admin.TabularInline):
    model = RecetaMedica
    extra = 1
    fields = ('medicamento', 'presentacion', 'dosis', 'frecuencia', 'duracion', 'indicaciones_especiales')


class ExamenClinicoInline(admin.TabularInline):
    model = ExamenClinico
    extra = 0
    fields = ('nombre_examen', 'tipo_examen', 'justificacion_clinica', 'estado', 'archivo_adjunto')


@admin.register(AtencionClinica)
class AtencionClinicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_atencion', 'mascota_nombre', 'veterinario_nombre', 'motivo_consulta', 'signos_vitales_resumen', 'diagnostico_resumen')
    list_filter = ('fecha_atencion', 'veterinario', 'mucosas', 'requiere_control')
    search_fields = ('ficha__mascota__nombre', 'ficha__numero_ficha', 'motivo_consulta', 'diagnostico_principal', 'veterinario__first_name', 'veterinario__last_name')
    inlines = [RecetaMedicaInline, ExamenClinicoInline]
    date_hierarchy = 'fecha_atencion'

    fieldsets = (
        ('Datos Generales', {
            'fields': (('ficha', 'cita'), ('veterinario', 'fecha_atencion'))
        }),
        ('Motivo y Anamnesis', {
            'fields': ('motivo_consulta', 'anamnesis')
        }),
        ('Signos Vitales y Examen Físico', {
            'fields': (
                ('peso_kg', 'temperatura_c'),
                ('frecuencia_cardiaca_lpm', 'frecuencia_respiratoria_rpm'),
                ('tiempo_llenado_capilar_seg', 'mucosas'),
                'examen_fisico'
            )
        }),
        ('Juicio Clínico y Plan Terapéutico', {
            'fields': ('diagnostico_principal', 'diagnosticos_diferenciales', 'tratamiento_aplicado', 'indicaciones_tutor')
        }),
        ('Control Posterior', {
            'fields': (('requiere_control', 'dias_proximo_control'),)
        }),
    )

    @admin.display(description='Mascota')
    def mascota_nombre(self, obj):
        return f"{obj.ficha.mascota.nombre} ({obj.ficha.numero_ficha})"

    @admin.display(description='Veterinario')
    def veterinario_nombre(self, obj):
        return f"Dr(a). {obj.veterinario.get_full_name() or obj.veterinario.username}"

    @admin.display(description='Signos Vitales')
    def signos_vitales_resumen(self, obj):
        return format_html(
            '<span>⚖️ {} Kg | 🌡️ {} °C</span>',
            obj.peso_kg, obj.temperatura_c
        )

    @admin.display(description='Diagnóstico')
    def diagnostico_resumen(self, obj):
        if len(obj.diagnostico_principal) > 40:
            return obj.diagnostico_principal[:37] + '...'
        return obj.diagnostico_principal


@admin.register(RecetaMedica)
class RecetaMedicaAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'dosis', 'frecuencia', 'duracion', 'mascota_paciente', 'fecha_receta')
    search_fields = ('medicamento', 'atencion__ficha__mascota__nombre', 'indicaciones_especiales')

    @admin.display(description='Paciente')
    def mascota_paciente(self, obj):
        return obj.atencion.ficha.mascota.nombre

    @admin.display(description='Fecha')
    def fecha_receta(self, obj):
        return obj.atencion.fecha_atencion.strftime('%d/%m/%Y')


@admin.register(ExamenClinico)
class ExamenClinicoAdmin(admin.ModelAdmin):
    list_display = ('nombre_examen', 'tipo_examen', 'mascota_paciente', 'estado_badge', 'fecha_solicitud', 'tiene_archivo')
    list_filter = ('estado', 'tipo_examen', 'fecha_solicitud')
    search_fields = ('nombre_examen', 'atencion__ficha__mascota__nombre', 'justificacion_clinica', 'resultado_informe')

    @admin.display(description='Paciente')
    def mascota_paciente(self, obj):
        return obj.atencion.ficha.mascota.nombre

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        colores = {
            'SOLICITADO': '#ffc107',
            'EN_PROCESO': '#0dcaf0',
            'COMPLETADO': '#198754',
            'CANCELADO': '#dc3545',
        }
        color = colores.get(obj.estado, '#6c757d')
        texto_color = '#000' if obj.estado in ['SOLICITADO', 'EN_PROCESO'] else '#fff'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 10px; font-weight: bold; font-size: 11px;">{}</span>',
            color, texto_color, obj.get_estado_display()
        )

    @admin.display(description='Resultado Adjunto')
    def tiene_archivo(self, obj):
        if obj.archivo_adjunto:
            return format_html('<a href="{}" target="_blank" style="color: green; font-weight: bold;">📎 Ver Archivo</a>', obj.archivo_adjunto.url)
        return format_html('<span style="color: #6c757d;">Sin archivo</span>')

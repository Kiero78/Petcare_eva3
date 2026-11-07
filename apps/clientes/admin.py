from django.contrib import admin
from django.utils.html import format_html
from .models import Especie, Raza, Tutor, Mascota


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'icono', 'total_mascotas')
    search_fields = ('nombre',)

    @admin.display(description='Total Mascotas')
    def total_mascotas(self, obj):
        return obj.mascotas.count()


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'especie', 'total_mascotas')
    list_filter = ('especie',)
    search_fields = ('nombre', 'especie__nombre')

    @admin.display(description='Total Mascotas')
    def total_mascotas(self, obj):
        return obj.mascotas.count()


class MascotaInline(admin.TabularInline):
    model = Mascota
    extra = 0
    fields = ('nombre', 'especie', 'raza', 'sexo', 'esterilizado', 'fecha_nacimiento', 'peso_actual_kg')
    show_change_link = True


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre_completo', 'telefono_principal', 'correo', 'comuna', 'total_mascotas_badge', 'activo')
    list_filter = ('activo', 'comuna', 'fecha_registro')
    search_fields = ('rut', 'nombres', 'apellidos', 'correo', 'telefono_principal')
    inlines = [MascotaInline]
    readonly_fields = ('fecha_registro',)
    fieldsets = (
        ('Identificación y Contacto', {
            'fields': (('nombres', 'apellidos'), ('rut', 'correo'), ('telefono_principal', 'telefono_secundario'))
        }),
        ('Ubicación y Estado', {
            'fields': (('direccion', 'comuna'), ('activo', 'usuario'))
        }),
        ('Observaciones', {
            'fields': ('observaciones', 'fecha_registro')
        }),
    )

    @admin.display(description='Mascotas')
    def total_mascotas_badge(self, obj):
        cantidad = obj.cantidad_mascotas
        return format_html(
            '<span style="background-color: #0dcaf0; color: #000; padding: 3px 8px; border-radius: 10px; font-weight: bold;">🐾 {}</span>',
            cantidad
        )


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie_badge', 'raza', 'tutor_enlace', 'sexo_badge', 'edad_calculada', 'peso_actual_kg', 'esterilizado_badge', 'fallecido')
    list_filter = ('especie', 'sexo', 'esterilizado', 'fallecido')
    search_fields = ('nombre', 'numero_microchip', 'tutor__nombres', 'tutor__apellidos', 'tutor__rut')
    readonly_fields = ('fecha_registro', 'edad_calculada')
    fieldsets = (
        ('Datos de la Mascota', {
            'fields': (('nombre', 'tutor'), ('especie', 'raza'), ('sexo', 'esterilizado'), ('fecha_nacimiento', 'edad_calculada', 'color'))
        }),
        ('Identificación y Salud', {
            'fields': (('numero_microchip', 'peso_actual_kg'), 'foto', 'alergias_conocidas', 'condiciones_preexistentes', 'fallecido')
        }),
        ('Metadatos', {
            'fields': ('fecha_registro',)
        }),
    )

    @admin.display(description='Especie')
    def especie_badge(self, obj):
        colores = {
            'Canino': '#0d6efd',
            'Felino': '#ffc107',
            'Ave': '#198754',
            'Exótico': '#6f42c1',
        }
        color = colores.get(obj.especie.nombre, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 6px; font-weight: 500;">{}</span>',
            color, obj.especie.nombre
        )

    @admin.display(description='Sexo')
    def sexo_badge(self, obj):
        if obj.sexo == 'M':
            return format_html('<span style="color: #0d6efd; font-weight: bold;">♂ Macho</span>')
        return format_html('<span style="color: #e83e8c; font-weight: bold;">♀ Hembra</span>')

    @admin.display(description='Esterilizado')
    def esterilizado_badge(self, obj):
        if obj.esterilizado:
            return format_html('<span style="color: green; font-weight: bold;">✓ Sí</span>')
        return format_html('<span style="color: #dc3545;">✗ No</span>')

    @admin.display(description='Tutor')
    def tutor_enlace(self, obj):
        return f"{obj.tutor.nombre_completo} ({obj.tutor.telefono_principal})"

    @admin.display(description='Edad')
    def edad_calculada(self, obj):
        return obj.edad

from django import forms
from .models import TipoVacuna, RegistroVacunacion, Recordatorio
from django.contrib.auth.models import User
from apps.clientes.models import Mascota, Tutor


class RegistroVacunacionForm(forms.ModelForm):
    class Meta:
        model = RegistroVacunacion
        fields = [
            'mascota', 'tipo_vacuna', 'veterinario',
            'fecha_aplicacion', 'fecha_proxima_dosis',
            'numero_lote', 'laboratorio', 'observaciones'
        ]
        widgets = {
            'mascota': forms.Select(attrs={'class': 'form-select'}),
            'tipo_vacuna': forms.Select(attrs={'class': 'form-select'}),
            'veterinario': forms.Select(attrs={'class': 'form-select'}),
            'fecha_aplicacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_proxima_dosis': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero_lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° de lote'}),
            'laboratorio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Zoetis, Boehringer'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_proxima_dosis'].required = False
        self.fields['fecha_proxima_dosis'].help_text = 'Dejar en blanco para calcular automáticamente según la periodicidad de la vacuna.'


class RecordatorioForm(forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ['mascota', 'tutor', 'tipo', 'titulo', 'descripcion', 'fecha_programada', 'medio_envio', 'estado']
        widgets = {
            'mascota': forms.Select(attrs={'class': 'form-select'}),
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_programada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'medio_envio': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

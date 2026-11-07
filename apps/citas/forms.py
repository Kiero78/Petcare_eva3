from django import forms
from .models import Cita, HorarioDisponibilidad
from django.contrib.auth.models import User
from apps.clientes.models import Tutor, Mascota


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = [
            'tutor', 'mascota', 'veterinario', 'tipo_cita',
            'fecha', 'hora_inicio', 'hora_fin', 'motivo', 'observaciones'
        ]
        widgets = {
            'tutor': forms.Select(attrs={'class': 'form-select', 'id': 'select-tutor'}),
            'mascota': forms.Select(attrs={'class': 'form-select', 'id': 'select-mascota'}),
            'veterinario': forms.Select(attrs={'class': 'form-select', 'id': 'select-veterinario'}),
            'tipo_cita': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'input-fecha'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'input-hora-inicio'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'input-hora-fin'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motivo principal de la consulta'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas adicionales / preparaciones previas'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar veterinarios que tengan rol VETERINARIO o superusuarios
        self.fields['veterinario'].queryset = User.objects.filter(
            is_active=True
        ).filter(
            models_Q_or_staff()
        ).distinct()

        # Si ya se seleccionó tutor o es instancia existente, poblar las mascotas
        if 'tutor' in self.data:
            try:
                tutor_id = int(self.data.get('tutor'))
                self.fields['mascota'].queryset = Mascota.objects.filter(tutor_id=tutor_id, fallecido=False)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['mascota'].queryset = self.instance.tutor.mascotas.filter(fallecido=False)
        else:
            self.fields['mascota'].queryset = Mascota.objects.none()


def models_Q_or_staff():
    from django.db.models import Q
    return Q(perfil__rol='VETERINARIO') | Q(is_superuser=True) | Q(is_staff=True)


class HorarioDisponibilidadForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponibilidad
        fields = ['veterinario', 'dia_semana', 'hora_inicio', 'hora_fin', 'duracion_bloque_minutos', 'activo']
        widgets = {
            'veterinario': forms.Select(attrs={'class': 'form-select'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duracion_bloque_minutos': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'step': 5}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

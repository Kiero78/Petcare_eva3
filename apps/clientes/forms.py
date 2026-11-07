from django import forms
from .models import Tutor, Mascota, Especie, Raza


class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = [
            'rut', 'nombres', 'apellidos', 'correo',
            'telefono_principal', 'telefono_secundario',
            'direccion', 'comuna', 'observaciones'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono_principal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'telefono_secundario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contacto de emergencia (opcional)'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle, N°, Depto / Casa'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comuna'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones particulares'}),
        }


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = [
            'tutor', 'nombre', 'especie', 'raza', 'sexo',
            'esterilizado', 'fecha_nacimiento', 'color',
            'numero_microchip', 'peso_actual_kg',
            'alergias_conocidas', 'condiciones_preexistentes', 'foto'
        ]
        widgets = {
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la mascota'}),
            'especie': forms.Select(attrs={'class': 'form-select', 'id': 'select-especie'}),
            'raza': forms.Select(attrs={'class': 'form-select', 'id': 'select-raza'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'esterilizado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Blanco con café'}),
            'numero_microchip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° Microchip (15 dígitos)'}),
            'peso_actual_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'alergias_conocidas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alergias a medicamentos, alimentos, etc.'}),
            'condiciones_preexistentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Condiciones crónicas o cirugías previas'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

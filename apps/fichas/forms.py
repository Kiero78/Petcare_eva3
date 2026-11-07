from django import forms
from .models import FichaClinica, AtencionClinica, RecetaMedica, ExamenClinico


class FichaClinicaForm(forms.ModelForm):
    class Meta:
        model = FichaClinica
        fields = ['grupo_sanguineo', 'antecedentes_quirurgicos', 'enfermedades_cronicas', 'alertas_medicas']
        widgets = {
            'grupo_sanguineo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: DEA 1.1 Positivo / Tipo A'}),
            'antecedentes_quirurgicos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'enfermedades_cronicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alertas_medicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '¡Alergia a fármacos, agresividad por dolor, etc.!'}),
        }


class AtencionClinicaForm(forms.ModelForm):
    class Meta:
        model = AtencionClinica
        fields = [
            'motivo_consulta', 'anamnesis',
            'peso_kg', 'temperatura_c', 'frecuencia_cardiaca_lpm',
            'frecuencia_respiratoria_rpm', 'tiempo_llenado_capilar_seg', 'mucosas',
            'examen_fisico', 'diagnostico_principal', 'diagnosticos_diferenciales',
            'tratamiento_aplicado', 'indicaciones_tutor',
            'requiere_control', 'dias_proximo_control'
        ]
        widgets = {
            'motivo_consulta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo principal'}),
            'anamnesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Historia del cuadro clínico reportado por el tutor'}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'temperatura_c': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'frecuencia_cardiaca_lpm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'lpm'}),
            'frecuencia_respiratoria_rpm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'rpm'}),
            'tiempo_llenado_capilar_seg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'seg'}),
            'mucosas': forms.Select(attrs={'class': 'form-select'}),
            'examen_fisico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Hallazgos de la exploración física'}),
            'diagnostico_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Diagnóstico definitivo o presuntivo'}),
            'diagnosticos_diferenciales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Otros diagnósticos posibles'}),
            'tratamiento_aplicado': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Procedimientos y medicamentos aplicados en clínica'}),
            'indicaciones_tutor': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instrucciones para el hogar y cuidados'}),
            'requiere_control': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'check-control'}),
            'dias_proximo_control': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Días'}),
        }


class RecetaMedicaForm(forms.ModelForm):
    class Meta:
        model = RecetaMedica
        fields = ['medicamento', 'presentacion', 'dosis', 'frecuencia', 'duracion', 'indicaciones_especiales']
        widgets = {
            'medicamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre comercial o genérico'}),
            'presentacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Comprimidos 20mg / Suspensión oral'}),
            'dosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1 comprimido / 2 ml'}),
            'frecuencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cada 12 horas'}),
            'duracion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 7 días'}),
            'indicaciones_especiales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Administrar con comida'}),
        }


class ExamenClinicoForm(forms.ModelForm):
    class Meta:
        model = ExamenClinico
        fields = ['nombre_examen', 'tipo_examen', 'justificacion_clinica', 'estado', 'resultado_informe', 'archivo_adjunto']
        widgets = {
            'nombre_examen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Hemograma completo / Ecografía abdominal'}),
            'tipo_examen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Hematología, Imagenología, Bioquímica'}),
            'justificacion_clinica': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'resultado_informe': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Informe o conclusiones del examen'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control'}),
        }

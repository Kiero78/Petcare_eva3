from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, date

from .models import FichaClinica, AtencionClinica, RecetaMedica, ExamenClinico
from .forms import FichaClinicaForm, AtencionClinicaForm, RecetaMedicaForm, ExamenClinicoForm
from apps.clientes.models import Mascota
from apps.citas.models import Cita
from apps.recordatorios.models import Recordatorio
from apps.usuarios.decorators import solo_veterinario


@login_required
def ficha_detalle(request, mascota_id):
    """
    Visualización integral de la Ficha Clínica Digital de la mascota.
    """
    mascota = get_object_or_404(Mascota.objects.select_related('tutor', 'especie', 'raza'), pk=mascota_id)
    ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)

    atenciones = ficha.atenciones.select_related('veterinario').prefetch_related('recetas', 'examenes').order_by('-fecha_atencion')
    vacunaciones = mascota.vacunaciones.select_related('tipo_vacuna', 'veterinario').order_by('-fecha_aplicacion')
    recordatorios = mascota.recordatorios.order_by('fecha_programada')

    context = {
        'mascota': mascota,
        'ficha': ficha,
        'atenciones': atenciones,
        'vacunaciones': vacunaciones,
        'recordatorios': recordatorios,
    }
    return render(request, 'fichas/ficha_detalle.html', context)


@login_required
@solo_veterinario
def ficha_editar(request, mascota_id):
    mascota = get_object_or_404(Mascota, pk=mascota_id)
    ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)

    if request.method == 'POST':
        form = FichaClinicaForm(request.POST, instance=ficha)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ficha clínica de {mascota.nombre} actualizada.")
            return redirect('fichas:ficha_detalle', mascota_id=mascota.id)
    else:
        form = FichaClinicaForm(instance=ficha)

    return render(request, 'fichas/ficha_form.html', {'form': form, 'mascota': mascota, 'titulo': 'Editar Antecedentes Clínicos'})


@login_required
@solo_veterinario
def atencion_crear(request, mascota_id):
    mascota = get_object_or_404(Mascota, pk=mascota_id)
    ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)

    if request.method == 'POST':
        form = AtencionClinicaForm(request.POST)
        if form.is_valid():
            atencion = form.save(commit=False)
            atencion.ficha = ficha
            atencion.veterinario = request.user
            atencion.save()

            # Si requiere control, generar recordatorio preventivo automático
            if atencion.requiere_control and atencion.dias_proximo_control:
                fecha_control = date.today() + timedelta(days=atencion.dias_proximo_control)
                Recordatorio.objects.create(
                    mascota=mascota,
                    tutor=mascota.tutor,
                    tipo='CONTROL_PERIODICO',
                    titulo=f"Control Médico para {mascota.nombre}",
                    descripcion=f"Control post-atención de {atencion.diagnostico_principal[:80]}. Agendado por Dr(a). {request.user.last_name}.",
                    fecha_programada=fecha_control,
                    estado='PENDIENTE',
                    medio_envio='WHATSAPP'
                )

            messages.success(request, "Atención médica registrada exitosamente.")
            return redirect('fichas:atencion_detalle', pk=atencion.pk)
    else:
        initial = {'peso_kg': mascota.peso_actual_kg}
        form = AtencionClinicaForm(initial=initial)

    return render(request, 'fichas/atencion_form.html', {
        'form': form, 'mascota': mascota, 'titulo': f'Nueva Consulta Médica para {mascota.nombre}'
    })


@login_required
@solo_veterinario
def atencion_crear_desde_cita(request, cita_id):
    cita = get_object_or_404(Cita.objects.select_related('mascota__tutor', 'veterinario'), pk=cita_id)
    mascota = cita.mascota
    ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)

    # Si ya tiene atención vinculada, ir a ella
    if hasattr(cita, 'atencion_clinica'):
        return redirect('fichas:atencion_detalle', pk=cita.atencion_clinica.pk)

    if request.method == 'POST':
        form = AtencionClinicaForm(request.POST)
        if form.is_valid():
            atencion = form.save(commit=False)
            atencion.ficha = ficha
            atencion.cita = cita
            atencion.veterinario = cita.veterinario
            atencion.save()

            # Cambiar estado de la cita a FINALIZADA
            cita.estado = 'FINALIZADA'
            cita.save()

            # Programar control si aplica
            if atencion.requiere_control and atencion.dias_proximo_control:
                fecha_control = date.today() + timedelta(days=atencion.dias_proximo_control)
                Recordatorio.objects.create(
                    mascota=mascota,
                    tutor=mascota.tutor,
                    tipo='CONTROL_PERIODICO',
                    titulo=f"Control Médico para {mascota.nombre}",
                    descripcion=f"Control posterior a Cita #{cita.id}. Diagnóstico: {atencion.diagnostico_principal[:80]}.",
                    fecha_programada=fecha_control,
                    estado='PENDIENTE',
                    medio_envio='WHATSAPP'
                )

            messages.success(request, f"Atención registrada y Cita #{cita.id} marcada como FINALIZADA.")
            return redirect('fichas:atencion_detalle', pk=atencion.pk)
    else:
        initial = {
            'motivo_consulta': cita.motivo,
            'peso_kg': mascota.peso_actual_kg,
        }
        form = AtencionClinicaForm(initial=initial)

    return render(request, 'fichas/atencion_form.html', {
        'form': form, 'mascota': mascota, 'cita': cita,
        'titulo': f'Atención Médica Cita #{cita.id} - {mascota.nombre}'
    })


@login_required
def atencion_detalle(request, pk):
    atencion = get_object_or_404(
        AtencionClinica.objects.select_related('ficha__mascota__tutor', 'veterinario', 'cita'),
        pk=pk
    )
    recetas = atencion.recetas.all()
    examenes = atencion.examenes.all()

    receta_form = RecetaMedicaForm()
    examen_form = ExamenClinicoForm()

    context = {
        'atencion': atencion,
        'mascota': atencion.ficha.mascota,
        'tutor': atencion.ficha.mascota.tutor,
        'recetas': recetas,
        'examenes': examenes,
        'receta_form': receta_form,
        'examen_form': examen_form,
    }
    return render(request, 'fichas/atencion_detalle.html', context)


# ----------------- RECETAS Y EXÁMENES -----------------

@login_required
@solo_veterinario
def receta_agregar(request, atencion_id):
    atencion = get_object_or_404(AtencionClinica, pk=atencion_id)
    if request.method == 'POST':
        form = RecetaMedicaForm(request.POST)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.atencion = atencion
            receta.save()
            messages.success(request, f"Medicamento {receta.medicamento} agregado a la receta.")
    return redirect('fichas:atencion_detalle', pk=atencion.id)


@login_required
@solo_veterinario
def receta_eliminar(request, pk):
    receta = get_object_or_404(RecetaMedica, pk=pk)
    atencion_id = receta.atencion.id
    if request.method == 'POST':
        receta.delete()
        messages.info(request, "Medicamento eliminado de la prescripción.")
    return redirect('fichas:atencion_detalle', pk=atencion_id)


@login_required
def receta_imprimir(request, atencion_id):
    atencion = get_object_or_404(
        AtencionClinica.objects.select_related('ficha__mascota__tutor', 'veterinario'),
        pk=atencion_id
    )
    recetas = atencion.recetas.all()
    return render(request, 'fichas/receta_imprimir.html', {
        'atencion': atencion,
        'mascota': atencion.ficha.mascota,
        'tutor': atencion.ficha.mascota.tutor,
        'recetas': recetas,
    })


@login_required
@solo_veterinario
def examen_agregar(request, atencion_id):
    atencion = get_object_or_404(AtencionClinica, pk=atencion_id)
    if request.method == 'POST':
        form = ExamenClinicoForm(request.POST, request.FILES)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.atencion = atencion
            if examen.archivo_adjunto and not examen.fecha_resultado:
                examen.fecha_resultado = timezone.now()
                examen.estado = 'COMPLETADO'
            examen.save()
            messages.success(request, f"Examen {examen.nombre_examen} registrado.")
    return redirect('fichas:atencion_detalle', pk=atencion.id)

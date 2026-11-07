from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from django.core.exceptions import ValidationError

from .models import Cita, HorarioDisponibilidad
from .forms import CitaForm, HorarioDisponibilidadForm
from apps.clientes.models import Tutor, Mascota


@login_required
def calendario_citas(request):
    """
    Vista principal del Calendario Veterinario Dinámico.
    Permite visualizar citas por mes, semana, día y filtrar por profesional.
    """
    veterinarios = User.objects.filter(is_active=True).filter(
        models_Q_vet()
    ).distinct()

    veterinario_id = request.GET.get('veterinario', '')

    context = {
        'veterinarios': veterinarios,
        'veterinario_id': veterinario_id,
        'tutores': Tutor.objects.filter(activo=True).order_by('apellidos'),
    }
    return render(request, 'citas/calendario.html', context)


def models_Q_vet():
    from django.db.models import Q
    return Q(perfil__rol='VETERINARIO') | Q(is_superuser=True)


@login_required
def citas_lista(request):
    """
    Vista tabular de citas médicas con filtros avanzados.
    """
    fecha_filtro = request.GET.get('fecha', '')
    veterinario_id = request.GET.get('veterinario', '')
    estado_filtro = request.GET.get('estado', '')

    citas = Cita.objects.select_related('tutor', 'mascota', 'veterinario').order_by('-fecha', 'hora_inicio')

    if fecha_filtro:
        citas = citas.filter(fecha=fecha_filtro)
    if veterinario_id:
        citas = citas.filter(veterinario_id=veterinario_id)
    if estado_filtro:
        citas = citas.filter(estado=estado_filtro)

    veterinarios = User.objects.filter(is_active=True).filter(models_Q_vet()).distinct()

    context = {
        'citas': citas,
        'veterinarios': veterinarios,
        'fecha_filtro': fecha_filtro,
        'veterinario_id': veterinario_id,
        'estado_filtro': estado_filtro,
        'estados': Cita.ESTADOS,
    }
    return render(request, 'citas/citas_lista.html', context)


@login_required
def cita_crear(request):
    """
    Agendamiento de cita con validación estricta de no-solapamiento.
    """
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.creado_por = request.user
            try:
                cita.save()
                messages.success(request, f"Cita #{cita.id} para {cita.mascota.nombre} agendada correctamente.")
                return redirect('citas:calendario')
            except ValidationError as e:
                # Si el modelo captura solapamiento u otra regla de negocio
                form.add_error(None, e.message if hasattr(e, 'message') else str(e))
    else:
        # Preseleccionar fecha si viene por GET (desde el click en el calendario)
        fecha_param = request.GET.get('fecha')
        vet_param = request.GET.get('veterinario_id')
        initial = {}
        if fecha_param:
            initial['fecha'] = fecha_param
        if vet_param:
            initial['veterinario'] = vet_param
        form = CitaForm(initial=initial)

    return render(request, 'citas/cita_form.html', {'form': form, 'titulo': 'Agendar Nueva Cita Médica'})


@login_required
def cita_detalle(request, pk):
    cita = get_object_or_404(Cita.objects.select_related('tutor', 'mascota', 'veterinario', 'creado_por'), pk=pk)
    return render(request, 'citas/cita_detalle.html', {'cita': cita})


@login_required
def cita_cambiar_estado(request, pk, nuevo_estado):
    cita = get_object_or_404(Cita, pk=pk)
    estados_validos = dict(Cita.ESTADOS).keys()

    if nuevo_estado in estados_validos:
        cita.estado = nuevo_estado
        cita.save()
        messages.success(request, f"Estado de Cita #{cita.id} cambiado a {cita.get_estado_display()}.")

        # Si el estado es 'EN_ATENCION', redirigir a registrar la atención médica de la ficha si no existe
        if nuevo_estado == 'EN_ATENCION':
            return redirect('fichas:atencion_crear_desde_cita', cita_id=cita.id)

    return redirect('citas:cita_detalle', pk=cita.id)


# ----------------- APIS JSON PARA EL CALENDARIO Y VERIFICACIÓN -----------------

@login_required
def api_citas_eventos(request):
    """
    Provee eventos en formato JSON compatibles con FullCalendar.
    Resuelve el requerimiento de visualización y control de agenda en tiempo real.
    """
    start_str = request.GET.get('start', '')
    end_str = request.GET.get('end', '')
    veterinario_id = request.GET.get('veterinario_id', '')

    citas = Cita.objects.exclude(estado='CANCELADA').select_related('mascota', 'tutor', 'veterinario')

    if start_str:
        citas = citas.filter(fecha__gte=start_str[:10])
    if end_str:
        citas = citas.filter(fecha__lte=end_str[:10])
    if veterinario_id:
        citas = citas.filter(veterinario_id=veterinario_id)

    eventos = []
    colores_estado = {
        'PENDIENTE': '#ffc107',
        'CONFIRMADA': '#0dcaf0',
        'EN_ATENCION': '#0d6efd',
        'FINALIZADA': '#198754',
        'NO_ASISTIO': '#6c757d',
    }

    for c in citas:
        color = colores_estado.get(c.estado, '#0d6efd')
        start_iso = f"{c.fecha.isoformat()}T{c.hora_inicio.strftime('%H:%M:%S')}"
        end_iso = f"{c.fecha.isoformat()}T{c.hora_fin.strftime('%H:%M:%S')}"

        eventos.append({
            'id': c.id,
            'title': f"{c.mascota.nombre} - Dr(a). {c.veterinario.last_name or c.veterinario.username} ({c.get_tipo_cita_display()})",
            'start': start_iso,
            'end': end_iso,
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#000' if c.estado in ['PENDIENTE', 'CONFIRMADA'] else '#fff',
            'url': f"/citas/{c.id}/",
            'extendedProps': {
                'tutor': c.tutor.nombre_completo,
                'mascota': c.mascota.nombre,
                'especie': c.mascota.especie.nombre,
                'veterinario': c.veterinario.get_full_name() or c.veterinario.username,
                'motivo': c.motivo,
                'estado': c.get_estado_display(),
            }
        })

    return JsonResponse(eventos, safe=False)


@login_required
def api_verificar_solapamiento(request):
    """
    Verifica asíncronamente si existe solapamiento antes de enviar el formulario.
    """
    veterinario_id = request.GET.get('veterinario_id')
    fecha = request.GET.get('fecha')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fin = request.GET.get('hora_fin')
    cita_id = request.GET.get('cita_id')

    if not all([veterinario_id, fecha, hora_inicio, hora_fin]):
        return JsonResponse({'valido': True})

    query = Cita.objects.filter(
        veterinario_id=veterinario_id,
        fecha=fecha
    ).exclude(estado='CANCELADA').filter(
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio
    )

    if cita_id:
        query = query.exclude(id=cita_id)

    if query.exists():
        conflicto = query.first()
        return JsonResponse({
            'valido': False,
            'mensaje': (
                f"¡Horario Ocupado! El profesional ya tiene la Cita #{conflicto.id} "
                f"({conflicto.mascota.nombre}) de {conflicto.hora_inicio.strftime('%H:%M')} a {conflicto.hora_fin.strftime('%H:%M')}."
            )
        })

    return JsonResponse({'valido': True})


# ----------------- HORARIOS DE DISPONIBILIDAD -----------------

@login_required
def disponibilidad_lista(request):
    horarios = HorarioDisponibilidad.objects.select_related('veterinario').order_by('veterinario', 'dia_semana', 'hora_inicio')
    return render(request, 'citas/disponibilidad_lista.html', {'horarios': horarios})


@login_required
def disponibilidad_crear(request):
    if request.method == 'POST':
        form = HorarioDisponibilidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Horario de disponibilidad guardado.")
            return redirect('citas:disponibilidad_lista')
    else:
        form = HorarioDisponibilidadForm()

    return render(request, 'citas/disponibilidad_form.html', {'form': form, 'titulo': 'Configurar Horario de Atención'})

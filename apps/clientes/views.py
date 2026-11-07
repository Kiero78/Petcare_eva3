from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Tutor, Mascota, Especie, Raza
from .forms import TutorForm, MascotaForm
from apps.fichas.models import FichaClinica


@login_required
def tutor_lista(request):
    busqueda = request.GET.get('q', '').strip()
    tutores = Tutor.objects.filter(activo=True)

    if busqueda:
        tutores = tutores.filter(
            Q(rut__icontains=busqueda) |
            Q(nombres__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(telefono_principal__icontains=busqueda) |
            Q(correo__icontains=busqueda)
        )

    tutores = tutores.prefetch_related('mascotas')
    paginator = Paginator(tutores, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'busqueda': busqueda,
        'total': tutores.count(),
    }
    return render(request, 'clientes/tutor_lista.html', context)


@login_required
def tutor_detalle(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk)
    mascotas = tutor.mascotas.filter(fallecido=False).select_related('especie', 'raza')
    citas_recientes = tutor.citas.select_related('mascota', 'veterinario').order_by('-fecha', '-hora_inicio')[:10]

    context = {
        'tutor': tutor,
        'mascotas': mascotas,
        'citas_recientes': citas_recientes,
    }
    return render(request, 'clientes/tutor_detalle.html', context)


@login_required
def tutor_crear(request):
    if request.method == 'POST':
        form = TutorForm(request.POST)
        if form.is_valid():
            tutor = form.save()
            messages.success(request, f"Tutor {tutor.nombre_completo} registrado exitosamente.")
            return redirect('clientes:tutor_detalle', pk=tutor.pk)
    else:
        form = TutorForm()

    return render(request, 'clientes/tutor_form.html', {'form': form, 'titulo': 'Registrar Nuevo Tutor'})


@login_required
def tutor_editar(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk)
    if request.method == 'POST':
        form = TutorForm(request.POST, instance=tutor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {tutor.nombre_completo} actualizados.")
            return redirect('clientes:tutor_detalle', pk=tutor.pk)
    else:
        form = TutorForm(instance=tutor)

    return render(request, 'clientes/tutor_form.html', {'form': form, 'tutor': tutor, 'titulo': 'Editar Tutor'})


@login_required
def tutor_eliminar(request, pk):
    tutor = get_object_or_404(Tutor, pk=pk)
    if request.method == 'POST':
        tutor.activo = False
        tutor.save()
        messages.warning(request, f"Tutor {tutor.nombre_completo} dado de baja.")
        return redirect('clientes:tutor_lista')

    return render(request, 'clientes/tutor_confirm_delete.html', {'tutor': tutor})


# ----------------- MASCOTAS -----------------

@login_required
def mascota_lista(request):
    busqueda = request.GET.get('q', '').strip()
    especie_id = request.GET.get('especie', '')
    mascotas = Mascota.objects.filter(fallecido=False).select_related('tutor', 'especie', 'raza')

    if busqueda:
        mascotas = mascotas.filter(
            Q(nombre__icontains=busqueda) |
            Q(numero_microchip__icontains=busqueda) |
            Q(tutor__nombres__icontains=busqueda) |
            Q(tutor__apellidos__icontains=busqueda) |
            Q(tutor__rut__icontains=busqueda)
        )

    if especie_id:
        mascotas = mascotas.filter(especie_id=especie_id)

    paginator = Paginator(mascotas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    especies = Especie.objects.all()

    context = {
        'page_obj': page_obj,
        'busqueda': busqueda,
        'especie_id': especie_id,
        'especies': especies,
        'total': mascotas.count(),
    }
    return render(request, 'clientes/mascota_lista.html', context)


@login_required
def mascota_detalle(request, pk):
    mascota = get_object_or_404(Mascota.objects.select_related('tutor', 'especie', 'raza'), pk=pk)

    # Asegurar existencia de Ficha Clínica digital
    ficha, creada = FichaClinica.objects.get_or_create(mascota=mascota)

    # Consultas / Atenciones médicas
    atenciones = ficha.atenciones.select_related('veterinario').order_by('-fecha_atencion')
    vacunas = mascota.vacunaciones.select_related('tipo_vacuna', 'veterinario').order_by('-fecha_aplicacion')
    recordatorios = mascota.recordatorios.order_by('fecha_programada')
    citas = mascota.citas.select_related('veterinario').order_by('-fecha', '-hora_inicio')[:5]

    context = {
        'mascota': mascota,
        'ficha': ficha,
        'atenciones': atenciones,
        'vacunas': vacunas,
        'recordatorios': recordatorios,
        'citas': citas,
    }
    return render(request, 'clientes/mascota_detalle.html', context)


@login_required
def mascota_crear(request):
    tutor_preseleccionado = request.GET.get('tutor_id')
    initial_data = {}
    if tutor_preseleccionado:
        initial_data['tutor'] = tutor_preseleccionado

    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save()
            # Crear automáticamente su ficha clínica digital
            FichaClinica.objects.get_or_create(mascota=mascota)
            messages.success(request, f"Mascota {mascota.nombre} registrada correctamente con su Ficha Clínica.")
            return redirect('clientes:mascota_detalle', pk=mascota.pk)
    else:
        form = MascotaForm(initial=initial_data)

    return render(request, 'clientes/mascota_form.html', {'form': form, 'titulo': 'Registrar Nueva Mascota'})


@login_required
def mascota_editar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {mascota.nombre} actualizados con éxito.")
            return redirect('clientes:mascota_detalle', pk=mascota.pk)
    else:
        form = MascotaForm(instance=mascota)

    return render(request, 'clientes/mascota_form.html', {'form': form, 'mascota': mascota, 'titulo': 'Editar Mascota'})


# ----------------- APIs JSON PARA INTERACTIVIDAD -----------------

@login_required
def api_mascotas_por_tutor(request, tutor_id):
    """Devuelve las mascotas asociadas a un tutor para agilizar el agendamiento dinámico."""
    mascotas = Mascota.objects.filter(tutor_id=tutor_id, fallecido=False).values('id', 'nombre', 'especie__nombre')
    return JsonResponse(list(mascotas), safe=False)


@login_required
def api_razas_por_especie(request, especie_id):
    """Devuelve las razas filtradas según la especie seleccionada."""
    razas = Raza.objects.filter(especie_id=especie_id).values('id', 'nombre')
    return JsonResponse(list(razas), safe=False)

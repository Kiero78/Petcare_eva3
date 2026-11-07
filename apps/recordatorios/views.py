from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
import urllib.parse

from .models import TipoVacuna, RegistroVacunacion, Recordatorio
from .forms import RegistroVacunacionForm, RecordatorioForm
from apps.clientes.models import Mascota, Tutor


@login_required
def panel_recordatorios(request):
    """
    Panel central de control para Medicina Preventiva y Vacunación.
    Permite visualizar alertas vencidas, próximas y vacunas recientes.
    """
    hoy = date.today()
    limite_proximos = hoy + timedelta(days=15)

    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')

    recordatorios = Recordatorio.objects.select_related('mascota', 'tutor').order_by('fecha_programada')

    if tipo_filtro:
        recordatorios = recordatorios.filter(tipo=tipo_filtro)
    if estado_filtro:
        recordatorios = recordatorios.filter(estado=estado_filtro)

    # Segmentación
    vencidos = Recordatorio.objects.filter(
        estado__in=['PENDIENTE', 'ENVIADO'],
        fecha_programada__lt=hoy
    ).select_related('mascota', 'tutor').order_by('fecha_programada')

    proximos = Recordatorio.objects.filter(
        estado__in=['PENDIENTE', 'ENVIADO'],
        fecha_programada__gte=hoy,
        fecha_programada__lte=limite_proximos
    ).select_related('mascota', 'tutor').order_by('fecha_programada')

    ultimas_vacunaciones = RegistroVacunacion.objects.select_related(
        'mascota__tutor', 'tipo_vacuna', 'veterinario'
    ).order_by('-fecha_aplicacion')[:10]

    context = {
        'recordatorios': recordatorios,
        'vencidos': vencidos,
        'proximos': proximos,
        'ultimas_vacunaciones': ultimas_vacunaciones,
        'hoy': hoy,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'tipos': Recordatorio.TIPOS,
        'estados': Recordatorio.ESTADOS,
    }
    return render(request, 'recordatorios/panel.html', context)


@login_required
def vacunacion_registrar(request):
    mascota_id = request.GET.get('mascota_id')
    initial = {}
    if mascota_id:
        initial['mascota'] = mascota_id
    initial['veterinario'] = request.user.id

    if request.method == 'POST':
        form = RegistroVacunacionForm(request.POST)
        if form.is_valid():
            vacuna = form.save()
            messages.success(
                request,
                f"Vacuna {vacuna.tipo_vacuna.nombre} registrada para {vacuna.mascota.nombre}. "
                f"Próxima dosis calculada: {vacuna.fecha_proxima_dosis.strftime('%d/%m/%Y')}."
            )
            return redirect('recordatorios:panel')
    else:
        form = RegistroVacunacionForm(initial=initial)

    return render(request, 'recordatorios/vacunacion_form.html', {'form': form, 'titulo': 'Registrar Aplicación de Vacuna'})


@login_required
def recordatorio_crear(request):
    mascota_id = request.GET.get('mascota_id')
    initial = {}
    if mascota_id:
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        initial['mascota'] = mascota.id
        initial['tutor'] = mascota.tutor.id

    if request.method == 'POST':
        form = RecordatorioForm(request.POST)
        if form.is_valid():
            rec = form.save()
            messages.success(request, f"Recordatorio '{rec.titulo}' programado para el {rec.fecha_programada.strftime('%d/%m/%Y')}.")
            return redirect('recordatorios:panel')
    else:
        form = RecordatorioForm(initial=initial)

    return render(request, 'recordatorios/recordatorio_form.html', {'form': form, 'titulo': 'Programar Recordatorio Preventivo'})


@login_required
def recordatorio_cambiar_estado(request, pk, nuevo_estado):
    rec = get_object_or_404(Recordatorio, pk=pk)
    estados_validos = dict(Recordatorio.ESTADOS).keys()

    if nuevo_estado in estados_validos:
        rec.estado = nuevo_estado
        if nuevo_estado == 'ENVIADO':
            rec.fecha_envio_real = timezone.now()
        rec.save()
        messages.success(request, f"Recordatorio actualizado a {rec.get_estado_display()}.")

    return redirect('recordatorios:panel')


@login_required
def recordatorio_enviar_whatsapp(request, pk):
    """
    Genera el enlace directo a WhatsApp Web/App con el mensaje preformateado.
    """
    rec = get_object_or_404(Recordatorio.objects.select_related('tutor', 'mascota'), pk=pk)
    telefono = rec.tutor.telefono_principal.replace(' ', '').replace('+', '').replace('-', '')

    mensaje = (
        f"Hola {rec.tutor.nombres}, le saludamos desde Clínica Veterinaria PetCare 🐾. "
        f"Le recordamos que para su mascota *{rec.mascota.nombre}* está programado: *{rec.titulo}* "
        f"con fecha prevista {rec.fecha_programada.strftime('%d/%m/%Y')}. "
        f"Por favor contáctenos para coordinar su cita médica o confirmar su asistencia. ¡Muchas gracias!"
    )

    mensaje_encoded = urllib.parse.quote(mensaje)
    url_whatsapp = f"https://api.whatsapp.com/send?phone={telefono}&text={mensaje_encoded}"

    # Marcar como enviado
    rec.estado = 'ENVIADO'
    rec.fecha_envio_real = timezone.now()
    rec.save()

    return redirect(url_whatsapp)

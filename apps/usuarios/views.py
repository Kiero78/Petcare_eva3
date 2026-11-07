from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.db.models import Count

from apps.clientes.models import Tutor, Mascota
from apps.citas.models import Cita
from apps.fichas.models import AtencionClinica
from apps.recordatorios.models import Recordatorio


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario, password=clave)

        if user is not None:
            login(request, user)
            messages.success(request, f"¡Bienvenido(a) a PetCare, {user.first_name or user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Credenciales inválidas. Por favor verifique su usuario y contraseña.")

    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Ha cerrado su sesión de forma segura.")
    return redirect('usuarios:login')


@login_required
def dashboard_view(request):
    hoy = date.today()

    # Métricas generales
    total_tutores = Tutor.objects.filter(activo=True).count()
    total_mascotas = Mascota.objects.filter(fallecido=False).count()

    # Citas de hoy
    citas_hoy = Cita.objects.filter(fecha=hoy).select_related('mascota', 'tutor', 'veterinario').order_by('hora_inicio')
    total_citas_hoy = citas_hoy.count()
    citas_pendientes = citas_hoy.filter(estado__in=['PENDIENTE', 'CONFIRMADA']).count()
    citas_atendidas = citas_hoy.filter(estado='FINALIZADA').count()

    # Recordatorios y Vacunas
    recordatorios_urgentes = Recordatorio.objects.filter(
        estado__in=['PENDIENTE', 'ENVIADO'],
        fecha_programada__lte=hoy
    ).select_related('mascota', 'tutor').order_by('fecha_programada')[:5]

    total_alertas = Recordatorio.objects.filter(
        estado__in=['PENDIENTE', 'ENVIADO'],
        fecha_programada__lte=hoy
    ).count()

    # Últimas atenciones clínicas
    ultimas_atenciones = AtencionClinica.objects.select_related(
        'ficha__mascota', 'veterinario'
    ).order_by('-fecha_atencion')[:5]

    # Citas recientes para vista rápida
    proximas_citas = Cita.objects.filter(
        fecha__gte=hoy,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).select_related('mascota', 'tutor', 'veterinario').order_by('fecha', 'hora_inicio')[:5]

    contexto = {
        'total_tutores': total_tutores,
        'total_mascotas': total_mascotas,
        'total_citas_hoy': total_citas_hoy,
        'citas_pendientes': citas_pendientes,
        'citas_atendidas': citas_atendidas,
        'citas_hoy': citas_hoy,
        'recordatorios_urgentes': recordatorios_urgentes,
        'total_alertas': total_alertas,
        'ultimas_atenciones': ultimas_atenciones,
        'proximas_citas': proximas_citas,
        'hoy': hoy,
    }
    return render(request, 'dashboard.html', contexto)

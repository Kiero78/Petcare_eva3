from datetime import date
from .models import Recordatorio
from apps.citas.models import Cita


def alertas_globales(request):
    """
    Context processor para proveer contadores de alertas en tiempo real en la barra de navegación.
    """
    if not request.user.is_authenticated:
        return {}

    hoy = date.today()
    recordatorios_urgentes = Recordatorio.objects.filter(
        estado__in=['PENDIENTE', 'ENVIADO'],
        fecha_programada__lte=hoy
    ).count()

    citas_hoy = Cita.objects.filter(
        fecha=hoy,
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_ATENCION']
    ).count()

    return {
        'total_alertas_sanitarias': recordatorios_urgentes,
        'total_citas_hoy': citas_hoy,
        'fecha_hoy_sistema': hoy,
    }

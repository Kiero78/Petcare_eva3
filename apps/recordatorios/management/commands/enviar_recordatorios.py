from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from apps.recordatorios.models import Recordatorio


class Command(BaseCommand):
    help = 'Revisa y despacha recordatorios de vacunas y controles periódicos pendientes para los próximos días'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=3,
            help='Ventana de anticipación en días para alertar (por defecto 3 días)'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        hoy = date.today()
        limite = hoy + timedelta(days=dias)

        self.stdout.write(self.style.NOTICE(f"--- Procesando recordatorios entre {hoy} y {limite} ---"))

        pendientes = Recordatorio.objects.filter(
            estado='PENDIENTE',
            fecha_programada__lte=limite
        ).select_related('mascota', 'tutor')

        total = pendientes.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No existen recordatorios pendientes en el rango indicado."))
            return

        procesados = 0
        for rec in pendientes:
            # Simular emisión de alerta
            rec.estado = 'ENVIADO'
            rec.fecha_envio_real = timezone.now()
            rec.notas_seguimiento = f"Notificación automatizada despachada vía {rec.get_medio_envio_display()} el {timezone.now().strftime('%d/%m/%Y %H:%M')}."
            rec.save()
            procesados += 1

            self.stdout.write(
                f"[ENVIADO] ID #{rec.id} | {rec.titulo} -> {rec.tutor.nombre_completo} ({rec.tutor.telefono_principal})"
            )

        self.stdout.write(self.style.SUCCESS(f"¡Éxito! Se procesaron {procesados} recordatorio(s) preventivo(s)."))

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta

from apps.usuarios.models import PerfilUsuario
from apps.clientes.models import Especie, Raza, Tutor, Mascota
from apps.citas.models import HorarioDisponibilidad, Cita
from apps.fichas.models import FichaClinica, AtencionClinica, RecetaMedica, ExamenClinico
from apps.recordatorios.models import TipoVacuna, RegistroVacunacion, Recordatorio


class Command(BaseCommand):
    help = 'Puebla la base de datos con datos clínicos realistas para demostración y evaluación'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Iniciando Seed Data para PetCare ---"))

        # 1. USUARIOS Y ROLES
        users_data = [
            ('admin', 'admin1234', 'Marcelo', 'Administrador', 'admin@petcare.cl', 'ADMIN', '11.111.111-1', '+56 9 1111 2222', '12345', 'Cirugía y Traumatología', True),
            ('dr_perez', 'vet1234', 'Carlos', 'Pérez', 'cperez@petcare.cl', 'VETERINARIO', '15.234.567-8', '+56 9 2222 3333', '98765', 'Medicina Felina y Canina', False),
            ('dra_gonzalez', 'vet1234', 'María', 'González', 'mgonzalez@petcare.cl', 'VETERINARIO', '16.345.678-9', '+56 9 3333 4444', '54321', 'Dermatología Veterinaria', False),
            ('recepcion', 'recep1234', 'Camila', 'Soto', 'recepcion@petcare.cl', 'RECEPCIONISTA', '18.456.789-0', '+56 9 4444 5555', '', '', False),
        ]

        usuarios = {}
        for username, pwd, fname, lname, email, rol, rut, fono, reg, esp, is_super in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': email,
                    'is_staff': True,
                    'is_superuser': is_super
                }
            )
            user.set_password(pwd)
            user.save()

            perfil, _ = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    'rol': rol,
                    'rut': rut,
                    'telefono': fono,
                    'numero_colegiado': reg,
                    'especialidad': esp,
                }
            )
            perfil.rol = rol
            perfil.save()
            usuarios[username] = user
            self.stdout.write(f"Usuario '{username}' configurado (Rol: {rol}).")

        # 2. ESPECIES Y RAZAS
        especies_razas = {
            'Canino': ['Labrador Retriever', 'Pastor Alemán', 'Poodle Toy', 'Bulldog Francés', 'Golden Retriever', 'Mestizo', 'Beagle', 'Yorkshire Terrier'],
            'Felino': ['Siamés', 'Persa', 'Maine Coon', 'Común Europeo', 'Bengala', 'Ragdoll'],
            'Ave': ['Canario', 'Periquito Australiano', 'Ninfa'],
            'Exótico': ['Conejo Enano', 'Hurón', 'Cobayo / Cuy'],
        }

        especies_objs = {}
        for esp_nom, razas_list in especies_razas.items():
            esp, _ = Especie.objects.get_or_create(nombre=esp_nom)
            especies_objs[esp_nom] = esp
            for r_nom in razas_list:
                Raza.objects.get_or_create(especie=esp, nombre=r_nom)
        self.stdout.write("Especies y razas precargadas.")

        # 3. HORARIOS DE DISPONIBILIDAD
        vet_perez = usuarios['dr_perez']
        vet_gonzalez = usuarios['dra_gonzalez']

        for dia in range(0, 6):  # Lunes a Sábado
            HorarioDisponibilidad.objects.get_or_create(
                veterinario=vet_perez,
                dia_semana=dia,
                hora_inicio=time(9, 0),
                hora_fin=time(14, 0),
                defaults={'duracion_bloque_minutos': 30, 'activo': True}
            )
            HorarioDisponibilidad.objects.get_or_create(
                veterinario=vet_gonzalez,
                dia_semana=dia,
                hora_inicio=time(14, 30),
                hora_fin=time(19, 0),
                defaults={'duracion_bloque_minutos': 30, 'activo': True}
            )
        self.stdout.write("Horarios de disponibilidad médica configurados.")

        # 4. TIPOS DE VACUNAS
        canino = especies_objs['Canino']
        felino = especies_objs['Felino']

        vacunas_catalogo = [
            (canino, 'Vacuna Óctuple', 'Protege contra Moquillo, Parvovirus, Hepatitis, Leptospirosis, Parainfluenza y Coronavirus', 12, True),
            (canino, 'Vacuna Antirrábica', 'Inmunización obligatoria contra la Rabia según normativa sanitaria', 12, True),
            (canino, 'Vacuna KC (Tos de las Perreras)', 'Bordetella bronchiseptica y Parainfluenza Canina', 12, False),
            (felino, 'Vacuna Triple Felina', 'Rinotraqueítis, Calicivirus y Panleucopenia Felina', 12, True),
            (felino, 'Vacuna Leucemia Felina (FeLV)', 'Inmunización contra el virus de la Leucemia Felina', 12, True),
            (felino, 'Vacuna Antirrábica Felina', 'Inmunización obligatoria contra la Rabia', 12, True),
        ]

        vacunas_objs = {}
        for esp, nom, desc, meses, oblig in vacunas_catalogo:
            v_obj, _ = TipoVacuna.objects.get_or_create(
                especie=esp, nombre=nom,
                defaults={'descripcion': desc, 'periodicidad_meses': meses, 'obligatoria': oblig}
            )
            vacunas_objs[nom] = v_obj
        self.stdout.write("Catálogo de vacunas establecido.")

        # 5. TUTORES
        tutores_data = [
            ('13.567.890-1', 'Juan Ignacio', 'Morales Tapia', 'juan.morales@gmail.com', '+56 9 9123 4567', 'Av. Las Condes 8900', 'Las Condes'),
            ('14.234.567-2', 'Valentina', 'Rojas Silva', 'valerajas@hotmail.com', '+56 9 8234 5678', 'Los Leones 1450 Depto 402', 'Providencia'),
            ('17.890.123-3', 'Matías Andrés', 'Cifuentes Vera', 'matias.cifuentes@gmail.com', '+56 9 7345 6789', 'Vicuña Mackenna 230', 'Santiago Centro'),
            ('12.987.654-4', 'Claudia', 'Muñoz Fernández', 'claudia.munoz@yahoo.es', '+56 9 6456 7890', 'Gran Avenida 4500', 'San Miguel'),
        ]

        tutores = []
        for rut, nom, ape, email, fono, dir, com in tutores_data:
            t, _ = Tutor.objects.get_or_create(
                rut=rut,
                defaults={
                    'nombres': nom, 'apellidos': ape, 'correo': email,
                    'telefono_principal': fono, 'direccion': dir, 'comuna': com, 'activo': True
                }
            )
            tutores.append(t)
        self.stdout.write("Tutores registrados.")

        # 6. MASCOTAS
        t_juan, t_vale, t_matias, t_claudia = tutores
        raza_labrador = Raza.objects.filter(especie=canino, nombre='Labrador Retriever').first()
        raza_pastor = Raza.objects.filter(especie=canino, nombre='Pastor Alemán').first()
        raza_siames = Raza.objects.filter(especie=felino, nombre='Siamés').first()
        raza_comun = Raza.objects.filter(especie=felino, nombre='Común Europeo').first()

        mascotas_data = [
            (t_juan, 'Max', canino, raza_labrador, 'M', True, date(2021, 5, 10), 'Dorado', '985141000123456', 32.5, 'Alergia a pulgas', ''),
            (t_juan, 'Luna', felino, raza_siames, 'H', True, date(2022, 8, 20), 'Crema y marrón', '985141000654321', 4.2, '', 'Soplo cardíaco grado I'),
            (t_vale, 'Rocky', canino, raza_pastor, 'M', False, date(2020, 2, 14), 'Negro y fuego', '985141000789012', 36.8, '', 'Displasia de cadera leve'),
            (t_matias, 'Misi', felino, raza_comun, 'H', True, date(2023, 1, 15), 'Atigrado gris', '985141000345678', 3.8, '', ''),
            (t_claudia, 'Toby', canino, raza_labrador, 'M', True, date(2022, 11, 5), 'Chocolate', '985141000901234', 28.0, 'Intolerancia a pollo', ''),
        ]

        mascotas = []
        for tut, nom, esp, raz, sex, est, fnac, col, chip, peso, ale, pre in mascotas_data:
            m, _ = Mascota.objects.get_or_create(
                numero_microchip=chip,
                defaults={
                    'tutor': tut, 'nombre': nom, 'especie': esp, 'raza': raz, 'sexo': sex,
                    'esterilizado': est, 'fecha_nacimiento': fnac, 'color': col,
                    'peso_actual_kg': peso, 'alergias_conocidas': ale, 'condiciones_preexistentes': pre
                }
            )
            # Asegurar Ficha Clínica
            FichaClinica.objects.get_or_create(mascota=m)
            mascotas.append(m)
        self.stdout.write("Mascotas registradas con Fichas Clínicas Digitales inicializadas.")

        # 7. CITAS MÉDICAS (Hoy, pasadas y futuras)
        hoy = date.today()
        max_dog, luna_cat, rocky_dog, misi_cat, toby_dog = mascotas

        citas_data = [
            # Cita de hoy con Dr. Pérez
            (t_juan, max_dog, vet_perez, hoy, time(9, 30), time(10, 0), 'CONSULTA', 'EN_ATENCION', 'Revisión por cojera en extremidad posterior derecha tras ejercicio'),
            # Cita de hoy con Dra. González
            (t_vale, rocky_dog, vet_gonzalez, hoy, time(15, 0), time(15, 30), 'CONTROL', 'CONFIRMADA', 'Control de peso y evaluación de displasia de cadera'),
            # Cita de hoy completada
            (t_matias, misi_cat, vet_perez, hoy, time(11, 0), time(11, 30), 'VACUNACION', 'FINALIZADA', 'Vacunación anual y desparasitación interna'),
            # Cita futura mañana
            (t_claudia, toby_dog, vet_perez, hoy + timedelta(days=1), time(10, 0), time(10, 30), 'CONSULTA', 'CONFIRMADA', 'Dermatitis alérgica y prurito en zona dorsal'),
            # Cita futura en 3 días
            (t_juan, luna_cat, vet_gonzalez, hoy + timedelta(days=3), time(16, 0), time(16, 30), 'EXAMENES', 'PENDIENTE', 'Control cardiológico semestral y ecocardiograma'),
        ]

        citas_creadas = []
        for tut, masc, vet, fch, hi, hf, tcita, est, mot in citas_data:
            c, _ = Cita.objects.get_or_create(
                mascota=masc, fecha=fch, hora_inicio=hi,
                defaults={
                    'tutor': tut, 'veterinario': vet, 'hora_fin': hf,
                    'tipo_cita': tcita, 'estado': est, 'motivo': mot,
                    'creado_por': usuarios['recepcion']
                }
            )
            citas_creadas.append(c)
        self.stdout.write("Citas médicas agendadas en tiempo real sin solapamiento.")

        # 8. ATENCIÓN CLÍNICA Y RECETA (Para Max y Misi)
        ficha_max = max_dog.ficha_clinica
        atencion_max, _ = AtencionClinica.objects.get_or_create(
            ficha=ficha_max,
            motivo_consulta='Cojera en pata trasera derecha',
            defaults={
                'cita': citas_creadas[0],
                'veterinario': vet_perez,
                'fecha_atencion': timezone.now() - timedelta(minutes=45),
                'anamnesis': 'Tutor relata que Max estuvo jugando intensamente en el parque hace 2 días y amaneció sin apoyar del todo la pata trasera derecha.',
                'peso_kg': 32.5,
                'temperatura_c': 38.6,
                'frecuencia_cardiaca_lpm': 95,
                'frecuencia_respiratoria_rpm': 24,
                'tiempo_llenado_capilar_seg': 1.5,
                'mucosas': 'ROSADAS',
                'examen_fisico': 'Dolor a la palpación y extensión de rodilla derecha. Signo de cajón negativo. No se palpan crepitaciones óseas evidentes.',
                'diagnostico_principal': 'Esguince / distensión muscular en cuádriceps femoral derecho',
                'diagnosticos_diferenciales': 'Ruptura parcial ligamento cruzado craneal',
                'tratamiento_aplicado': 'Administración en consulta de Meloxicam 0.2 mg/kg SC.',
                'indicaciones_tutor': 'Reposo estricto por 7 días. Paseos sólo con correa de 5 minutos para necesidades fisiológicas. Aplicar hielo local los primeros 3 días.',
                'requiere_control': True,
                'dias_proximo_control': 7,
            }
        )

        # Receta médica para Max
        RecetaMedica.objects.get_or_create(
            atencion=atencion_max,
            medicamento='Meloxicam Oral 0.5 mg/ml',
            defaults={
                'presentacion': 'Suspensión Oral con jeringa dosificadora',
                'dosis': '0.1 mg/kg (3.2 ml)',
                'frecuencia': 'Cada 24 horas',
                'duracion': '5 días',
                'indicaciones_especiales': 'Administrar directamente en la boca o mezclado con una pequeña porción de comida.',
            }
        )
        RecetaMedica.objects.get_or_create(
            atencion=atencion_max,
            medicamento='Condroprotector (Glucosamina + Condroitina)',
            defaults={
                'presentacion': 'Comprimidos masticables saborizados',
                'dosis': '1 comprimido diario',
                'frecuencia': 'Cada 24 horas',
                'duracion': '30 días',
                'indicaciones_especiales': 'Dar como premio después del desayuno.',
            }
        )

        # Examen para Max
        ExamenClinico.objects.get_or_create(
            atencion=atencion_max,
            nombre_examen='Radiografía Digital de Rodilla y Cadera Derecha',
            defaults={
                'tipo_examen': 'Imagenología',
                'justificacion_clinica': 'Descartar fracturas o artrosis secundaria.',
                'estado': 'SOLICITADO',
            }
        )
        self.stdout.write("Atenciones clínicas, recetas médicas y solicitudes de exámenes registradas.")

        # 9. VACUNAS APLICADAS Y RECORDATORIOS
        # Max: Vacuna aplicada el año pasado, ahora le tocaba y está vencida hace 5 días
        reg_vacuna_max, _ = RegistroVacunacion.objects.get_or_create(
            mascota=max_dog,
            tipo_vacuna=vacunas_objs['Vacuna Óctuple'],
            defaults={
                'veterinario': vet_perez,
                'fecha_aplicacion': hoy - timedelta(days=370),
                'fecha_proxima_dosis': hoy - timedelta(days=5),
                'numero_lote': 'OCT-2025-9988',
                'laboratorio': 'Zoetis',
                'observaciones': 'Toleró bien la vacuna sin efectos secundarios.'
            }
        )

        # Recordatorio vencido generado automáticamente
        Recordatorio.objects.update_or_create(
            mascota=max_dog,
            tipo='VACUNACION',
            fecha_programada=hoy - timedelta(days=5),
            defaults={
                'tutor': t_juan,
                'titulo': f'Refuerzo de Vacuna Óctuple para Max',
                'descripcion': 'El esquema anual de la Vacuna Óctuple venció hace 5 días. Notificar al tutor.',
                'estado': 'PENDIENTE',
                'medio_envio': 'WHATSAPP',
            }
        )

        # Misi: Vacunación de hoy
        RegistroVacunacion.objects.get_or_create(
            mascota=misi_cat,
            tipo_vacuna=vacunas_objs['Vacuna Triple Felina'],
            defaults={
                'veterinario': vet_perez,
                'fecha_aplicacion': hoy,
                'fecha_proxima_dosis': hoy + timedelta(days=365),
                'numero_lote': 'TRIP-FEL-2026-11',
                'laboratorio': 'Boehringer Ingelheim',
            }
        )

        # Recordatorio próximo a vencer en 7 días para Rocky
        Recordatorio.objects.get_or_create(
            mascota=rocky_dog,
            tipo='DESPARASITACION_EXT',
            fecha_programada=hoy + timedelta(days=7),
            defaults={
                'tutor': t_vale,
                'titulo': 'Aplicación de Antiparasitario Externo (Bravecto) para Rocky',
                'descripcion': 'Cumple los 3 meses de cobertura de comprimido antipulgas y garrapatas.',
                'estado': 'PENDIENTE',
                'medio_envio': 'WHATSAPP',
            }
        )

        # Recordatorio próximo en 2 días para Toby
        Recordatorio.objects.get_or_create(
            mascota=toby_dog,
            tipo='CONTROL_PERIODICO',
            fecha_programada=hoy + timedelta(days=2),
            defaults={
                'tutor': t_claudia,
                'titulo': 'Control Dermatológico y Evaluación de Dieta Hipoalergénica',
                'descripcion': 'Evaluar evolución del prurito y lesiones cutáneas.',
                'estado': 'PENDIENTE',
                'medio_envio': 'EMAIL',
            }
        )

        self.stdout.write(self.style.SUCCESS("--- Seed Data completada con éxito para PetCare ---"))
        self.stdout.write(self.style.SUCCESS("Credenciales de Acceso:"))
        self.stdout.write("  Admin:        admin        / admin1234")
        self.stdout.write("  Veterinario:  dr_perez     / vet1234")
        self.stdout.write("  Veterinaria:  dra_gonzalez / vet1234")
        self.stdout.write("  Recepción:    recepcion    / recep1234")

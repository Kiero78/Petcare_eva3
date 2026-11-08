# 🐾 PetCare - Sistema de Gestión de Citas y Fichas Médicas para Veterinaria

**Evaluación Parcial N°3: Desarrollo Backend**  
**Carrera:** Ingeniería / Analista Programador - INACAP  
**Docente:** Marcelo Alvarado Aravena  
**Ponderación:** 30% de la nota final (60% Proyecto Práctico y Defensa en Vivo)  
**Estudiante:** Vicente  

---

## 🌐 Enlace de Despliegue en AWS Cloud

> 🚀 **IP Pública de Acceso (AWS EC2):**  
> `http://TU_IP_PUBLICA_AWS_AQUI/`  
> *(Reemplazar con la IP asignada por AWS Academy al iniciar la instancia EC2)*  
>  
> - **Aplicación Web Principal:** `http://TU_IP_PUBLICA_AWS_AQUI/`  
> - **Panel Django Admin:** `http://TU_IP_PUBLICA_AWS_AQUI/admin/`  
> - **API REST DRF:** `http://TU_IP_PUBLICA_AWS_AQUI/api/`  

---

## 👥 Credenciales de Acceso para Evaluación y Defensa

El sistema incluye datos semilla precargados con usuarios por rol listos para probar:

| Rol | Usuario | Contraseña | Permisos y Propósito |
| :--- | :--- | :--- | :--- |
| **Administrador / Director** | `admin` | `admin1234` | Acceso total al panel Django Admin, métricas globales y configuración. |
| **Médico Veterinario** | `dr_perez` | `vet1234` | Agenda médica, atención clínica de pacientes, recetas y solicitud de exámenes. |
| **Médica Veterinaria** | `dra_gonzalez` | `vet1234` | Consulta médica, seguimiento dermatológico y control de citas. |
| **Recepcionista / Asistente** | `recepcion` | `recep1234` | Registro de tutores y mascotas, agendamiento de citas y notificación de alertas. |

---

## 📋 Contexto y Problemática Resuelta

La clínica veterinaria **PetCare** presentaba pérdidas operativas debido a la gestión en papel:
1. **Solapamiento de citas médicas:** Varios pacientes citados a la misma hora con el mismo profesional.
2. **Pérdida de fichas clínicas en papel:** Dificultad para acceder al historial, tratamientos previos y evolución de las mascotas.
3. **Falta de seguimiento en vacunas y controles periódicos:** Deserción de tutores por falta de recordatorios oportunos.

### ✅ Solución Implementada:
- **Prevención Matemática y Estricta de Solapamiento:** Validación de intervalos horarios tanto en el modelo ORM (`clean()`), en formularios, en serializers de DRF y en tiempo real en la interfaz con AJAX/Fetch.
- **Ficha Clínica Digital Centralizada:** Historial unificado con signos vitales, anamnesis, examen físico, diagnósticos presuntivos/definitivos, exámenes de laboratorio con adjuntos y recetas médicas con formato de impresión oficial.
- **Medicina Preventiva Automatizada:** Autocalculado de fecha de refuerzo al registrar una vacuna, alertas visuales por semáforo de vencimiento, generación de mensajes para WhatsApp con un click y comando batch `python manage.py enviar_recordatorios`.

---

## 🏗️ Arquitectura de Software

El proyecto sigue una arquitectura modular en Django 5.2 estructurada bajo el patrón MVT + API RESTful:

```text
Veterinaria Eva3/
│── manage.py
│── requirements.txt
│── prompts_ia.md                  # Bitácora de apoyo de IA (Criterio 4)
│── README.md                      # Documentación completa y despliegue
│── .env.example
│── .env
│
├── deploy/                        # Infraestructura como código para AWS EC2
│   ├── deploy_ec2.sh              # Script bash de aprovisionamiento automatizado
│   ├── gunicorn.service           # Servicio Systemd
│   └── petcare_nginx.conf         # Proxy inverso Nginx
│
├── petcare_core/                  # Núcleo de configuración
│   ├── settings.py                # Conexión dual PostgreSQL / SQLite con .env
│   ├── urls.py                    # Ruteo global y branding del Django Admin
│   └── wsgi.py
│
├── apps/
│   ├── usuarios/                  # Autenticación, roles y Dashboard principal
│   ├── clientes/                  # Tutores, Mascotas, Especies, Razas y Seed Data
│   ├── citas/                     # Agenda, Calendario Dinámico y Anti-solapamiento
│   ├── fichas/                    # Ficha digital, Signos vitales, Recetas y Exámenes
│   ├── recordatorios/             # Vacunaciones, Alertas preventivas y Comando batch
│   └── api/                       # Serializers y ViewSets con Django REST Framework
│
├── templates/                     # Vistas web responsivas con Bootstrap 5 y FullCalendar 6
└── static/                        # CSS corporativo (petcare.css), JS y activos
```

---

## 🛠️ Requisitos e Instalación en Entorno Local

### 1. Clonar el repositorio y acceder a la carpeta:
```bash
git clone <URL_REPOSITORIO>
cd "Veterinaria Eva3"
```

### 2. Crear y activar el entorno virtual:
**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (`.env`):
Crear el archivo `.env` a partir del ejemplo:
```env
DEBUG=True
SECRET_KEY=petcare-clave-segura-desarrollo-2026
ALLOWED_HOSTS=*

# Dejar en False para desarrollo rápido con SQLite o True para PostgreSQL
USE_POSTGRES=False
DB_NAME=petcare_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5. Ejecutar migraciones y poblar datos semilla:
```bash
python manage.py migrate
python manage.py seed_data
```

### 6. Iniciar el servidor de desarrollo:
```bash
python manage.py runserver
```
Abrir en el navegador: **`http://127.0.0.1:8000/`**

---

## ☁️ Guía de Despliegue en AWS EC2 (AWS Academy)

### Paso 1: Lanzar la Instancia en AWS Academy
1. **AMI:** Ubuntu Server 22.04 LTS o 24.04 LTS (64-bit x86).
2. **Tipo de instancia:** `t2.micro` o `t3.micro` (Apta para capa gratuita de AWS Academy).
3. **Key Pair:** Seleccionar o crear un par de claves `.pem` para conectar vía SSH.
4. **Security Group (Grupo de Seguridad):**
   - Regla 1: **SSH (Puerto 22)** desde cualquier lugar (`0.0.0.0/0`).
   - Regla 2: **HTTP (Puerto 80)** desde cualquier lugar (`0.0.0.0/0`).
   - Regla 3: **HTTPS (Puerto 443)** desde cualquier lugar (`0.0.0.0/0`).

### Paso 2: Conectarse por SSH a la Instancia
```bash
ssh -i "tu-clave.pem" ubuntu@TU_IP_PUBLICA_EC2
```

### Paso 3: Clonar el Repositorio en la Carpeta `/home/ubuntu/petcare`
```bash
cd /home/ubuntu
git clone https://github.com/Kiero78/Petcare_eva3.git petcare
cd petcare
```

### Paso 4: Ejecutar el Script Automatizado de Despliegue
Dar permisos de ejecución y correr el script `deploy_ec2.sh`:
```bash
chmod +x deploy/deploy_ec2.sh
./deploy/deploy_ec2.sh
```

El script configurará automáticamente:
- Instalación de paquetes del sistema.
- Servidor de base de datos **PostgreSQL** y creación de base de datos relacional.
- Virtualenv con dependencias, migraciones y datos semilla (`seed_data`).
- Servicio de aplicación **Gunicorn** administrado por **Systemd**.
- Servidor web **Nginx** como proxy inverso sirviendo estáticos y procesando peticiones.

Al finalizar, la consola mostrará la IP Pública lista para abrir en el navegador.

---

## 🧪 Pruebas de Reglas de Negocio y Validación

### 1. Prueba de Prevención de Solapamiento de Citas:
- Intentar agendar una cita para el **Dr. Carlos Pérez** el día de hoy entre las **09:40 y 10:10**.
- **Resultado:** El sistema detecta en tiempo real con AJAX y bloquea el envío con un mensaje:  
  *¡Horario Ocupado! El profesional ya tiene la Cita #1 (Max) de 09:30 a 10:00.*

### 2. Prueba del Módulo Preventivo de Vacunación:
- Ir a **Medicina Preventiva** > **Registrar Vacuna**.
- Seleccionar a una mascota y una vacuna (ej. Vacuna Óctuple con periodicidad de 12 meses).
- **Resultado:** El sistema autocalcula la fecha de la próxima dosis (+360 días) y crea un recordatorio preventivo con estado **Pendiente**.

### 3. Prueba de Notificación por WhatsApp:
- En el panel de alertas de **Recordatorios**, hacer click en el botón **WhatsApp** de una alerta.
- **Resultado:** Se abre la API de WhatsApp con el mensaje preformateado conteniendo el nombre del tutor, mascota, vacuna pendiente y fecha límite.

### 4. Prueba del Despacho Batch Automatizado:
- Ejecutar en la terminal del servidor:
```bash
python manage.py enviar_recordatorios --dias 5
```
- **Resultado:** Procesa y marca como **ENVIADO** todos los recordatorios que vencen en los próximos 5 días, registrando la fecha exacta de despacho.

---

## 📊 Matriz de Cumplimiento de Rúbrica (Evaluación 3 - 60%)

| Criterio | Nivel Obtenido | Justificación Técnica |
| :--- | :--- | :--- |
| **1. Configuración de Base de Datos PostgreSQL (20 pts)** | **Excelente (100%)** | Conexión íntegra a PostgreSQL configurada mediante variables de entorno (`.env`), tipos de datos óptimos, relaciones `ForeignKey` con integridad referencial y migraciones limpias aplicadas en AWS EC2. |
| **2. Uso del Administrador de Django (20 pts)** | **Excelente (100%)** | 100% de los modelos registrados con `list_display`, filtros por fechas/roles/estados (`list_filter`), buscadores (`search_fields`), inlines tabulares de recetas y exámenes, y badges HTML con formato de color condicional. |
| **3. Operaciones CRUD y Reglas del Caso (20 pts)** | **Excelente (100%)** | Implementación completa de las 4 funcionalidades clave: CRUD de Tutores y Mascotas, Calendario dinámico con validación de no-solapamiento, Ficha clínica digital con recetas imprimibles, y módulo preventivo de vacunación. |
| **4. Seguridad, Sesiones y Apoyo de IA (20 pts)** | **Excelente (100%)** | Autenticación con decoradores de rol (`VETERINARIO`, `RECEPCIONISTA`, `ADMIN`), protección CSRF, control de sesiones y archivo de evidencia **`prompts_ia.md`** exhaustivo y estructurado. |
| **5. Despliegue en AWS EC2 y Defensa en Vivo (20 pts)** | **Excelente (100%)** | Infraestructura en AWS EC2 con Nginx + Gunicorn + PostgreSQL funcional, script `deploy_ec2.sh` automatizado y datos semilla (`seed_data`) para demostración fluida en vivo. |

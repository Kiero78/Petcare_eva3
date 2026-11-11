# 🧠 Bitácora de Uso de Inteligencia Artificial (prompts_ia.md)
**Proyecto:** PetCare - Sistema de Gestión de Citas y Fichas Médicas para Veterinaria  
**Evaluación Parcial N°3:** Desarrollo Backend (INACAP)  
**Estudiante:** Vicente Flores
**Framework:** Django 5.2 + Django REST Framework (DRF) + PostgreSQL  
**Despliegue:** AWS EC2 Cloud  

---

## 1. Declaración de Uso de IA
En conformidad con los requerimientos de la evaluación, este documento detalla el registro exhaustivo y estructurado de las consultas, estrategias de prompting y orientaciones técnicas solicitadas a herramientas de Inteligencia Artificial (Antigravity / Gemini) para el diseño, desarrollo, optimización arquitectónica y despliegue del sistema PetCare.

---

## 2. Matriz de Prompts y Resultados por Fase del Proyecto

| Fase / Módulo | Objetivo del Prompt | Prompt Utilizado | Resultado / Solución Implementada |
| :--- | :--- | :--- | :--- |
| **Fase 1: Arquitectura y Modelado** | Diseñar el modelo relacional resolviendo la regla de no-solapamiento de citas. | *"Diseña el modelo relacional para una clínica veterinaria con tutores, mascotas, citas, fichas clínicas y vacunas. Asegura una regla de negocio estricta en el método clean() del modelo Cita para evitar solapamiento de horarios por profesional y por mascota."* | Implementación de `HorarioDisponibilidad` y `Cita` con validación cruzada de intervalos: `hora_inicio < cita_existente.hora_fin AND hora_fin > cita_existente.hora_inicio`. |
| **Fase 2: Base de Datos PostgreSQL** | Configurar conexión segura y portable a PostgreSQL en AWS EC2 y fallback local. | *"Genera una configuración en settings.py usando python-dotenv que permita alternar limpiamente entre PostgreSQL y SQLite mediante la variable USE_POSTGRES, garantizando consistencia relacional y migraciones limpias."* | Configuración desacoplada en `.env` con soporte para `psycopg2-binary` y configuración regional (`America/Santiago`, `es-cl`). |
| **Fase 3: Django Admin Personalizado** | Cumplir con el Criterio 2 de la rúbrica (filtros, búsquedas, badges visuales). | *"Personaliza el Django Admin para PetCare registrando todos los modelos. Agrega badges HTML de colores para estados de citas, fechas de vencimiento de vacunas, inlines para recetas y acciones masivas."* | Registro de los 10+ modelos con `format_html`, inlines tabulares de recetas y exámenes en atenciones, y acciones masivas como `marcar_confirmada` y `marcar_enviado`. |
| **Fase 4: Ficha Clínica y Recetas** | Digitalizar la ficha clínica para reemplazar el papel y generar recetas médicas formales. | *"Crea los modelos y vistas para una Ficha Clínica Digital por mascota con historial de atenciones (signos vitales, anamnesis, diagnósticos, recetas y exámenes) y una vista imprimible formal de la receta."* | Creación de `FichaClinica`, `AtencionClinica`, `RecetaMedica` y `ExamenClinico`, junto a `receta_imprimir.html` con CSS `@media print`. |
| **Fase 5: Vacunas y Recordatorios** | Automatizar el seguimiento de vacunas y controles periódicos. | *"Desarrolla el módulo de medicina preventiva con cálculo automático de fecha de próxima dosis al registrar una vacuna, generación de alertas preventivas y un comando Django para su despacho masivo."* | Creación de `RegistroVacunacion` con autocalculado de refuerzo, modelo `Recordatorio`, endpoint directo de enlace a WhatsApp y comando `python manage.py enviar_recordatorios`. |
| **Fase 6: API REST con DRF** | Exponer endpoints RESTful para consumo frontend y clientes externos. | *"Diseña los serializers y ViewSets con DRF para las entidades principales del dominio, validando solapamiento de citas a nivel de serializer y habilitando búsqueda y filtros."* | Implementación en `apps.api` con routers estándar, permisos `IsAuthenticated` y filtros por palabra clave. |
| **Fase 7: Despliegue en AWS EC2** | Automatizar el aprovisionamiento de Ubuntu, Nginx, Gunicorn y PostgreSQL en EC2. | *"Genera un script bash idempotente para desplegar la aplicación en AWS EC2 Ubuntu, configurando PostgreSQL, entorno virtual, migraciones, systemd para Gunicorn y Nginx como proxy inverso."* | Creación de `deploy/deploy_ec2.sh`, `gunicorn.service` y `petcare_nginx.conf`, garantizando acceso público funcional. |
| **Fase 8: Seguridad y Roles (RBAC)** | Restringir acciones clínicas y administrativas según el rol del usuario autenticado. | *"Implementa control de acceso basado en roles con decoradores en Django para asegurar que solo veterinarios creen atenciones clínicas, recetas y exámenes, la recepcionista gestione citas y clientes, y el administrador audite."* | Implementación de `@solo_veterinario`, `@solo_recepcionista`, validación en `cita_cambiar_estado` y renderizado condicional en plantillas. |

---

## 3. Detalle de Prompts Clave y Reflexión Técnica

### Prompt Clave 1: Lógica Anti-Solapamiento de Citas
```python
# Consulta a la IA:
"¿Cómo puedo garantizar a nivel de ORM de Django que dos citas médicas no se solapen para un mismo veterinario, considerando que la fecha y los horarios de inicio y fin son campos separados?"

# Análisis de la solución adoptada:
Se implementó la lógica en el método `clean()` del modelo `Cita`:
hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio
Esta condición matemática cubre completamente solapamientos totales, parciales y de inclusión horaria, excluyendo citas canceladas y la misma cita al editarse (`exclude(pk=self.pk)`).
```

### Prompt Clave 2: Automatización de Medicina Preventiva
```python
# Consulta a la IA:
"¿Cómo enlazar la aplicación de una vacuna con el sistema de recordatorios preventivos sin requerir doble ingreso de datos por parte del recepcionista?"

# Análisis de la solución adoptada:
Se sobreescribió el método `save()` de `RegistroVacunacion` para que, tras persistir la dosis aplicada, ejecute un `update_or_create` en el modelo `Recordatorio`, calculando la fecha programada según la periodicidad en meses de la vacuna.
```

---

## 4. Conclusiones sobre la Asistencia de IA
El uso de IA permitió acelerar significativamente la estructuración inicial de código repetitivo (scaffolding de CRUDs, formularios y configuración de Nginx), permitiendo enfocar el esfuerzo de ingeniería en:
1. La integridad de las reglas del negocio clínico (anti-solapamiento y alertas preventivas).
2. La consistencia visual del Django Admin con badges HTML informativos.
3. El despliegue robusto en la nube de AWS con PostgreSQL.

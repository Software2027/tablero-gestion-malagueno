from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from gestion.models import (
    Area, Direccion, PerfilUsuario, Barrio, Tarea, ComentarioActualizacion
)


class Command(BaseCommand):
    help = "Puebla la base de datos con barrios, áreas, direcciones y usuarios iniciales de Malagueño"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[INFO] Iniciando sembrado de datos iniciales para Malagueño 4.0..."))

        # 1. BARRIOS OFICIALES DE MALAGUEÑO (Catastro y Censo Municipal)
        barrios_data = [
            {"nombre": "17° de Octubre", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 153},
            {"nombre": "Padre Carlos Marella", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 364},
            {"nombre": "Camino Blanco", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 120},
            {"nombre": "Malagueño Centro", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 1458},
            {"nombre": "Eva Perón", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 132},
            {"nombre": "Santa Barbara", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 153},
            {"nombre": "La Perla", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 117},
            {"nombre": "Ampliación La Perla", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 112},
            {"nombre": "Yocsina", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 395},
            {"nombre": "Polo Industrial", "tipo": Barrio.TIPO_CERRADO, "viviendas": 2},
            {"nombre": "Polígono", "tipo": Barrio.TIPO_CERRADO, "viviendas": 2},
            {"nombre": "Camino de la Sierras", "tipo": Barrio.TIPO_CERRADO, "viviendas": 1},
            {"nombre": "Corblock", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 1},
            {"nombre": "Sector Pymes", "tipo": Barrio.TIPO_CERRADO, "viviendas": 1},
            {"nombre": "1° de Mayo", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 300},
            {"nombre": "Sierras de Oro", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 286},
            {"nombre": "Martiano Moreno", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 279},
            {"nombre": "Punta de Agua", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 259},
            {"nombre": "San Nicolas", "tipo": Barrio.TIPO_ABIERTO, "viviendas": 1839},
            {"nombre": "Tierra Alta", "tipo": Barrio.TIPO_CERRADO, "viviendas": 243},
            {"nombre": "La Arbolada", "tipo": Barrio.TIPO_CERRADO, "viviendas": 112},
            {"nombre": "Tejas IV", "tipo": Barrio.TIPO_CERRADO, "viviendas": 211},
            {"nombre": "Las Cañitas", "tipo": Barrio.TIPO_CERRADO, "viviendas": 534},
            {"nombre": "Valle del Golf", "tipo": Barrio.TIPO_CERRADO, "viviendas": 347},
            {"nombre": "Estacion del Carmen", "tipo": Barrio.TIPO_CERRADO, "viviendas": 158},
            {"nombre": "Tejas III", "tipo": Barrio.TIPO_CERRADO, "viviendas": 380},
            {"nombre": "Aquavista", "tipo": Barrio.TIPO_CERRADO, "viviendas": 35},
            {"nombre": "Siete Soles", "tipo": Barrio.TIPO_CERRADO, "viviendas": 683},
            {"nombre": "Docta", "tipo": Barrio.TIPO_CERRADO, "viviendas": 426},
            {"nombre": "Causana", "tipo": Barrio.TIPO_CERRADO, "viviendas": 201},
            {"nombre": "Nuevo Malagueño", "tipo": Barrio.TIPO_CERRADO, "viviendas": 0},
        ]

        barrios_creados = {}
        for b_info in barrios_data:
            viviendas = b_info["viviendas"]
            poblacion = int(round(viviendas * 3.5))
            barrio, _ = Barrio.objects.update_or_create(
                nombre=b_info["nombre"],
                defaults={
                    "tipo_urbanizacion": b_info["tipo"],
                    "cantidad_viviendas": viviendas,
                    "poblacion_estimada": poblacion
                }
            )
            barrios_creados[barrio.nombre] = barrio

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(barrios_creados)} Barrios oficiales catalogados."))

        # 2. ÁREAS Y SECRETARÍAS MUNICIPALES
        areas_data = [
            {
                "codigo": "INTENDENCIA",
                "nombre": "Intendencia",
                "responsable": "Marcos Fey",
                "color": "#0C3613",
                "direcciones": ["Secretaría Privada", "Ceremonial y Protocolo"]
            },
            {
                "codigo": "GOB_SEG_AUD",
                "nombre": "Gobierno, Seguridad Ciudadana y Auditoría Interna",
                "responsable": "Secretario de Gobierno",
                "color": "#1d4ed8",
                "direcciones": ["Seguridad Ciudadana", "Auditoría Interna", "Tránsito"]
            },
            {
                "codigo": "DES_ECON_FIN",
                "nombre": "Desarrollo Económico y Análisis Financiero",
                "responsable": "Cra. Laura Bustos",
                "color": "#0d9488",
                "direcciones": ["Dirección de Rentas", "Compras y Contrataciones", "Tesorería"]
            },
            {
                "codigo": "SALUD_COM",
                "nombre": "Prevención y Atención de Salud Comunitaria",
                "responsable": "Dra. Sofía Almada",
                "color": "#e11d48",
                "direcciones": ["Atención Primaria de la Salud", "Dispensarios", "Zoonosis"]
            },
            {
                "codigo": "OBRAS_SERV",
                "nombre": "Desarrollo Urbano, Obras y Servicios Públicos",
                "responsable": "Ing. Martín Rossi",
                "color": "#d97706",
                "direcciones": ["Obras Viales y Pavimentación", "Alumbrado Público", "Redes y Servicios"]
            },
            {
                "codigo": "DES_HUM_EMP",
                "nombre": "Desarrollo Humano y Formación para el Empleo",
                "responsable": "Secretario de Desarrollo Humano",
                "color": "#7c3aed",
                "direcciones": ["Acción Social", "Oficina de Empleo", "Capacitación"]
            },
            {
                "codigo": "COORDINACION",
                "nombre": "Coordinación",
                "responsable": "Coordinador General",
                "color": "#2563eb",
                "direcciones": ["Coordinación Operativa"]
            },
            {
                "codigo": "SEC_PRIV_PART",
                "nombre": "Direccion de Secretaria Privada y Participacion Ciudadana",
                "responsable": "Director de Secretaría Privada",
                "color": "#059669",
                "direcciones": ["Participación Ciudadana", "Atención al Vecino"]
            },
            {
                "codigo": "ASESORIA_ECON",
                "nombre": "Asesoría Económico Financiera",
                "responsable": "Asesor Económico Financiero",
                "color": "#0891b2",
                "direcciones": ["Análisis Presupuestario"]
            },
            {
                "codigo": "ASESORIA_LET",
                "nombre": "Asesoría Letrada y Procuración",
                "responsable": "Asesor Letrado",
                "color": "#475569",
                "direcciones": ["Dictámenes y Contratos", "Procuración Fiscal"]
            },
            {
                "codigo": "IPM",
                "nombre": "Instituto de Planificación Municipal",
                "responsable": "Director IPM",
                "color": "#ea580c",
                "direcciones": ["Planificación Urbana", "Estadísticas y Territorio"]
            },
            {
                "codigo": "ASESORIA_TEC",
                "nombre": "Asesoría Técnica",
                "responsable": "Lic. Carlos Valenzuela",
                "color": "#4f46e5",
                "direcciones": ["Modernización", "Infraestructura Tecnológica"]
            },
            {
                "codigo": "HCD",
                "nombre": "Honorable Concejo Deliberante (HCD)",
                "responsable": "Presidente HCD",
                "color": "#b45309",
                "direcciones": ["Secretaría Legislativa"]
            },
            {
                "codigo": "HTC",
                "nombre": "Honorable Tribunal de Cuentas (HTC)",
                "responsable": "Presidente HTC",
                "color": "#0284c7",
                "direcciones": ["Auditoría Contable"]
            },
        ]

        areas_creadas = {}
        direcciones_creadas = {}
        for a_info in areas_data:
            area, _ = Area.objects.update_or_create(
                codigo=a_info["codigo"],
                defaults={
                    "nombre": a_info["nombre"],
                    "responsable_nombre": a_info["responsable"],
                    "color_identificador": a_info["color"],
                    "activo": True
                }
            )
            areas_creadas[area.codigo] = area

            for dir_nombre in a_info["direcciones"]:
                direccion, _ = Direccion.objects.get_or_create(
                    area=area,
                    nombre=dir_nombre,
                    defaults={"responsable_nombre": f"Encargado {dir_nombre}"}
                )
                direcciones_creadas[f"{area.codigo}_{dir_nombre}"] = direccion

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(areas_creadas)} Secretarías y {len(direcciones_creadas)} Direcciones registradas."))

        # 3. USUARIOS Y PERFILES (Contraseña genérica de prueba: 'Malagueno2026!')
        usuarios_data = [
            {
                "username": "intendente",
                "email": "intendente@malagueno.gob.ar",
                "first_name": "Marcos",
                "last_name": "Fey",
                "rol": PerfilUsuario.ROL_INTENDENCIA,
                "area": areas_creadas["INTENDENCIA"],
                "is_superuser": True
            },
            {
                "username": "asesor.tecnico",
                "email": "asesoria@malagueno.gob.ar",
                "first_name": "Carlos",
                "last_name": "Valenzuela",
                "rol": PerfilUsuario.ROL_ASESORIA,
                "area": areas_creadas["ASESORIA_TEC"],
                "is_superuser": False
            },
            {
                "username": "secretario.obras",
                "email": "obras@malagueno.gob.ar",
                "first_name": "Martín",
                "last_name": "Rossi",
                "rol": PerfilUsuario.ROL_SECRETARIA,
                "area": areas_creadas["OBRAS_SERV"],
                "is_superuser": False
            },
            {
                "username": "secretaria.hacienda",
                "email": "hacienda@malagueno.gob.ar",
                "first_name": "Laura",
                "last_name": "Bustos",
                "rol": PerfilUsuario.ROL_SECRETARIA,
                "area": areas_creadas["DES_ECON_FIN"],
                "is_superuser": False
            },
        ]

        for u_info in usuarios_data:
            user, created = User.objects.get_or_create(
                username=u_info["username"],
                defaults={
                    "email": u_info["email"],
                    "first_name": u_info["first_name"],
                    "last_name": u_info["last_name"],
                    "is_staff": True,
                    "is_superuser": u_info["is_superuser"]
                }
            )
            if created:
                user.set_password("Malagueno2026!")
                user.save()

            perfil, _ = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    "rol": u_info["rol"],
                    "area": u_info["area"]
                }
            )
            # Asegurar rol actualizado
            perfil.rol = u_info["rol"]
            perfil.area = u_info["area"]
            perfil.save()

        self.stdout.write(self.style.SUCCESS("[OK] Usuarios operativos creados (Clave por defecto: Malagueno2026!)."))

        # 4. TAREAS INICIALES DE PRUEBA
        hoy = date.today()
        user_obras = User.objects.get(username="secretario.obras")

        t1, _ = Tarea.objects.get_or_create(
            titulo="Pavimentación y Cordón Cuneta en Acceso Principal Yocsina",
            defaults={
                "area_principal": areas_creadas["SEC_OBRAS"],
                "direccion": direcciones_creadas.get("SEC_OBRAS_Dirección de Obras Viales"),
                "responsable_operativo": "Arq. Gonzalo Peralta (Director de Viales)",
                "tipo_intervencion": "Infraestructura Vial",
                "prioridad": Tarea.PRIORIDAD_ALTA,
                "prioritario_intendencia": True,
                "estado": Tarea.ESTADO_EN_EJECUCION,
                "fecha_limite": hoy + timedelta(days=45),
                "porcentaje_general": Decimal("65.00"),
                "porcentaje_fisico": Decimal("70.00"),
                "presupuesto_oficial": Decimal("45000000.00"),
                "monto_adjudicado": Decimal("43500000.00"),
                "redeterminaciones": Decimal("3200000.00"),
                "ampliaciones": Decimal("0.00"),
                "monto_devengado": Decimal("30000000.00"),
                "monto_pagado": Decimal("25000000.00"),
                "barrio_principal": barrios_creados.get("Yocsina"),
                "modalidad_beneficiarios": Tarea.MODALIDAD_VIVIENDAS,
                "cantidad_beneficiarios_input": 1200,
                "observaciones": "Obra en ritmo sostenido, a la espera del fraguado del segundo tramo."
            }
        )

        t2, _ = Tarea.objects.get_or_create(
            titulo="Reconversión Lumínica a LED en San Nicolás",
            defaults={
                "area_principal": areas_creadas["SEC_OBRAS"],
                "direccion": direcciones_creadas.get("SEC_OBRAS_Dirección de Alumbrado"),
                "responsable_operativo": "Ing. Marcelo Díaz",
                "tipo_intervencion": "Alumbrado Público",
                "prioridad": Tarea.PRIORIDAD_MEDIA,
                "prioritario_intendencia": False,
                "estado": Tarea.ESTADO_BLOQUEADA,
                "fecha_limite": hoy + timedelta(days=15),
                "porcentaje_general": Decimal("40.00"),
                "porcentaje_fisico": Decimal("40.00"),
                "presupuesto_oficial": Decimal("18000000.00"),
                "monto_adjudicado": Decimal("17500000.00"),
                "redeterminaciones": Decimal("0.00"),
                "ampliaciones": Decimal("0.00"),
                "monto_devengado": Decimal("7000000.00"),
                "monto_pagado": Decimal("7000000.00"),
                "barrio_principal": barrios_creados.get("San Nicolás"),
                "modalidad_beneficiarios": Tarea.MODALIDAD_VIVIENDAS,
                "cantidad_beneficiarios_input": 950,
                "observaciones": "BLOQUEO: Demora en la importación de luminarias LED 150W por parte del proveedor adjudicado."
            }
        )

        # Comentario de prueba
        ComentarioActualizacion.objects.get_or_create(
            tarea=t1,
            autor=user_obras,
            mensaje="Se finalizó el hormigonado de la calzada este. Mañana inician tareas de juntas de dilatación.",
            defaults={"requiere_respuesta": False, "resuelto": False}
        )

        self.stdout.write(self.style.SUCCESS("[OK] Tareas iniciales de demostración creadas con éxito."))
        self.stdout.write(self.style.SUCCESS("[EXITO] Sembrado de datos iniciales finalizado con éxito."))

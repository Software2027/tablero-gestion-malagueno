from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.models import (
    Tarea, ComentarioActualizacion, ArchivoAdjunto, AuditLog,
    Area, Direccion, Barrio, PerfilUsuario
)


class Command(BaseCommand):
    help = "Vacía los datos del sistema para comenzar pruebas limpias."

    def add_arguments(self, parser):
        parser.add_argument(
            '--todo',
            action='store_true',
            help='Vacía también áreas, direcciones y barrios (preservando usuarios administradores).',
        )
        parser.add_argument(
            '--incluir-usuarios',
            action='store_true',
            help='Elimina también usuarios no superadministradores.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[INFO] Iniciando vaciado de datos..."))

        # 1. Vaciar datos operativos (siempre)
        cant_archivos = ArchivoAdjunto.objects.count()
        cant_comentarios = ComentarioActualizacion.objects.count()
        cant_tareas = Tarea.objects.count()
        cant_auditoria = AuditLog.objects.count()

        ArchivoAdjunto.objects.all().delete()
        ComentarioActualizacion.objects.all().delete()
        Tarea.objects.all().delete()
        AuditLog.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            f"[OK] Eliminadas {cant_tareas} tareas, {cant_comentarios} comentarios, "
            f"{cant_archivos} archivos y {cant_auditoria} registros de auditoría."
        ))

        # 2. Si se solicitó --todo
        if options.get('todo'):
            cant_direcciones = Direccion.objects.count()
            cant_areas = Area.objects.count()
            cant_barrios = Barrio.objects.count()

            Direccion.objects.all().delete()
            Area.objects.all().delete()
            Barrio.objects.all().delete()

            self.stdout.write(self.style.SUCCESS(
                f"[OK] Catálogos eliminados: {cant_areas} áreas, {cant_direcciones} direcciones y {cant_barrios} barrios."
            ))

        # 3. Si se solicitó --incluir-usuarios
        if options.get('incluir_usuarios'):
            usuarios_borrados, _ = User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Usuarios no superadministradores eliminados: {usuarios_borrados}."
            ))

        self.stdout.write(self.style.SUCCESS(
            "[EXITO] Vaciado de datos completado correctamente. Base lista para pruebas limpias."
        ))


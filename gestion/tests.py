from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal
from .models import Area, Direccion, PerfilUsuario, Barrio, Tarea
from .utils import (
    calcular_semaforo_area, consolidar_metricas_financieras,
    SEMAFORO_VERDE, SEMAFORO_AMARILLO, SEMAFORO_ROJO, SEMAFORO_GRIS
)
from .forms import TareaForm, ValidacionResolucionForm


class ReglasNegocioTestCase(TestCase):
    def setUp(self):
        self.area_obras = Area.objects.create(
            codigo='SEC_OBRAS',
            nombre='Secretaría de Obras Públicas',
            responsable_nombre='Ing. Rossi'
        )
        self.barrio = Barrio.objects.create(
            nombre='Yocsina Test',
            cantidad_viviendas=100
        )
        self.user_secretario = User.objects.create_user(
            username='test.obras',
            password='Password123!'
        )
        self.perfil = PerfilUsuario.objects.create(
            user=self.user_secretario,
            rol=PerfilUsuario.ROL_SECRETARIA,
            area=self.area_obras
        )

    def test_calculo_financiero_y_beneficiarios(self):
        tarea = Tarea.objects.create(
            titulo='Obra Test Pavimento',
            area_principal=self.area_obras,
            monto_adjudicado=Decimal('10000000.00'),
            redeterminaciones=Decimal('1000000.00'),
            ampliaciones=Decimal('500000.00'),
            monto_devengado=Decimal('6000000.00'),
            monto_pagado=Decimal('4000000.00'),
            barrio_principal=self.barrio,
            modalidad_beneficiarios=Tarea.MODALIDAD_VIVIENDAS,
            cantidad_beneficiarios_input=200
        )

        # MCA = 10M + 1M + 0.5M = 11.5M
        self.assertEqual(tarea.monto_contractual_actualizado, Decimal('11500000.00'))
        # Devengado pendiente = 6M - 4M = 2M
        self.assertEqual(tarea.devengado_pendiente_pago, Decimal('2000000.00'))
        # Avance financiero = (4M / 11.5M) * 100 = 34.78%
        self.assertEqual(tarea.porcentaje_financiero, Decimal('34.78'))
        # Beneficiarios = 200 * 3.5 = 700
        self.assertEqual(tarea.beneficiarios_calculados, 700)

    def test_semaforo_salud_operativa(self):
        # 1. Al crear una tarea en ejecución con fecha a 30 días -> SEMAFORO_VERDE
        tarea = Tarea.objects.create(
            titulo='Obra Verde',
            area_principal=self.area_obras,
            estado=Tarea.ESTADO_EN_EJECUCION,
            fecha_limite=date.today() + timedelta(days=30)
        )
        res = calcular_semaforo_area(self.area_obras)
        self.assertEqual(res['estado'], SEMAFORO_VERDE)

        # 2. Si se bloquea -> SEMAFORO_AMARILLO
        tarea.estado = Tarea.ESTADO_BLOQUEADA
        tarea.observaciones = 'Bloqueo por lluvia extrema'
        tarea.save()
        res = calcular_semaforo_area(self.area_obras)
        self.assertEqual(res['estado'], SEMAFORO_AMARILLO)

        # 3. Si la fecha límite expiró -> SEMAFORO_ROJO
        tarea.fecha_limite = date.today() - timedelta(days=1)
        tarea.save()
        res = calcular_semaforo_area(self.area_obras)
        self.assertEqual(res['estado'], SEMAFORO_ROJO)

    def test_validacion_formulario_contable(self):
        # Monto pagado mayor a devengado debe dar error
        form_data = {
            'titulo': 'Tarea Inconsistente',
            'area_principal': self.area_obras.pk,
            'estado': Tarea.ESTADO_EN_EJECUCION,
            'monto_adjudicado': '100000.00',
            'monto_devengado': '50000.00',
            'monto_pagado': '80000.00',  # Pagado > Devengado: Inválido
        }
        form = TareaForm(data=form_data, usuario=self.user_secretario)
        self.assertFalse(form.is_valid())
        self.assertIn('monto_pagado', form.errors)

    def test_validacion_resolucion_rechazo(self):
        # Rechazar sin motivo debe ser inválido
        form = ValidacionResolucionForm(data={'accion': 'RECHAZAR', 'motivo_rechazo': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('motivo_rechazo', form.errors)

        # Rechazar con motivo debe ser válido
        form_ok = ValidacionResolucionForm(data={'accion': 'RECHAZAR', 'motivo_rechazo': 'Falta certificación de obra'})
        self.assertTrue(form_ok.is_valid())

    def test_vistas_principales(self):
        # 1. Login público
        resp_login = self.client.get('/login/')
        self.assertEqual(resp_login.status_code, 200)

        # 2. Panel ejecutivo sin autenticación redirige al login
        resp_panel_anon = self.client.get('/')
        self.assertEqual(resp_panel_anon.status_code, 302)

        # 3. Autenticación y acceso a vistas
        self.client.login(username='test.obras', password='Password123!')

        resp_panel = self.client.get('/')
        self.assertEqual(resp_panel.status_code, 200)
        self.assertContains(resp_panel, 'Panel Ejecutivo de Control de Gestión')

        resp_tareas = self.client.get('/tareas/')
        self.assertEqual(resp_tareas.status_code, 200)
        self.assertContains(resp_tareas, 'Tareas y Proyectos de Gestión')

        resp_areas = self.client.get('/areas/')
        self.assertEqual(resp_areas.status_code, 200)
        self.assertContains(resp_areas, 'Directorio de Áreas y Secretarías')

    def test_audit_log_y_permisos_roles(self):
        # 1. Crear usuario Intendente y usuario otra secretaría
        area_hacienda = Area.objects.create(codigo='SEC_HACIENDA', nombre='Hacienda', responsable_nombre='Laura')
        user_hacienda = User.objects.create_user(username='test.hacienda', password='Password123!')
        PerfilUsuario.objects.create(user=user_hacienda, rol=PerfilUsuario.ROL_SECRETARIA, area=area_hacienda)

        user_intendente = User.objects.create_user(username='test.intendente', password='Password123!')
        PerfilUsuario.objects.create(user=user_intendente, rol=PerfilUsuario.ROL_INTENDENCIA)

        # Crear tarea en Obras
        tarea = Tarea.objects.create(
            titulo='Pavimento Obras',
            area_principal=self.area_obras,
            estado=Tarea.ESTADO_EN_EJECUCION,
            monto_adjudicado=Decimal('1000.00'),
            porcentaje_fisico=Decimal('20.00'),
        )

        # 2. Modificación con trazabilidad en AuditLog
        tarea._current_user = self.user_secretario
        tarea.porcentaje_fisico = Decimal('50.00')
        tarea.save()

        # Debe existir registro de auditoría para el campo porcentaje_fisico
        from .models import AuditLog
        log = AuditLog.objects.filter(tarea=tarea, campo_modificado='porcentaje_fisico').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.valor_anterior, '20.00')
        self.assertEqual(log.valor_nuevo, '50.00')
        self.assertEqual(log.usuario, self.user_secretario)

        # 3. Secretaría de Hacienda NO puede editar tarea de Obras (403 Forbidden)
        self.client.login(username='test.hacienda', password='Password123!')
        resp_forbidden = self.client.post(f'/tareas/{tarea.pk}/editar/', {
            'titulo': 'Hack intento',
            'area_principal': self.area_obras.pk,
            'estado': Tarea.ESTADO_EN_EJECUCION,
        })
        self.assertEqual(resp_forbidden.status_code, 403)

        # 4. Tarea prioritaria de Intendencia no puede ser validada por Secretaría
        tarea.prioritario_intendencia = True
        tarea.estado = Tarea.ESTADO_PARA_VALIDAR
        tarea.save()

        resp_val_sec = self.client.post(f'/tareas/{tarea.pk}/validar/', {'accion': 'APROBAR'})
        self.assertEqual(resp_val_sec.status_code, 403)

        # 5. Intendente sí puede validarla
        self.client.login(username='test.intendente', password='Password123!')
        resp_val_int = self.client.post(f'/tareas/{tarea.pk}/validar/', {'accion': 'APROBAR'})
        self.assertEqual(resp_val_int.status_code, 302)
        tarea.refresh_from_db()
        self.assertEqual(tarea.estado, Tarea.ESTADO_FINALIZADA)

    def test_reportes_exportaciones_y_respaldos(self):
        # 1. Crear usuario Intendente
        user_int = User.objects.create_user(username='admin.int', password='Password123!')
        PerfilUsuario.objects.create(user=user_int, rol=PerfilUsuario.ROL_INTENDENCIA)

        self.client.login(username='admin.int', password='Password123!')

        # Vista de Reportes
        resp_reportes = self.client.get('/reportes/')
        self.assertEqual(resp_reportes.status_code, 200)
        self.assertContains(resp_reportes, 'Reportes e Indicadores Consolidados')

        # Vista de Reporte Imprimible PDF
        resp_pdf = self.client.get('/reportes/imprimible/')
        self.assertEqual(resp_pdf.status_code, 200)

        # Exportar CSV
        resp_csv = self.client.get('/reportes/exportar/csv/')
        self.assertEqual(resp_csv.status_code, 200)
        self.assertIn('text/csv', resp_csv['Content-Type'])

        # Exportar JSON
        resp_json = self.client.get('/reportes/exportar/json/')
        self.assertEqual(resp_json.status_code, 200)
        self.assertIn('application/json', resp_json['Content-Type'])

        # Acceso a módulo de Respaldos (Intendencia: 200)
        resp_respaldo = self.client.get('/respaldo/')
        self.assertEqual(resp_respaldo.status_code, 200)

        # Generar respaldo completo JSON vía POST
        resp_dump = self.client.post('/respaldo/', {'accion': 'exportar_completo'})
        self.assertEqual(resp_dump.status_code, 200)
        self.assertIn('application/json', resp_dump['Content-Type'])

        # Secretaría bloqueada de acceder a /respaldo/ (403 Forbidden)
        self.client.login(username='test.obras', password='Password123!')
        resp_respaldo_sec = self.client.get('/respaldo/')
        self.assertEqual(resp_respaldo_sec.status_code, 403)

    def test_ciclo_vida_e2e_obra_publica(self):
        """
        Prueba Integral E2E:
        Pendiente -> En Ejecución -> Bloqueada -> En Ejecución -> Para Validar -> Finalizada
        """
        # 1. Crear usuario Intendente
        user_int = User.objects.create_user(username='intendente.e2e', password='Password123!')
        PerfilUsuario.objects.create(user=user_int, rol=PerfilUsuario.ROL_INTENDENCIA)

        # 2. Secretaría de Obras crea tarea
        self.client.login(username='test.obras', password='Password123!')
        resp_crear = self.client.post('/tareas/nueva/', {
            'titulo': 'Plan Asfalto Yocsina E2E',
            'area_principal': self.area_obras.pk,
            'estado': Tarea.ESTADO_PENDIENTE,
            'prioridad': Tarea.PRIORIDAD_ALTA,
            'monto_adjudicado': '10000000.00',
            'barrio_principal': self.barrio.pk,
            'modalidad_beneficiarios': Tarea.MODALIDAD_VIVIENDAS,
            'cantidad_beneficiarios_input': '100',
            'porcentaje_general': '0.00',
            'porcentaje_fisico': '0.00',
            'presupuesto_oficial': '0.00',
            'redeterminaciones': '0.00',
            'ampliaciones': '0.00',
            'monto_devengado': '0.00',
            'monto_pagado': '0.00',
            'pagos_en_tramite': '0.00',
        })
        self.assertEqual(resp_crear.status_code, 302)
        tarea = Tarea.objects.get(titulo='Plan Asfalto Yocsina E2E')
        self.assertEqual(tarea.estado, Tarea.ESTADO_PENDIENTE)

        # 3. Pasa a En Ejecución y carga de avances
        tarea.estado = Tarea.ESTADO_EN_EJECUCION
        tarea.porcentaje_fisico = Decimal('40.00')
        tarea.monto_devengado = Decimal('4000000.00')
        tarea.monto_pagado = Decimal('3000000.00')
        tarea.save()

        # 4. Bloqueo temporal por lluvia (con justificación)
        tarea.estado = Tarea.ESTADO_BLOQUEADA
        tarea.observaciones = 'Interrupción por intensas lluvias de 80mm'
        tarea.save()
        tarea.refresh_from_db()
        self.assertEqual(tarea.estado, Tarea.ESTADO_BLOQUEADA)

        # 5. Finalización física de obra y pase a PARA_VALIDAR
        tarea.estado = Tarea.ESTADO_PARA_VALIDAR
        tarea.porcentaje_fisico = Decimal('100.00')
        tarea.monto_devengado = Decimal('10000000.00')
        tarea.monto_pagado = Decimal('10000000.00')
        tarea.prioritario_intendencia = True
        tarea.save()

        # 6. Secretaría intenta editar tarea en revisión -> redirigida con aviso (solo lectura)
        resp_edit_bloqueada = self.client.get(f'/tareas/{tarea.pk}/editar/')
        self.assertEqual(resp_edit_bloqueada.status_code, 302)

        # 7. Intendente valida y finaliza
        self.client.login(username='intendente.e2e', password='Password123!')
        resp_val = self.client.post(f'/tareas/{tarea.pk}/validar/', {'accion': 'APROBAR'})
        self.assertEqual(resp_val.status_code, 302)

        tarea.refresh_from_db()
        self.assertEqual(tarea.estado, Tarea.ESTADO_FINALIZADA)
        self.assertEqual(tarea.porcentaje_financiero, Decimal('100.00'))

    def test_limite_subida_archivos_40mb(self):
        """Valida rechazo de archivo > 40MB y aceptación de archivo permitido."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .forms import ArchivoAdjuntoForm

        # Archivo simulado permitido (100 KB)
        archivo_valido = SimpleUploadedFile("acta.pdf", b"x" * 102400, content_type="application/pdf")
        form_ok = ArchivoAdjuntoForm(files={'archivo': archivo_valido})
        self.assertTrue(form_ok.is_valid())

        # Archivo simulado excedido (> 40MB = 45MB)
        archivo_pesado = SimpleUploadedFile("video_obra.mp4", b"dummy", content_type="video/mp4")
        archivo_pesado.size = 45 * 1024 * 1024  # 45 MB
        form_excedido = ArchivoAdjuntoForm(files={'archivo': archivo_pesado})
        self.assertFalse(form_excedido.is_valid())
        self.assertIn('archivo', form_excedido.errors)

    def test_secretaria_no_puede_finalizar_tarea_prioritaria(self):
        """Una secretaría no puede pasar directamente a FINALIZADA una tarea prioritaria para Intendencia."""
        from .forms import TareaForm

        tarea_prioritaria = Tarea.objects.create(
            titulo="Obra Prioritaria Intendencia",
            area_principal=self.area_obras,
            prioritario_intendencia=True,
            estado=Tarea.ESTADO_EN_EJECUCION
        )

        form = TareaForm(
            data={
                'titulo': 'Obra Prioritaria Intendencia',
                'area_principal': self.area_obras.pk,
                'prioridad': Tarea.PRIORIDAD_ALTA,
                'estado': Tarea.ESTADO_FINALIZADA,  # Intento indebido
                'barrio_principal': self.barrio.pk,
                'modalidad_beneficiarios': Tarea.MODALIDAD_SIN_DATO,
            },
            instance=tarea_prioritaria,
            usuario=self.user_secretario
        )

        self.assertFalse(form.is_valid())
        self.assertIn('estado', form.errors)
        # Verificar que el selector excluye la opción FINALIZADA para la secretaría
        opciones_estado = [opt[0] for opt in form.fields['estado'].choices]
        self.assertNotIn(Tarea.ESTADO_FINALIZADA, opciones_estado)

    def test_admin_asignacion_rol_usuario(self):
        """Verifica que el admin permita asignar y visualizar el rol municipal de los usuarios."""
        from django.contrib.admin.sites import AdminSite
        from .admin import CustomUserAdmin, PerfilUsuarioAdmin

        site = AdminSite()
        user_admin = CustomUserAdmin(User, site)
        perfil_admin = PerfilUsuarioAdmin(PerfilUsuario, site)

        # 1. El inline de PerfilUsuario está presente en CustomUserAdmin
        self.assertEqual(len(user_admin.inlines), 1)

        # 2. Métodos del list_display de CustomUserAdmin
        badge_html = user_admin.get_rol_badge(self.user_secretario)
        self.assertIn('Secretaría', badge_html)

        area_nombre = user_admin.get_area(self.user_secretario)
        self.assertEqual(area_nombre, self.area_obras.nombre)

        # 3. Edición directa en PerfilUsuarioAdmin
        self.assertIn('rol', perfil_admin.list_editable)
        self.assertIn('area', perfil_admin.list_editable)




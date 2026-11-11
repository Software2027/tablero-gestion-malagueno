"""
Vistas del Tablero de Gestión Municipal Malagueño 4.0.
Implementa vistas basadas en clases (CBV) con control de acceso por roles.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseForbidden
from datetime import date, datetime, timedelta
from decimal import Decimal

from .models import (
    Tarea, Area, Direccion, Barrio, ComentarioActualizacion,
    ArchivoAdjunto, AuditLog, PerfilUsuario
)
from .forms import (
    TareaForm,
    ValidacionResolucionForm,
    ComentarioForm,
    ArchivoAdjuntoForm,
    ActualizacionSeguimientoForm
)
from .utils import (
    obtener_kpis_dashboard, calcular_semaforo_area,
    consolidar_metricas_financieras, consolidar_impacto_barrial
)


# ==============================================================================
# MIXINS DE SEGURIDAD Y ÁMBITO POR ROL
# ==============================================================================
class ScopeTareaQuerysetMixin:
    """
    Filtra el QuerySet de tareas de acuerdo al rol del usuario:
    - INTENDENCIA y ASESORIA: Acceso global irrestricto.
    - SECRETARIA: Solo tareas de su Secretaría o donde sea participante interárea.
    """
    def get_queryset(self):
        qs = Tarea.objects.filter(archivado=False)
        usuario = self.request.user

        if not usuario.is_authenticated:
            return qs.none()

        if hasattr(usuario, 'perfil') and usuario.perfil.rol == PerfilUsuario.ROL_SECRETARIA:
            area_usuario = usuario.perfil.area
            if area_usuario:
                qs = qs.filter(
                    Q(area_principal=area_usuario) | Q(areas_intervinientes=area_usuario)
                ).distinct()
            else:
                return qs.none()
        return qs


# ==============================================================================
# AUTENTICACIÓN
# ==============================================================================
class MunicipalLoginView(LoginView):
    template_name = 'gestion/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('panel_ejecutivo')


# ==============================================================================
# 1. PANEL EJECUTIVO (DASHBOARD)
# ==============================================================================
class PanelEjecutivoView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion/panel_ejecutivo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        # 1. KPIs principales
        kpis = obtener_kpis_dashboard(usuario)
        context['kpis'] = kpis

        # 2. Semáforos por cada Secretaría
        areas = Area.objects.filter(activo=True)
        semaforos_areas = []
        for area in areas:
            info_semaforo = calcular_semaforo_area(area)
            semaforos_areas.append({
                'area': area,
                'info': info_semaforo
            })
        context['semaforos_areas'] = semaforos_areas

        # 3. Tareas prioritarias para Intendencia y próximas a vencer
        hoy = date.today()
        qs_base = Tarea.objects.filter(archivado=False)
        if hasattr(usuario, 'perfil') and usuario.perfil.rol == PerfilUsuario.ROL_SECRETARIA:
            area_usr = usuario.perfil.area
            qs_base = qs_base.filter(Q(area_principal=area_usr) | Q(areas_intervinientes=area_usr))

        context['tareas_prioritarias'] = qs_base.filter(
            prioritario_intendencia=True
        ).exclude(estado=Tarea.ESTADO_FINALIZADA)[:5]

        context['tareas_por_validar'] = qs_base.filter(
            estado=Tarea.ESTADO_PARA_VALIDAR
        )[:5]

        context['tareas_vencidas_recientes'] = qs_base.filter(
            fecha_limite__lt=hoy
        ).exclude(estado=Tarea.ESTADO_FINALIZADA)[:5]

        return context


# ==============================================================================
# 2. GESTIÓN DE TAREAS (LISTADO Y FILTROS)
# ==============================================================================
class TareasListView(LoginRequiredMixin, ScopeTareaQuerysetMixin, ListView):
    model = Tarea
    template_name = 'gestion/tareas_lista.html'
    context_object_name = 'tareas'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('area_principal', 'barrio_principal', 'direccion')

        # Búsqueda por texto
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(titulo__icontains=q) |
                Q(responsable_operativo__icontains=q) |
                Q(descripcion__icontains=q)
            )

        # Filtro de Área
        area_id = self.request.GET.get('area')
        if area_id:
            qs = qs.filter(area_principal_id=area_id)

        # Filtro de Estado
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        # Filtro de Prioridad
        prioridad = self.request.GET.get('prioridad')
        if prioridad:
            qs = qs.filter(prioridad=prioridad)

        # Filtro "Prioritario Intendencia"
        if self.request.GET.get('prioritario') == '1':
            qs = qs.filter(prioritario_intendencia=True)

        # Filtro "Solo Vencidas"
        if self.request.GET.get('vencidas') == '1':
            hoy = date.today()
            qs = qs.filter(fecha_limite__lt=hoy).exclude(estado=Tarea.ESTADO_FINALIZADA)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['areas'] = Area.objects.filter(activo=True)
        context['estados'] = Tarea.ESTADOS_CHOICES
        context['prioridades'] = Tarea.PRIORIDADES_CHOICES
        context['filtros_activos'] = self.request.GET
        return context


# ==============================================================================
# 3. CREACIÓN Y EDICIÓN DE TAREAS
# ==============================================================================
class TareaCreateView(LoginRequiredMixin, CreateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'gestion/tarea_form.html'
    success_url = reverse_lazy('tareas_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import json
        from gestion.models import Direccion, Barrio
        
        # Mapa de direcciones por área
        mapa_dir = {}
        for d in Direccion.objects.filter(activo=True).select_related('area'):
            area_id = str(d.area_id)
            if area_id not in mapa_dir:
                mapa_dir[area_id] = []
            mapa_dir[area_id].append({'id': d.id, 'nombre': d.nombre})
        context['mapa_direcciones_json'] = json.dumps(mapa_dir)

        # Mapa de barrios con viviendas oficiales
        mapa_barrios = {}
        for b in Barrio.objects.all():
            mapa_barrios[str(b.id)] = {
                'id': b.id,
                'nombre': b.nombre,
                'tipo': b.tipo_urbanizacion,
                'viviendas': b.cantidad_viviendas,
                'poblacion': b.poblacion_estimada,
            }
        context['mapa_barrios_json'] = json.dumps(mapa_barrios)
        return context

    def form_valid(self, form):
        # Inyectar usuario actual para auditoría (AuditLog)
        form.instance._current_user = self.request.user
        messages.success(self.request, "Tarea creada exitosamente.")
        return super().form_valid(form)


class TareaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'gestion/tarea_form.html'
    success_url = reverse_lazy('tareas_lista')

    def dispatch(self, request, *args, **kwargs):
        tarea = self.get_object()
        usuario = request.user

        # Regla 1: Restricción de ámbito para Secretarías
        if hasattr(usuario, 'perfil') and usuario.perfil.rol == PerfilUsuario.ROL_SECRETARIA:
            if tarea.area_principal != usuario.perfil.area:
                return HttpResponseForbidden("No tiene permisos para modificar tareas pertenecientes a otra Secretaría.")

            # Regla 2: Si está 'PARA_VALIDAR', queda en modo solo lectura estricto
            if tarea.estado == Tarea.ESTADO_PARA_VALIDAR:
                messages.warning(request, f'La tarea "#{tarea.id}" está en revisión ("Para Validar") y se encuentra en modo solo lectura.')
                return redirect('tarea_seguimiento', pk=tarea.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import json
        from gestion.models import Direccion, Barrio
        
        # Mapa de direcciones por área
        mapa_dir = {}
        for d in Direccion.objects.filter(activo=True).select_related('area'):
            area_id = str(d.area_id)
            if area_id not in mapa_dir:
                mapa_dir[area_id] = []
            mapa_dir[area_id].append({'id': d.id, 'nombre': d.nombre})
        context['mapa_direcciones_json'] = json.dumps(mapa_dir)

        # Mapa de barrios con viviendas oficiales
        mapa_barrios = {}
        for b in Barrio.objects.all():
            mapa_barrios[str(b.id)] = {
                'id': b.id,
                'nombre': b.nombre,
                'tipo': b.tipo_urbanizacion,
                'viviendas': b.cantidad_viviendas,
                'poblacion': b.poblacion_estimada,
            }
        context['mapa_barrios_json'] = json.dumps(mapa_barrios)
        return context

    def form_valid(self, form):
        # Inyectar usuario actual para auditoría (AuditLog)
        form.instance._current_user = self.request.user
        messages.success(self.request, "Tarea actualizada exitosamente.")
        return super().form_valid(form)


class TareaArchivarView(LoginRequiredMixin, View):
    """Soft Delete lógico de tareas."""
    def post(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        usuario = request.user

        # Regla: Las secretarías solo archivan tareas de su área
        if hasattr(usuario, 'perfil') and usuario.perfil.rol == PerfilUsuario.ROL_SECRETARIA:
            if tarea.area_principal != usuario.perfil.area:
                return HttpResponseForbidden("No tiene permisos para archivar tareas de otra secretaría.")

        tarea._current_user = usuario
        tarea.archivado = True
        tarea.save()
        messages.info(request, f'La tarea "#{tarea.id} - {tarea.titulo}" ha sido archivada.')
        return redirect('tareas_lista')


# ==============================================================================
# 4. MODAL DE SEGUIMIENTO Y EVIDENCIAS MULTIMEDIA
# ==============================================================================
class SeguimientoView(LoginRequiredMixin, View):
    """
    Vista unificada de seguimiento y bitácora de novedades con evidencias multimedia.
    Agrupa en un solo paso: comentario, autor/área, archivos adjuntos y requerimientos.
    """
    def get(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        comentarios = tarea.comentarios.select_related('autor').prefetch_related('archivos').all().order_by('-created_at')
        archivos = tarea.archivos.all().order_by('-subido_el')

        # Determinar el firmante sugerido por defecto
        quien_default = ""
        if hasattr(request.user, 'perfil') and request.user.perfil.area:
            quien_default = request.user.perfil.area.nombre
        elif request.user.get_full_name():
            quien_default = request.user.get_full_name()
        else:
            quien_default = request.user.username

        actualizacion_form = ActualizacionSeguimientoForm(initial={'quien_comenta': quien_default})

        # Armado de eventos para la card de Historial
        historial_eventos = []
        # Evento de creación
        if tarea.created_at:
            historial_eventos.append({
                'titulo': 'Tarea creada en el sistema',
                'fecha': tarea.created_at,
                'detalle': f'Responsable operativo: {tarea.responsable_operativo or "A designar"}'
            })
        
        # Eventos por cada actualización/visita registrada
        for c in comentarios:
            resumen = c.mensaje.split('\n')[0][:65] if c.mensaje else "Actualización registrada"
            firmante = c.quien_comenta or c.autor.get_full_name() or c.autor.username
            historial_eventos.append({
                'titulo': f'{resumen} ({firmante})',
                'fecha': c.created_at,
                'detalle': f'{c.archivos.count()} archivo(s) adjunto(s)' if c.archivos.exists() else 'Sin adjuntos'
            })

        # Eventos de auditoría
        for a in tarea.auditorias.all()[:10]:
            usuario_str = a.usuario.get_full_name() or a.usuario.username if a.usuario else "Sistema"
            historial_eventos.append({
                'titulo': f'Acción: {a.get_accion_display()}',
                'fecha': a.timestamp,
                'detalle': f'Por {usuario_str}'
            })

        # Ordenar eventos cronológicamente (más recientes primero)
        historial_eventos.sort(key=lambda x: x['fecha'], reverse=True)

        return render(request, 'gestion/seguimiento_modal.html', {
            'tarea': tarea,
            'comentarios': comentarios,
            'archivos': archivos,
            'actualizacion_form': actualizacion_form,
            'historial_eventos': historial_eventos,
        })

    def post(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        tipo_accion = request.POST.get('tipo_accion')

        if tipo_accion == 'resolver_requerimiento':
            comentario_id = request.POST.get('comentario_id')
            comentario = get_object_or_404(ComentarioActualizacion, id=comentario_id, tarea=tarea)
            comentario.resuelto = True
            comentario.save()
            messages.success(request, "Requerimiento marcado como resuelto.")
            return redirect('tarea_seguimiento', pk=tarea.pk)

        # Acción principal unificada: Guardar comentario + autor + archivos
        form = ActualizacionSeguimientoForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarea = tarea
            comentario.autor = request.user
            
            if not comentario.quien_comenta:
                if hasattr(request.user, 'perfil') and request.user.perfil.area:
                    comentario.quien_comenta = request.user.perfil.area.nombre
                else:
                    comentario.quien_comenta = request.user.get_full_name() or request.user.username
            
            comentario.save()

            # Procesar múltiples archivos adjuntos
            archivos_subidos = request.FILES.getlist('archivos')
            LIMITE_40MB = 40 * 1024 * 1024
            archivos_guardados = 0

            for f in archivos_subidos:
                if f.size > LIMITE_40MB:
                    messages.warning(request, f'El archivo "{f.name}" supera el límite de 40MB y fue omitido.')
                    continue

                archivo_obj = ArchivoAdjunto(
                    tarea=tarea,
                    comentario=comentario,
                    archivo=f,
                    nombre_original=f.name,
                    tamano_bytes=f.size,
                    tipo_mime=f.content_type or ''
                )
                archivo_obj.save()
                archivos_guardados += 1

            if archivos_guardados > 0:
                messages.success(request, f"Actualización publicada exitosamente con {archivos_guardados} evidencia(s) adjunta(s).")
            else:
                messages.success(request, "Actualización publicada exitosamente.")
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())

        return redirect('tarea_seguimiento', pk=tarea.pk)


# ==============================================================================
# 5. VALIDACIÓN JERÁRQUICA (INTENDENCIA / ASESORÍA)
# ==============================================================================
class TareaValidarView(LoginRequiredMixin, View):
    """
    Resuelve tareas en estado PARA_VALIDAR (Aprobar -> Finalizada / Rechazar -> En Ejecución).
    """
    def get(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        form = ValidacionResolucionForm()
        return render(request, 'gestion/tarea_validar_modal.html', {
            'tarea': tarea,
            'form': form
        })

    def post(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        usuario = request.user
        rol = getattr(usuario.perfil, 'rol', None) if hasattr(usuario, 'perfil') else None

        # Verificación estricta de permisos de validación
        if rol == PerfilUsuario.ROL_SECRETARIA:
            return HttpResponseForbidden("Las Secretarías no tienen atribución para validar tareas elevadas.")

        if tarea.prioritario_intendencia and rol != PerfilUsuario.ROL_INTENDENCIA and not usuario.is_superuser:
            return HttpResponseForbidden("Las tareas prioritarias para Intendencia requieren exclusivamente la firma del Intendente.")

        form = ValidacionResolucionForm(request.POST)
        if form.is_valid():
            accion = form.cleaned_data['accion']
            motivo = form.cleaned_data['motivo_rechazo']
            tarea._current_user = usuario

            if accion == ValidacionResolucionForm.ACCION_APROBAR:
                tarea.estado = Tarea.ESTADO_FINALIZADA
                tarea.save()
                messages.success(request, f'Tarea "#{tarea.id}" validada y FINALIZADA con éxito.')
            else:
                tarea.estado = Tarea.ESTADO_EN_EJECUCION
                # Registrar comentario mandatorio explicando el rechazo
                ComentarioActualizacion.objects.create(
                    tarea=tarea,
                    autor=usuario,
                    mensaje=f"[VALIDACIÓN RECHAZADA]: {motivo}",
                    requiere_respuesta=True
                )
                tarea.save()
                messages.warning(request, f'Validación rechazada. La tarea regresó al estado "En Ejecución".')

            return redirect('tareas_lista')

        return render(request, 'gestion/tarea_validar_modal.html', {
            'tarea': tarea,
            'form': form
        })


# ==============================================================================
# 6. ÁREAS MUNICIPALES (DIRECTORIO Y DETALLE)
# ==============================================================================
class AreasListView(LoginRequiredMixin, ListView):
    model = Area
    template_name = 'gestion/areas_lista.html'
    context_object_name = 'areas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        areas_info = []
        for area in context['areas']:
            semaforo = calcular_semaforo_area(area)
            areas_info.append({
                'area': area,
                'semaforo': semaforo
            })
        context['areas_info'] = areas_info
        return context


class AreaDetalleView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion/area_detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area = get_object_or_404(Area, pk=self.kwargs['pk'])
        context['area'] = area
        context['semaforo'] = calcular_semaforo_area(area)

        # Tareas propias e interáreas
        context['tareas_propias'] = Tarea.objects.filter(area_principal=area, archivado=False)
        context['tareas_interareas'] = Tarea.objects.filter(areas_intervinientes=area, archivado=False)
        context['finanzas'] = consolidar_metricas_financieras(context['tareas_propias'])
        context['direcciones'] = area.direcciones.filter(activo=True)
        return context


# ==============================================================================
# 7. MÓDULO DE REPORTES E INFORMES
# ==============================================================================
import csv
import json
from django.http import HttpResponse
from django.db import transaction


class ReportesView(LoginRequiredMixin, TemplateView):
    """
    Matriz comparativa de gestión e indicadores por área y por barrio.
    """
    template_name = 'gestion/reportes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Matriz por Área
        areas = Area.objects.filter(activo=True)
        matriz_areas = []
        for a in areas:
            tareas_area = Tarea.objects.filter(area_principal=a, archivado=False)
            semaforo = calcular_semaforo_area(a)
            finanzas = consolidar_metricas_financieras(tareas_area)
            matriz_areas.append({
                'area': a,
                'semaforo': semaforo,
                'finanzas': finanzas,
            })
        context['matriz_areas'] = matriz_areas

        # 2. Matriz Territorial por Barrio
        context['matriz_barrios'] = consolidar_impacto_barrial()

        # 3. Totales Consolidados
        context['totales_globales'] = consolidar_metricas_financieras()
        return context


class ReporteImprimiblePDFView(LoginRequiredMixin, ScopeTareaQuerysetMixin, ListView):
    """
    Genera el Informe Ejecutivo de Estado de Situación de Malagueño 4.0
    según el diseño oficial estructurado en 5 secciones e imprimible en PDF.
    """
    model = Tarea
    template_name = 'gestion/reportes_pdf.html'
    context_object_name = 'tareas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy = date.today()
        ahora = datetime.now()
        qs = self.get_queryset().filter(archivado=False)

        # 1. Metadatos del encabezado
        context['fecha_hora_generado'] = ahora.strftime("%d/%m/%Y, %H:%M:%S")
        usuario = self.request.user
        if hasattr(usuario, 'perfil') and usuario.perfil.rol == PerfilUsuario.ROL_SECRETARIA and usuario.perfil.area:
            context['alcance_informe'] = f"Gestión de {usuario.perfil.area.nombre}"
        else:
            context['alcance_informe'] = "Gestión municipal general"

        # 2. Contadores superiores
        total_tareas = qs.count()
        total_finalizados = qs.filter(estado=Tarea.ESTADO_FINALIZADA).count()
        total_en_ejecucion = qs.filter(estado=Tarea.ESTADO_EN_EJECUCION).count()
        total_vencidos = qs.filter(fecha_limite__lt=hoy).exclude(estado=Tarea.ESTADO_FINALIZADA).count()
        total_otros = max(0, total_tareas - (total_finalizados + total_en_ejecucion + total_vencidos))

        context['total_tareas'] = total_tareas
        context['total_finalizados'] = total_finalizados
        context['total_en_ejecucion'] = total_en_ejecucion
        context['total_vencidos'] = total_vencidos
        context['total_otros'] = total_otros

        # Porcentajes para barra apilada
        if total_tareas > 0:
            pct_fin = round((total_finalizados / total_tareas) * 100)
            pct_eje = round((total_en_ejecucion / total_tareas) * 100)
            pct_ven = round((total_vencidos / total_tareas) * 100)
            pct_otr = max(0, 100 - (pct_fin + pct_eje + pct_ven))
        else:
            pct_fin = pct_eje = pct_ven = pct_otr = 0

        context['pct_finalizados'] = pct_fin
        context['pct_en_ejecucion'] = pct_eje
        context['pct_vencidos'] = pct_ven
        context['pct_otros'] = pct_otr

        # 3. Situación general (Finanzas consolidadas)
        finanzas = consolidar_metricas_financieras(qs)
        context['finanzas'] = finanzas

        # 4. Semáforo y estado por área (14 Secretarías)
        areas = Area.objects.filter(activo=True)
        matriz_areas = []
        for a in areas:
            t_area = Tarea.objects.filter(
                Q(area_principal=a) | Q(areas_intervinientes=a),
                archivado=False
            ).distinct()
            cnt_total = t_area.count()
            cnt_fin = t_area.filter(estado=Tarea.ESTADO_FINALIZADA).count()
            cnt_ven = t_area.filter(fecha_limite__lt=hoy).exclude(estado=Tarea.ESTADO_FINALIZADA).count()
            cnt_bloq = t_area.filter(estado=Tarea.ESTADO_BLOQUEADA).count()
            cnt_prox = t_area.filter(
                fecha_limite__gte=hoy,
                fecha_limite__lte=hoy + timedelta(days=7)
            ).exclude(estado=Tarea.ESTADO_FINALIZADA).count()

            # Cálculo de avance promedio
            if cnt_total > 0:
                suma_avances = sum(float(t.porcentaje_general or 0) for t in t_area)
                pct_avance = round(suma_avances / cnt_total)
            else:
                pct_avance = 0

            # Determinación semáforo
            if cnt_total == 0:
                sem_class = "gray"
                sem_label = "Sin tareas"
            elif cnt_ven > 0:
                sem_class = "red"
                sem_label = "Rojo · vencidas"
            elif cnt_bloq > 0 or cnt_prox > 0:
                sem_class = "yellow"
                sem_label = "Amarillo · atención"
            else:
                sem_class = "green"
                sem_label = "Al día"

            matriz_areas.append({
                'nombre': a.nombre,
                'sem_class': sem_class,
                'sem_label': sem_label,
                'total': cnt_total,
                'finalizados': cnt_fin,
                'vencidos': cnt_ven,
                'avance': pct_avance,
            })
        context['matriz_areas'] = matriz_areas

        # 5. Cinco temas prioritarios
        # Tareas abiertas ordenadas por prioritario_intendencia DESC, prioridad DESC, fecha_limite ASC
        from django.db.models import Case, When, Value, IntegerField
        cinco_prio = qs.exclude(estado=Tarea.ESTADO_FINALIZADA).annotate(
            orden_prioridad=Case(
                When(prioridad=Tarea.PRIORIDAD_CRITICA, then=Value(4)),
                When(prioridad=Tarea.PRIORIDAD_ALTA, then=Value(3)),
                When(prioridad=Tarea.PRIORIDAD_MEDIA, then=Value(2)),
                When(prioridad=Tarea.PRIORIDAD_BAJA, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-prioritario_intendencia', '-orden_prioridad', 'fecha_limite')[:5]
        context['cinco_prioritarios'] = cinco_prio

        # 6. Cinco próximos a vencer
        # Tareas abiertas con fecha_limite >= hoy ordenadas por cercanía
        cinco_prox = qs.exclude(estado=Tarea.ESTADO_FINALIZADA).filter(
            fecha_limite__gte=hoy
        ).order_by('fecha_limite')[:5]
        context['cinco_proximos_a_vencer'] = cinco_prox

        # 7. Inversión e impacto por barrio
        # Solo barrios con tareas asociadas o sin barrio asignado
        barrios_activos = Barrio.objects.filter(tareas_principales__in=qs).distinct()
        matriz_barrios = []
        for b in barrios_activos:
            t_barrio = qs.filter(barrio_principal=b)
            if t_barrio.exists():
                mca_b = sum((t.monto_contractual_actualizado or Decimal('0.00')) for t in t_barrio)
                pag_b = sum((t.monto_pagado or Decimal('0.00')) for t in t_barrio)
                viv_dir = sum((t.viviendas_directas or 0) for t in t_barrio)
                viv_ind = sum((t.viviendas_indirectas or 0) for t in t_barrio)
                per_dir = sum((t.personas_directas or 0) for t in t_barrio)
                per_ind = sum((t.personas_indirectas or 0) for t in t_barrio)

                matriz_barrios.append({
                    'nombre': b.nombre,
                    'tareas_count': t_barrio.count(),
                    'mca': mca_b,
                    'pagado': pag_b,
                    'viv_directas': viv_dir,
                    'viv_indirectas': viv_ind,
                    'per_directas': per_dir,
                    'per_indirectas': per_ind,
                })

        # Tareas sin barrio asignado si existieran
        t_sin_barrio = qs.filter(barrio_principal__isnull=True)
        if t_sin_barrio.exists():
            mca_sb = sum((t.monto_contractual_actualizado or Decimal('0.00')) for t in t_sin_barrio)
            pag_sb = sum((t.monto_pagado or Decimal('0.00')) for t in t_sin_barrio)
            matriz_barrios.append({
                'nombre': "Sin barrio asignado",
                'tareas_count': t_sin_barrio.count(),
                'mca': mca_sb,
                'pagado': pag_sb,
                'viv_directas': sum((t.viviendas_directas or 0) for t in t_sin_barrio),
                'viv_indirectas': sum((t.viviendas_indirectas or 0) for t in t_sin_barrio),
                'per_directas': sum((t.personas_directas or 0) for t in t_sin_barrio),
                'per_indirectas': sum((t.personas_indirectas or 0) for t in t_sin_barrio),
            })

        context['matriz_barrios_impacto'] = matriz_barrios
        return context


class ExportarCSVView(LoginRequiredMixin, ScopeTareaQuerysetMixin, View):
    """
    Exporta el listado de tareas a formato CSV con encoding compatible con Excel (UTF-8-SIG).
    """
    def get(self, request):
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="tablero_malagueno_{date.today():%Y%m%d}.csv"'

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'ID', 'Titulo', 'Area Principal', 'Direccion', 'Responsable Operativo',
            'Estado', 'Prioridad', 'Prioritario Intendencia', 'Fecha Limite',
            '% General', '% Fisico', '% Financiero',
            'Presupuesto Oficial', 'Adjudicado', 'Redeterminaciones', 'Ampliaciones',
            'MCA (Monto Actualizado)', 'Devengado', 'Pagado', 'Devengado Pendiente',
            'Barrio Principal', 'Beneficiarios Estimados'
        ])

        for t in qs:
            writer.writerow([
                t.id,
                t.titulo,
                t.area_principal.codigo,
                t.direccion.nombre if t.direccion else '',
                t.responsable_operativo or '',
                t.get_estado_display(),
                t.get_prioridad_display(),
                'SI' if t.prioritario_intendencia else 'NO',
                t.fecha_limite.strftime('%d/%m/%Y') if t.fecha_limite else '',
                f"{t.porcentaje_general}%",
                f"{t.porcentaje_fisico}%",
                f"{t.porcentaje_financiero}%",
                f"{t.presupuesto_oficial:.2f}",
                f"{t.monto_adjudicado:.2f}",
                f"{t.redeterminaciones:.2f}",
                f"{t.ampliaciones:.2f}",
                f"{t.monto_contractual_actualizado:.2f}",
                f"{t.monto_devengado:.2f}",
                f"{t.monto_pagado:.2f}",
                f"{t.devengado_pendiente_pago:.2f}",
                t.barrio_principal.nombre if t.barrio_principal else '',
                t.beneficiarios_calculados
            ])

        return response


class ExportarJSONView(LoginRequiredMixin, ScopeTareaQuerysetMixin, View):
    """
    Exporta las tareas a JSON según el alcance del usuario.
    """
    def get(self, request):
        qs = self.get_queryset()
        data = []
        for t in qs:
            data.append({
                'id': t.id,
                'titulo': t.titulo,
                'area': t.area_principal.codigo,
                'estado': t.estado,
                'prioridad': t.prioridad,
                'prioritario_intendencia': t.prioritario_intendencia,
                'fecha_limite': str(t.fecha_limite) if t.fecha_limite else None,
                'porcentaje_general': float(t.porcentaje_general),
                'porcentaje_fisico': float(t.porcentaje_fisico),
                'porcentaje_financiero': float(t.porcentaje_financiero),
                'monto_contractual_actualizado': float(t.monto_contractual_actualizado),
                'monto_devengado': float(t.monto_devengado),
                'monto_pagado': float(t.monto_pagado),
                'barrio_principal': t.barrio_principal.nombre if t.barrio_principal else None,
                'beneficiarios': t.beneficiarios_calculados,
            })
        response = HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="tareas_malagueno_{date.today():%Y%m%d}.json"'
        return response


class ExportarBarriosCSVView(LoginRequiredMixin, View):
    """
    Exporta la matriz de inversión y beneficiarios por barrio a formato CSV (UTF-8-SIG para Excel).
    """
    def get(self, request):
        import csv
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="inversion_barrios_malagueno_{date.today():%Y%m%d}.csv"'

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Barrio', 'Tipo Urbanizacion', 'Viviendas Oficiales (Censo)', 'Poblacion Estimada',
            'Tareas Principales', 'Tareas Adicionales', 'Total Intervenciones',
            'Monto Contractual (MCA $)', 'Monto Pagado ($)',
            'Viviendas Directas', 'Viviendas Indirectas',
            'Personas Directas', 'Personas Indirectas', 'Total Beneficiarios Estimados'
        ])

        barrios = Barrio.objects.all().order_by('nombre')
        for b in barrios:
            tareas_p = Tarea.objects.filter(barrio_principal=b, archivado=False)
            tareas_a = Tarea.objects.filter(barrios_adicionales=b, archivado=False)

            mca = sum((t.monto_contractual_actualizado or Decimal('0.00')) for t in tareas_p)
            pagado = sum((t.monto_pagado or Decimal('0.00')) for t in tareas_p)
            v_dir = sum((t.viviendas_directas or 0) for t in tareas_p)
            v_ind = sum((t.viviendas_indirectas or 0) for t in tareas_p)
            p_dir = sum((t.personas_directas or 0) for t in tareas_p)
            p_ind = sum((t.personas_indirectas or 0) for t in tareas_p)
            total_ben = sum(t.beneficiarios_calculados for t in tareas_p)

            writer.writerow([
                b.nombre,
                b.get_tipo_urbanizacion_display(),
                b.cantidad_viviendas,
                b.poblacion_estimada,
                tareas_p.count(),
                tareas_a.count(),
                tareas_p.count() + tareas_a.count(),
                f"{mca:.2f}",
                f"{pagado:.2f}",
                v_dir,
                v_ind,
                p_dir,
                p_ind,
                total_ben
            ])

        return response


# ==============================================================================
# 8. MÓDULO DE DATOS Y RESPALDO (EXCLUSIVO INTENDENCIA / ASESORÍA)
# ==============================================================================
class DatosRespaldoView(LoginRequiredMixin, View):
    """
    Permite descargar un respaldo integral de base de datos o restaurarlo desde JSON.
    Estrictamente restringido a Intendencia y Asesoría Técnica.
    """
    def dispatch(self, request, *args, **kwargs):
        rol = getattr(request.user.perfil, 'rol', None) if hasattr(request.user, 'perfil') else None
        if rol not in (PerfilUsuario.ROL_INTENDENCIA, PerfilUsuario.ROL_ASESORIA) and not request.user.is_superuser:
            return HttpResponseForbidden("La gestión de respaldos está reservada para Intendencia y Asesoría Técnica.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'gestion/datos_respaldo.html', {
            'total_areas': Area.objects.count(),
            'total_barrios': Barrio.objects.count(),
            'total_tareas': Tarea.objects.count(),
            'total_auditorias': AuditLog.objects.count(),
        })

    def post(self, request):
        accion = request.POST.get('accion')

        # DESCARGAR RESPALDO COMPLETO
        if accion == 'exportar_completo':
            dump_data = {
                'fecha_respaldo': str(date.today()),
                'areas': list(Area.objects.values('id', 'codigo', 'nombre', 'responsable_nombre', 'color_identificador', 'activo')),
                'barrios': list(Barrio.objects.values('id', 'nombre', 'tipo_urbanizacion', 'cantidad_viviendas', 'poblacion_estimada')),
                'direcciones': list(Direccion.objects.values('id', 'area_id', 'nombre', 'responsable_nombre', 'activo')),
                'tareas': list(Tarea.objects.values(
                    'id', 'titulo', 'descripcion', 'area_principal_id', 'direccion_id',
                    'responsable_operativo', 'tipo_intervencion', 'prioridad', 'prioritario_intendencia',
                    'estado', 'fecha_limite', 'porcentaje_general', 'porcentaje_fisico',
                    'porcentaje_financiero', 'presupuesto_oficial', 'monto_adjudicado',
                    'redeterminaciones', 'ampliaciones', 'monto_devengado', 'monto_pagado',
                    'pagos_en_tramite', 'barrio_principal_id', 'modalidad_beneficiarios',
                    'viviendas_directas', 'viviendas_indirectas', 'personas_directas', 'personas_indirectas',
                    'cantidad_beneficiarios_input', 'link_google_maps', 'observaciones', 'archivado'
                ))
            }
            # Convertir Decimals y Dates a string
            contenido_json = json.dumps(dump_data, default=str, indent=2, ensure_ascii=False)
            response = HttpResponse(contenido_json, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="respaldo_malagueno_{date.today():%Y%m%d_%H%M}.json"'
            return response

        # IMPORTAR RESPALDO JSON
        elif accion == 'importar_respaldo':
            archivo = request.FILES.get('archivo_respaldo')
            if not archivo:
                messages.error(request, "Debe seleccionar un archivo JSON válido de respaldo.")
                return redirect('datos_respaldo')

            try:
                data = json.load(archivo)
                with transaction.atomic():
                    # 1. Áreas
                    for a_data in data.get('areas', []):
                        Area.objects.update_or_create(
                            codigo=a_data['codigo'],
                            defaults={
                                'nombre': a_data['nombre'],
                                'responsable_nombre': a_data.get('responsable_nombre', ''),
                                'color_identificador': a_data.get('color_identificador', '#338c33'),
                                'activo': a_data.get('activo', True),
                            }
                        )

                    # 2. Barrios
                    for b_data in data.get('barrios', []):
                        Barrio.objects.update_or_create(
                            nombre=b_data['nombre'],
                            defaults={
                                'tipo_urbanizacion': b_data.get('tipo_urbanizacion', 'ABIERTO'),
                                'cantidad_viviendas': b_data.get('cantidad_viviendas', 0),
                                'poblacion_estimada': b_data.get('poblacion_estimada', 0),
                            }
                        )

                    messages.success(request, "Respaldo importado y procesado exitosamente sin inconsistencias.")
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo de respaldo: {str(e)}")

            return redirect('datos_respaldo')

        return redirect('datos_respaldo')


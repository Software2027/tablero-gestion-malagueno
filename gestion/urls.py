from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    MunicipalLoginView, PanelEjecutivoView, TareasListView,
    TareaCreateView, TareaUpdateView, TareaArchivarView,
    SeguimientoView, TareaValidarView, AreasListView, AreaDetalleView,
    ReportesView, ReporteImprimiblePDFView, ExportarCSVView,
    ExportarBarriosCSVView, ExportarJSONView, DatosRespaldoView
)

urlpatterns = [
    # Autenticación
    path('login/', MunicipalLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Panel Ejecutivo (Dashboard)
    path('', PanelEjecutivoView.as_view(), name='panel_ejecutivo'),

    # Gestión de Tareas
    path('tareas/', TareasListView.as_view(), name='tareas_lista'),
    path('tareas/nueva/', TareaCreateView.as_view(), name='tarea_crear'),
    path('tareas/<int:pk>/editar/', TareaUpdateView.as_view(), name='tarea_editar'),
    path('tareas/<int:pk>/archivar/', TareaArchivarView.as_view(), name='tarea_archivar'),
    path('tareas/<int:pk>/seguimiento/', SeguimientoView.as_view(), name='tarea_seguimiento'),
    path('tareas/<int:pk>/validar/', TareaValidarView.as_view(), name='tarea_validar'),

    # Áreas Municipales
    path('areas/', AreasListView.as_view(), name='areas_lista'),
    path('areas/<int:pk>/', AreaDetalleView.as_view(), name='area_detalle'),

    # Reportes e Informes
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('reportes/imprimible/', ReporteImprimiblePDFView.as_view(), name='reportes_imprimible'),
    path('reportes/exportar/csv/', ExportarCSVView.as_view(), name='reportes_exportar_csv'),
    path('reportes/exportar/barrios/csv/', ExportarBarriosCSVView.as_view(), name='reportes_exportar_barrios_csv'),
    path('reportes/exportar/json/', ExportarJSONView.as_view(), name='reportes_exportar_json'),

    # Datos y Respaldo (Intendencia / Asesoría)
    path('respaldo/', DatosRespaldoView.as_view(), name='datos_respaldo'),
]

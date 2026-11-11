from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import (
    Area, Direccion, PerfilUsuario, Barrio, Tarea,
    ComentarioActualizacion, ArchivoAdjunto, AuditLog
)


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name = "Perfil y Rol Municipal"
    verbose_name_plural = "Perfil y Rol Municipal"
    fk_name = 'user'
    fields = ('rol', 'area', 'direccion', 'telefono')

    def get_extra(self, request, obj=None):
        if obj:
            try:
                if hasattr(obj, 'perfil') and obj.perfil:
                    return 0
            except Exception:
                return 1
            return 1
        return 1


# Desregistrar y volver a registrar User con el Inline de Perfil y Rol
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'get_nombre_completo', 'email', 'get_rol_badge', 'get_area', 'is_staff', 'is_active')
    list_filter = ('perfil__rol', 'perfil__area', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username
    get_nombre_completo.short_description = "Nombre y Apellido"

    def get_rol_badge(self, obj):
        try:
            if hasattr(obj, 'perfil') and obj.perfil:
                colores = {
                    'INTENDENCIA': '#0C3613',
                    'ASESORIA': '#246da8',
                    'SECRETARIA': '#338c33',
                }
                color = colores.get(obj.perfil.rol, '#64748b')
                return format_html(
                    '<span style="background:{}; color:#fff; padding:3px 9px; border-radius:12px; font-weight:700; font-size:11px; text-transform:uppercase;">{}</span>',
                    color,
                    obj.perfil.get_rol_display()
                )
        except Exception:
            pass
        return format_html('<span style="color:#94a3b8; font-style:italic;">Sin perfil</span>')
    get_rol_badge.short_description = "Rol Municipal"

    def get_area(self, obj):
        try:
            if hasattr(obj, 'perfil') and obj.perfil and obj.perfil.area:
                return obj.perfil.area.nombre
        except Exception:
            pass
        return "—"
    get_area.short_description = "Área Asignada"


class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 1
    fields = ('nombre', 'responsable_nombre', 'activo')


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'responsable_nombre', 'color_badge', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'codigo', 'responsable_nombre')
    inlines = [DireccionInline]

    def color_badge(self, obj):
        return format_html(
            '<span style="display:inline-block; width:18px; height:18px; background-color:{}; border-radius:3px; vertical-align:middle; margin-right:6px; border:1px solid #ccc;"></span>{}',
            obj.color_identificador,
            obj.color_identificador
        )
    color_badge.short_description = "Color Identificador"


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'responsable_nombre', 'activo')
    list_filter = ('area', 'activo')
    search_fields = ('nombre', 'responsable_nombre', 'area__nombre')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol_badge', 'rol', 'area', 'direccion', 'telefono')
    list_editable = ('rol', 'area')
    list_filter = ('rol', 'area')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'telefono')
    raw_id_fields = ('user',)

    def rol_badge(self, obj):
        colores = {
            'INTENDENCIA': '#0C3613',
            'ASESORIA': '#246da8',
            'SECRETARIA': '#338c33',
        }
        color = colores.get(obj.rol, '#64748b')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 9px; border-radius:12px; font-weight:700; font-size:11px; text-transform:uppercase;">{}</span>',
            color,
            obj.get_rol_display()
        )
    rol_badge.short_description = "Estado Rol"


@admin.register(Barrio)
class BarrioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_viviendas', 'poblacion_estimada')
    search_fields = ('nombre',)


class ComentarioInline(admin.StackedInline):
    model = ComentarioActualizacion
    extra = 0
    readonly_fields = ('autor', 'created_at')


class ArchivoInline(admin.TabularInline):
    model = ArchivoAdjunto
    extra = 0
    readonly_fields = ('subido_el', 'tamano_bytes')


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'titulo', 'area_principal', 'estado_badge',
        'prioridad_badge', 'prioritario_intendencia_icon',
        'fecha_limite', 'avance_general_progreso', 'archivado'
    )
    list_filter = (
        'estado', 'prioridad', 'prioritario_intendencia',
        'area_principal', 'archivado', 'barrio_principal'
    )
    search_fields = ('titulo', 'descripcion', 'responsable_operativo')
    inlines = [ComentarioInline, ArchivoInline]
    filter_horizontal = ('areas_intervinientes', 'barrios_adicionales')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('1. Identificación y Responsables', {
            'fields': (
                'titulo', 'descripcion', 'area_principal', 'direccion',
                'responsable_operativo', 'tipo_intervencion', 'prioridad',
                'prioritario_intendencia', 'areas_intervinientes'
            )
        }),
        ('2. Planificación y Avances', {
            'fields': (
                'estado', 'fecha_limite', 'porcentaje_general',
                'porcentaje_fisico', 'porcentaje_financiero'
            )
        }),
        ('3. Matriz Económica y Presupuesto', {
            'fields': (
                'presupuesto_oficial', 'monto_adjudicado', 'redeterminaciones',
                'ampliaciones', 'monto_devengado', 'monto_pagado', 'pagos_en_tramite'
            )
        }),
        ('4. Territorialidad y Beneficiarios', {
            'fields': (
                'barrio_principal', 'barrios_adicionales',
                'modalidad_beneficiarios', 'cantidad_beneficiarios_input',
                'link_google_maps'
            )
        }),
        ('5. Observaciones y Control', {
            'fields': ('observaciones', 'archivado', 'created_at', 'updated_at')
        }),
    )

    def estado_badge(self, obj):
        colores = {
            'PENDIENTE': '#64748b',
            'EN_EJECUCION': '#0284c7',
            'BLOQUEADA': '#d97706',
            'PARA_VALIDAR': '#7c3aed',
            'FINALIZADA': '#338c33',
        }
        color = colores.get(obj.estado, '#64748b')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 8px; border-radius:4px; font-weight:600; font-size:11px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"

    def prioridad_badge(self, obj):
        colores = {
            'BAJA': '#94a3b8',
            'MEDIA': '#3b82f6',
            'ALTA': '#f97316',
            'CRITICA': '#ef4444',
        }
        color = colores.get(obj.prioridad, '#94a3b8')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_badge.short_description = "Prioridad"

    def prioritario_intendencia_icon(self, obj):
        if obj.prioritario_intendencia:
            return format_html('<span style="color:#338c33; font-size:14px; font-weight:bold;">★ SÍ</span>')
        return format_html('<span style="color:#94a3b8;">—</span>')
    prioritario_intendencia_icon.short_description = "Intendencia"

    def avance_general_progreso(self, obj):
        return format_html(
            '<div style="width:100px; background:#e2e8f0; border-radius:4px; overflow:hidden;">'
            '<div style="width:{}%; background:#338c33; height:14px; text-align:center; color:#fff; font-size:9px; line-height:14px;">{}%</div>'
            '</div>',
            float(obj.porcentaje_general),
            float(obj.porcentaje_general)
        )
    avance_general_progreso.short_description = "% Avance"


@admin.register(ComentarioActualizacion)
class ComentarioActualizacionAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'autor', 'requiere_respuesta', 'resuelto', 'created_at')
    list_filter = ('requiere_respuesta', 'resuelto', 'created_at')
    search_fields = ('mensaje', 'tarea__titulo', 'autor__username')


@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('nombre_original', 'tarea', 'tipo_mime', 'tamano_mb_display', 'subido_el')
    list_filter = ('subido_el',)
    search_fields = ('nombre_original', 'tarea__titulo')

    def tamano_mb_display(self, obj):
        return f"{obj.tamano_megabytes:.2f} MB"
    tamano_mb_display.short_description = "Tamaño"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'usuario', 'accion', 'tarea', 'campo_modificado')
    list_filter = ('accion', 'timestamp')
    search_fields = ('tarea__titulo', 'usuario__username', 'campo_modificado', 'valor_anterior', 'valor_nuevo')
    readonly_fields = ('timestamp', 'usuario', 'accion', 'tarea', 'campo_modificado', 'valor_anterior', 'valor_nuevo')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

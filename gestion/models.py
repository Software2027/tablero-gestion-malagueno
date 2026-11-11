from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from decimal import Decimal


class Area(models.Model):
    """
    Representa una Secretaría u Órgano de gobierno municipal.
    """
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre del Área")
    codigo = models.CharField(max_length=30, unique=True, verbose_name="Código Identificador")
    responsable_nombre = models.CharField(max_length=150, verbose_name="Titular / Secretario")
    color_identificador = models.CharField(
        max_length=7,
        default="#338c33",
        verbose_name="Color Identificador (Hex)",
        help_text="Color corporativo en formato hexadecimal (ej. #338c33)"
    )
    activo = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Área / Secretaría"
        verbose_name_plural = "Áreas y Secretarías"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Direccion(models.Model):
    """
    Representa una Dirección o sub-área dependiente de una Secretaría.
    """
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="direcciones",
        verbose_name="Área / Secretaría Superior"
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la Dirección")
    responsable_nombre = models.CharField(max_length=150, blank=True, verbose_name="Director / Responsable")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden Jerárquico")
    activo = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        ordering = ['area', 'orden', 'id']

    def __str__(self):
        return f"{self.nombre} - {self.area.codigo}"


class PerfilUsuario(models.Model):
    """
    Extensión del modelo auth.User para gestionar roles y dependencias organizativas.
    """
    ROL_INTENDENCIA = 'INTENDENCIA'
    ROL_ASESORIA = 'ASESORIA'
    ROL_SECRETARIA = 'SECRETARIA'

    ROLES_CHOICES = [
        (ROL_INTENDENCIA, 'Intendencia'),
        (ROL_ASESORIA, 'Asesoría Técnica'),
        (ROL_SECRETARIA, 'Secretaría'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario del Sistema"
    )
    rol = models.CharField(
        max_length=20,
        choices=ROLES_CHOICES,
        default=ROL_SECRETARIA,
        verbose_name="Rol Operativo"
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
        verbose_name="Área Asignada"
    )
    direccion = models.ForeignKey(
        Direccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
        verbose_name="Dirección Asignada"
    )
    telefono = models.CharField(max_length=50, blank=True, verbose_name="Teléfono de Contacto")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        area_str = self.area.codigo if self.area else 'Global'
        return f"{self.user.get_full_name() or self.user.username} [{self.get_rol_display()} - {area_str}]"


class Barrio(models.Model):
    """
    Barrio o paraje catastral del ejido municipal de Malagueño.
    """
    TIPO_ABIERTO = 'ABIERTO'
    TIPO_CERRADO = 'CERRADO'
    TIPO_CHOICES = [
        (TIPO_ABIERTO, 'Abierto'),
        (TIPO_CERRADO, 'Cerrado'),
    ]

    nombre = models.CharField(max_length=120, unique=True, verbose_name="Nombre del Barrio")
    tipo_urbanizacion = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=TIPO_ABIERTO,
        verbose_name="Tipo de Urbanización"
    )
    cantidad_viviendas = models.PositiveIntegerField(default=0, verbose_name="Cantidad de Viviendas Estimadas")
    poblacion_estimada = models.PositiveIntegerField(default=0, verbose_name="Población Estimada")
    poligono_geografico = models.JSONField(null=True, blank=True, verbose_name="Datos GeoJSON / Polígono")

    class Meta:
        verbose_name = "Barrio"
        verbose_name_plural = "Barrios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_urbanizacion_display()})"


class Tarea(models.Model):
    """
    Entidad nuclear del Tablero de Gestión.
    Centraliza el seguimiento general, físico, financiero y territorial de las intervenciones.
    """
    # Estados de flujo de trabajo
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_EN_EJECUCION = 'EN_EJECUCION'
    ESTADO_BLOQUEADA = 'BLOQUEADA'
    ESTADO_PARA_VALIDAR = 'PARA_VALIDAR'
    ESTADO_FINALIZADA = 'FINALIZADA'

    ESTADOS_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_EN_EJECUCION, 'En Ejecución'),
        (ESTADO_BLOQUEADA, 'Bloqueada'),
        (ESTADO_PARA_VALIDAR, 'Para Validar'),
        (ESTADO_FINALIZADA, 'Finalizada'),
    ]

    # Prioridades
    PRIORIDAD_BAJA = 'BAJA'
    PRIORIDAD_MEDIA = 'MEDIA'
    PRIORIDAD_ALTA = 'ALTA'
    PRIORIDAD_CRITICA = 'CRITICA'

    PRIORIDADES_CHOICES = [
        (PRIORIDAD_BAJA, 'Baja'),
        (PRIORIDAD_MEDIA, 'Media'),
        (PRIORIDAD_ALTA, 'Alta'),
        (PRIORIDAD_CRITICA, 'Crítica'),
    ]

    # Modalidad de beneficiarios
    MODALIDAD_VIVIENDAS = 'VIVIENDAS'
    MODALIDAD_PERSONAS = 'PERSONAS'
    MODALIDAD_SIN_DATO = 'SIN_DATO'

    MODALIDADES_BENEFICIARIOS = [
        (MODALIDAD_VIVIENDAS, 'Por viviendas alcanzadas (estimación de habitantes × 3,5)'),
        (MODALIDAD_PERSONAS, 'Por personas individuales (capacitaciones, salud, programas sociales)'),
        (MODALIDAD_SIN_DATO, 'Sin beneficiarios cuantificados por el momento'),
    ]

    # 1. Datos Generales
    titulo = models.CharField(max_length=255, verbose_name="Título de la Tarea / Proyecto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción Detallada")
    area_principal = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="tareas_principales",
        verbose_name="Secretaría / Área Principal"
    )
    direccion = models.ForeignKey(
        Direccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas",
        verbose_name="Dirección Ejecutora"
    )
    responsable_operativo = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Responsable Operativo",
        help_text="Director, técnico o coordinador a cargo (sin usuario propio en esta etapa)"
    )
    tipo_intervencion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo de Intervención",
        help_text="Ej: Infraestructura, Bacheo, Alumbrado, Gestión Social, Administrativo"
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDADES_CHOICES,
        default=PRIORIDAD_MEDIA,
        verbose_name="Nivel de Prioridad"
    )
    prioritario_intendencia = models.BooleanField(
        default=False,
        verbose_name="Prioritario para Intendencia",
        help_text="Marcador exclusivo de Intendencia / Asesoría Técnica"
    )

    # 2. Articulación Interáreas
    areas_intervinientes = models.ManyToManyField(
        Area,
        blank=True,
        related_name="tareas_intervinientes",
        verbose_name="Áreas Intervinientes / Secundarias"
    )

    # 3. Planificación y Avances
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name="Estado de Gestión"
    )
    fecha_limite = models.DateField(null=True, blank=True, verbose_name="Fecha Límite Prevista")
    porcentaje_general = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="% Avance General"
    )
    porcentaje_fisico = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="% Avance Físico"
    )
    porcentaje_financiero = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="% Avance Financiero"
    )

    # 4. Gestión Presupuestaria y Financiera
    presupuesto_oficial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="Presupuesto Oficial ($)"
    )
    monto_adjudicado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="Monto Adjudicado ($)"
    )
    redeterminaciones = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="Redeterminaciones ($)"
    )
    ampliaciones = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="Ampliaciones ($)"
    )
    monto_devengado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="Monto Devengado ($)"
    )
    monto_pagado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="Monto Pagado ($)"
    )
    pagos_en_tramite = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        verbose_name="Pagos en Trámite ($)"
    )

    # 5. Territorio y Beneficiarios
    barrio_principal = models.ForeignKey(
        Barrio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas_principales",
        verbose_name="Barrio Principal (Absorbe 100% de la inversión)"
    )
    barrios_adicionales = models.ManyToManyField(
        Barrio,
        blank=True,
        related_name="tareas_adicionales",
        verbose_name="Barrios Adicionales Alcanzados (Sin duplicación monetaria)"
    )
    modalidad_beneficiarios = models.CharField(
        max_length=20,
        choices=MODALIDADES_BENEFICIARIOS,
        default=MODALIDAD_SIN_DATO,
        verbose_name="Modalidad de Cómputo de Beneficiarios"
    )
    viviendas_directas = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Viviendas beneficiadas directamente"
    )
    viviendas_indirectas = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Viviendas beneficiadas indirectamente"
    )
    personas_directas = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Personas beneficiadas directamente"
    )
    personas_indirectas = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Personas beneficiadas indirectamente"
    )
    cantidad_beneficiarios_input = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Cantidad Ingresada (Total)",
        help_text="Total unificado de beneficiarios directos e indirectos"
    )
    link_google_maps = models.URLField(max_length=500, blank=True, verbose_name="Ubicación en Google Maps")

    # 6. Observaciones y Control
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones / Justificación",
        help_text="Obligatorio documentar el motivo si el estado es BLOQUEADA"
    )
    archivado = models.BooleanField(
        default=False,
        verbose_name="Archivado (Soft Delete)",
        help_text="Las tareas archivadas no se eliminan físicamente de la base de datos"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Tarea de Gestión"
        verbose_name_plural = "Tareas de Gestión"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} [{self.area_principal.codigo}]"

    # ==========================================
    # CÁLCULOS FINANCIEROS Y FÓRMULAS DE NEGOCIO
    # ==========================================
    @property
    def monto_contractual_actualizado(self) -> Decimal:
        """MCA = Adjudicado + Redeterminaciones + Ampliaciones"""
        adjudicado = self.monto_adjudicado or Decimal('0.00')
        redet = self.redeterminaciones or Decimal('0.00')
        ampl = self.ampliaciones or Decimal('0.00')
        return adjudicado + redet + ampl

    @property
    def devengado_pendiente_pago(self) -> Decimal:
        """DPP = max(0, Devengado - Pagado)"""
        devengado = self.monto_devengado or Decimal('0.00')
        pagado = self.monto_pagado or Decimal('0.00')
        pendiente = devengado - pagado
        return pendiente if pendiente > Decimal('0.00') else Decimal('0.00')

    def calcular_avance_financiero_real(self) -> Decimal:
        """(Pagado / MCA) * 100"""
        mca = self.monto_contractual_actualizado
        if mca > Decimal('0.00'):
            pagado = self.monto_pagado or Decimal('0.00')
            calc = (pagado / mca) * Decimal('100.00')
            return round(min(calc, Decimal('100.00')), 2)
        return Decimal('0.00')

    @property
    def habitantes_directos(self) -> int:
        if self.modalidad_beneficiarios == self.MODALIDAD_VIVIENDAS:
            viv = self.viviendas_directas or (self.cantidad_beneficiarios_input if not self.viviendas_indirectas else 0)
            return int(round(viv * 3.5))
        elif self.modalidad_beneficiarios == self.MODALIDAD_PERSONAS:
            pers = self.personas_directas or (self.cantidad_beneficiarios_input if not self.personas_indirectas else 0)
            return pers
        return 0

    @property
    def habitantes_indirectos(self) -> int:
        if self.modalidad_beneficiarios == self.MODALIDAD_VIVIENDAS:
            return int(round(self.viviendas_indirectas * 3.5))
        elif self.modalidad_beneficiarios == self.MODALIDAD_PERSONAS:
            return self.personas_indirectas
        return 0

    @property
    def beneficiarios_calculados(self) -> int:
        """
        Cálculo de habitantes totales alcanzados (directos + indirectos)
        """
        return self.habitantes_directos + self.habitantes_indirectos

    @property
    def esta_vencida(self) -> bool:
        """
        Una tarea está vencida si su fecha límite < hoy, no está finalizada y no está archivada.
        """
        if self.fecha_limite and self.estado != self.ESTADO_FINALIZADA and not self.archivado:
            return self.fecha_limite < date.today()
        return False

    @property
    def dias_para_vencer(self) -> int | None:
        """Días restantes para la fecha límite (negativo si está vencida)."""
        if self.fecha_limite:
            delta = self.fecha_limite - date.today()
            return delta.days
        return None

    # ==========================================
    # VALIDACIONES DE NEGOCIO
    # ==========================================
    def clean(self):
        super().clean()

        # 1. Justificación obligatoria para estado BLOQUEADA
        if self.estado == self.ESTADO_BLOQUEADA and not self.observaciones.strip():
            raise ValidationError({
                'observaciones': 'Es obligatorio documentar la justificación o impedimento en el campo "Observaciones" cuando la tarea está Bloqueada.'
            })

        # 2. Restricción financiera: Pagado <= Devengado
        pagado = self.monto_pagado or Decimal('0.00')
        devengado = self.monto_devengado or Decimal('0.00')
        mca = self.monto_contractual_actualizado

        if pagado > devengado:
            raise ValidationError({
                'monto_pagado': f'El Monto Pagado (${pagado:,.2f}) no puede superar al Monto Devengado (${devengado:,.2f}).'
            })

        # 3. Restricción financiera: Devengado <= MCA (si MCA > 0)
        if mca > Decimal('0.00') and devengado > mca:
            raise ValidationError({
                'monto_devengado': f'El Monto Devengado (${devengado:,.2f}) no puede superar al Monto Contractual Actualizado (${mca:,.2f}).'
            })

    def save(self, *args, **kwargs):
        # Actualizar automáticamente el porcentaje financiero antes de persistir
        if self.monto_contractual_actualizado > Decimal('0.00'):
            self.porcentaje_financiero = self.calcular_avance_financiero_real()

        # Sincronizar cantidad_beneficiarios_input para compatibilidad hacia atrás
        if self.modalidad_beneficiarios == self.MODALIDAD_VIVIENDAS:
            if not self.viviendas_directas and not self.viviendas_indirectas and self.cantidad_beneficiarios_input:
                self.viviendas_directas = self.cantidad_beneficiarios_input
            else:
                self.cantidad_beneficiarios_input = (self.viviendas_directas or 0) + (self.viviendas_indirectas or 0)
        elif self.modalidad_beneficiarios == self.MODALIDAD_PERSONAS:
            if not self.personas_directas and not self.personas_indirectas and self.cantidad_beneficiarios_input:
                self.personas_directas = self.cantidad_beneficiarios_input
            else:
                self.cantidad_beneficiarios_input = (self.personas_directas or 0) + (self.personas_indirectas or 0)
        else:
            self.cantidad_beneficiarios_input = 0

        self.clean()
        super().save(*args, **kwargs)


def ruta_archivo_seguimiento(instance, filename):
    """
    Genera la ruta de almacenamiento estructurada y normalizada:
    media/seguimiento/<nombre_tarea_normalizado>/%Y/%m/<archivo_normalizado.ext>
    Reglas de sanitización:
    - Todo a minúsculas.
    - Espacios reemplazados por guiones bajos '_'.
    - Eliminación de acentos, tildes y caracteres especiales.
    """
    import os
    import re
    import unicodedata
    from datetime import datetime

    # 1. Normalizar nombre de la tarea para la subcarpeta
    if instance.tarea and instance.tarea.titulo:
        titulo_tarea = instance.tarea.titulo
    else:
        titulo_tarea = f"tarea_{instance.tarea_id or 'general'}"

    titulo_norm = unicodedata.normalize('NFKD', str(titulo_tarea)).encode('ascii', 'ignore').decode('utf-8').lower()
    titulo_norm = re.sub(r'\s+', '_', titulo_norm)
    titulo_norm = re.sub(r'[^a-z0-9_-]', '', titulo_norm)
    titulo_norm = re.sub(r'_+', '_', titulo_norm).strip('_')
    subcarpeta_tarea = titulo_norm[:60] or f"tarea_{instance.tarea_id or 'general'}"

    # 2. Normalizar nombre del archivo
    nombre_base, extension = os.path.splitext(filename)
    extension_norm = extension.lower()

    base_norm = unicodedata.normalize('NFKD', str(nombre_base)).encode('ascii', 'ignore').decode('utf-8').lower()
    base_norm = re.sub(r'\s+', '_', base_norm)
    base_norm = re.sub(r'[^a-z0-9_.-]', '', base_norm)
    base_norm = re.sub(r'_+', '_', base_norm).strip('_')
    if not base_norm:
        base_norm = "archivo"

    ahora = datetime.now()
    anio = ahora.strftime('%Y')
    mes = ahora.strftime('%m')
    nombre_final = f"{base_norm}{extension_norm}"

    # Django antepone settings.MEDIA_ROOT automáticamente
    return f"seguimiento/{subcarpeta_tarea}/{anio}/{mes}/{nombre_final}"


class ComentarioActualizacion(models.Model):
    """
    Registro cronológico de comentarios, novedades y pedidos de respuesta para la línea de tiempo.
    """
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="Tarea"
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="comentarios_gestion",
        verbose_name="Autor del Comentario"
    )
    quien_comenta = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Quién Comenta",
        help_text="Área, dependencia o cargo de quien emite el comentario (ej. Asesoría Técnica, Secretaría de Obras)"
    )
    mensaje = models.TextField(verbose_name="Contenido / Novedad")
    requiere_respuesta = models.BooleanField(
        default=False,
        verbose_name="Requiere Respuesta",
        help_text="Marca si esta novedad necesita atención o respuesta de otra área/autoridad"
    )
    resuelto = models.BooleanField(
        default=False,
        verbose_name="Requerimiento Resuelto"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Publicación")

    class Meta:
        verbose_name = "Comentario de Seguimiento"
        verbose_name_plural = "Comentarios de Seguimiento"
        ordering = ['created_at']

    def __str__(self):
        firmante = self.quien_comenta or self.autor.username
        return f"Comentario de {firmante} en {self.tarea.titulo} ({self.created_at:%d/%m/%Y %H:%M})"


class ArchivoAdjunto(models.Model):
    """
    Archivos multimedia adjuntos a una tarea o comentario (fotos, videos, PDFs con límite de 40MB).
    """
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name="archivos",
        verbose_name="Tarea"
    )
    comentario = models.ForeignKey(
        ComentarioActualizacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archivos",
        verbose_name="Comentario Vinculado (Opcional)"
    )
    archivo = models.FileField(
        upload_to=ruta_archivo_seguimiento,
        max_length=500,
        verbose_name="Archivo Adjunto"
    )
    nombre_original = models.CharField(max_length=255, verbose_name="Nombre Original del Archivo")
    tipo_mime = models.CharField(max_length=100, blank=True, verbose_name="Tipo MIME")
    tamano_bytes = models.PositiveIntegerField(default=0, verbose_name="Tamaño en Bytes")
    subido_el = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")

    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"
        ordering = ['-subido_el']

    def __str__(self):
        return f"{self.nombre_original} ({self.tamano_megabytes:.1f} MB)"

    @property
    def tamano_megabytes(self) -> float:
        return self.tamano_bytes / (1024 * 1024) if self.tamano_bytes else 0.0

    def clean(self):
        super().clean()
        # Validación de 40MB = 41943040 bytes
        LIMITE_40MB = 40 * 1024 * 1024
        if self.archivo and hasattr(self.archivo, 'size') and self.archivo.size > LIMITE_40MB:
            raise ValidationError(
                f"El archivo supera el tamaño máximo permitido de 40MB ({self.archivo.size / (1024*1024):.1f} MB)."
            )


class AuditLog(models.Model):
    """
    Registro inmutable de trazabilidad y auditoría de cambios para cumplimiento normativo.
    """
    ACCION_CREACION = 'CREACION'
    ACCION_MODIFICACION = 'MODIFICACION'
    ACCION_ARCHIVADO = 'ARCHIVADO'
    ACCION_DESARCHIVADO = 'DESARCHIVADO'
    ACCION_VALIDACION = 'VALIDACION'
    ACCION_RECHAZO = 'RECHAZO'

    ACCIONES_CHOICES = [
        (ACCION_CREACION, 'Creación'),
        (ACCION_MODIFICACION, 'Modificación'),
        (ACCION_ARCHIVADO, 'Archivado'),
        (ACCION_DESARCHIVADO, 'Desarchivado'),
        (ACCION_VALIDACION, 'Validación / Aprobación'),
        (ACCION_RECHAZO, 'Rechazo de Validación'),
    ]

    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name="auditorias",
        verbose_name="Tarea Afectada"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias_registradas",
        verbose_name="Usuario Responsable"
    )
    accion = models.CharField(max_length=50, choices=ACCIONES_CHOICES, verbose_name="Acción Realizada")
    campo_modificado = models.CharField(max_length=100, blank=True, verbose_name="Campo Modificado")
    valor_anterior = models.TextField(null=True, blank=True, verbose_name="Valor Anterior")
    valor_nuevo = models.TextField(null=True, blank=True, verbose_name="Valor Nuevo")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-timestamp']

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"[{self.timestamp:%d/%m/%Y %H:%M:%S}] {usuario_str} - {self.get_accion_display()} en #{self.tarea_id}"

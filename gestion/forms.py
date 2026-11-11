"""
Formularios de Gestión y Validación del Tablero Municipal.
Aplica reglas de negocio por rol y validaciones contables y operativas.
"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Tarea, ComentarioActualizacion, ArchivoAdjunto, Area, Direccion, Barrio, PerfilUsuario


class TareaForm(forms.ModelForm):
    """
    Formulario integral de Tarea con adaptación dinámica de permisos por rol.
    """
    class Meta:
        model = Tarea
        fields = [
            # 1. Identificación
            'titulo', 'descripcion', 'area_principal', 'direccion',
            'responsable_operativo', 'tipo_intervencion', 'prioridad',
            'prioritario_intendencia', 'areas_intervinientes',
            # 2. Planificación
            'estado', 'fecha_limite', 'porcentaje_general', 'porcentaje_fisico',
            # 3. Finanzas
            'presupuesto_oficial', 'monto_adjudicado', 'redeterminaciones',
            'ampliaciones', 'monto_devengado', 'monto_pagado', 'pagos_en_tramite',
            # 4. Territorio
            'barrio_principal', 'barrios_adicionales', 'modalidad_beneficiarios',
            'viviendas_directas', 'viviendas_indirectas',
            'personas_directas', 'personas_indirectas',
            'cantidad_beneficiarios_input', 'link_google_maps',
            # 5. Observaciones
            'observaciones'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Pavimentación Calle San Martín'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Descripción detallada de la obra o acción...'}),
            'area_principal': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.Select(attrs={'class': 'form-select'}),
            'responsable_operativo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del Director o Encargado'}),
            'tipo_intervencion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Infraestructura, Bacheo, Social'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'prioritario_intendencia': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'areas_intervinientes': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_limite': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'porcentaje_general': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '100', 'step': '0.01'}),
            'porcentaje_fisico': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '100', 'step': '0.01'}),
            'presupuesto_oficial': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'step': '0.01'}),
            'monto_adjudicado': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'step': '0.01'}),
            'redeterminaciones': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'step': '0.01'}),
            'ampliaciones': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'step': '0.01'}),
            'monto_devengado': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'step': '0.01'}),
            'monto_pagado': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'step': '0.01'}),
            'pagos_en_tramite': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'step': '0.01'}),
            'barrio_principal': forms.Select(attrs={'class': 'form-select'}),
            'barrios_adicionales': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'modalidad_beneficiarios': forms.Select(attrs={'class': 'form-select'}),
            'viviendas_directas': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'placeholder': '0'}),
            'viviendas_indirectas': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'placeholder': '0'}),
            'personas_directas': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'placeholder': 'Ej.: 35 asistentes'}),
            'personas_indirectas': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'placeholder': '0'}),
            'cantidad_beneficiarios_input': forms.HiddenInput(attrs={'min': '0'}),
            'link_google_maps': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://maps.google.com/...'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Motivo de bloqueo o notas de seguimiento...'}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        es_secretaria = False
        area_usuario = None

        if self.usuario and hasattr(self.usuario, 'perfil'):
            rol = self.usuario.perfil.rol
            area_usuario = self.usuario.perfil.area
            es_secretaria = (rol == PerfilUsuario.ROL_SECRETARIA)

        # Configurar campos no obligatorios explícitamente como required = False
        campos_opcionales = [
            'presupuesto_oficial', 'monto_adjudicado', 'redeterminaciones',
            'ampliaciones', 'monto_devengado', 'monto_pagado', 'pagos_en_tramite',
            'porcentaje_general', 'porcentaje_fisico', 'fecha_limite',
            'descripcion', 'direccion', 'responsable_operativo', 'tipo_intervencion',
            'viviendas_directas', 'viviendas_indirectas', 'personas_directas',
            'personas_indirectas', 'cantidad_beneficiarios_input',
            'link_google_maps', 'observaciones'
        ]
        for f in campos_opcionales:
            if f in self.fields:
                self.fields[f].required = False

        # Configurar Área Principal y Direcciones disponibles por defecto
        self.fields['area_principal'].queryset = Area.objects.filter(activo=True)
        self.fields['direccion'].queryset = Direccion.objects.filter(activo=True).select_related('area')

        # Si es una tarea nueva y el usuario tiene área asociada, preseleccionarla
        if not self.instance.pk and area_usuario:
            self.fields['area_principal'].initial = area_usuario

        # Regla de Seguridad para Secretarías:
        if es_secretaria:
            # 1. No puede marcar o desmarcar "Prioritario para Intendencia"
            self.fields['prioritario_intendencia'].disabled = True

            # 2. Solo puede crear y gestionar tareas de su propia Secretaría
            if area_usuario:
                self.fields['area_principal'].queryset = Area.objects.filter(pk=area_usuario.pk)
                self.fields['area_principal'].initial = area_usuario
                self.fields['direccion'].queryset = Direccion.objects.filter(area=area_usuario, activo=True)

            # 3. Si ya existe y es de otra secretaría, bloquear edición
            if self.instance.pk and self.instance.area_principal != area_usuario:
                for field_name in self.fields:
                    self.fields[field_name].disabled = True

            # 4. Regla Oficial de Negocio: Las tareas prioritarias para Intendencia
            # no pueden ser finalizadas directamente por una Secretaría (requieren validación superior)
            if self.instance.pk and self.instance.prioritario_intendencia:
                self.fields['estado'].choices = [
                    c for c in Tarea.ESTADOS_CHOICES if c[0] != Tarea.ESTADO_FINALIZADA
                ]
                self.fields['estado'].help_text = (
                    "Tarea Prioritaria para Intendencia: Al concluir los trabajos, "
                    "seleccione 'Para Validar' para que Intendencia audite y certifique su finalización formal."
                )

        # Regla 2: Si la tarea está en estado 'PARA_VALIDAR' y no es Intendencia/Asesoría, queda en solo lectura
        if self.instance.pk and self.instance.estado == Tarea.ESTADO_PARA_VALIDAR and es_secretaria:
            for field_name in self.fields:
                self.fields[field_name].disabled = True
            self.fields['observaciones'].help_text = "La tarea está en revisión (Solo Lectura) a la espera de validación superior."

    def clean_area_principal(self):
        area = self.cleaned_data.get('area_principal')
        if self.usuario and hasattr(self.usuario, 'perfil') and self.usuario.perfil.rol == PerfilUsuario.ROL_SECRETARIA:
            area_usuario = self.usuario.perfil.area
            if area_usuario and area != area_usuario:
                raise ValidationError("Una secretaría solo puede crear y gestionar tareas pertenecientes a su propia área.")
        return area

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        observaciones = cleaned_data.get('observaciones') or ''

        # Normalizar campos decimales vacíos a 0.00
        decimal_fields = [
            'presupuesto_oficial', 'monto_adjudicado', 'redeterminaciones',
            'ampliaciones', 'monto_devengado', 'monto_pagado', 'pagos_en_tramite',
            'porcentaje_general', 'porcentaje_fisico'
        ]
        for df in decimal_fields:
            if df in cleaned_data and cleaned_data[df] is None:
                cleaned_data[df] = Decimal('0.00')

        # 1. Justificación obligatoria para estado BLOQUEADA
        if estado == Tarea.ESTADO_BLOQUEADA and not observaciones.strip():
            self.add_error(
                'observaciones',
                'Es obligatorio justificar en el campo "Observaciones" el motivo por el cual la tarea queda Bloqueada.'
            )

        # 2. Control de Validación Superior para Tareas Prioritarias de Intendencia
        es_secretaria = False
        if self.usuario and hasattr(self.usuario, 'perfil'):
            es_secretaria = (self.usuario.perfil.rol == PerfilUsuario.ROL_SECRETARIA)

        es_prioritaria = (self.instance.pk and self.instance.prioritario_intendencia) or cleaned_data.get('prioritario_intendencia')
        if es_secretaria and es_prioritaria and estado == Tarea.ESTADO_FINALIZADA:
            self.add_error(
                'estado',
                'Las tareas con prioridad para Intendencia no pueden ser finalizadas directamente por la Secretaría. '
                'Debe enviar la tarea al estado "Para Validar" para que la finalización sea aprobada por Intendencia.'
            )

        # 3. Control Contable y Financiero
        adjudicado = cleaned_data.get('monto_adjudicado') or Decimal('0.00')
        redet = cleaned_data.get('redeterminaciones') or Decimal('0.00')
        ampl = cleaned_data.get('ampliaciones') or Decimal('0.00')
        devengado = cleaned_data.get('monto_devengado') or Decimal('0.00')
        pagado = cleaned_data.get('monto_pagado') or Decimal('0.00')

        mca = adjudicado + redet + ampl

        if pagado > devengado:
            self.add_error(
                'monto_pagado',
                f'El Monto Pagado (${pagado:,.2f}) no puede superar al Monto Devengado (${devengado:,.2f}).'
            )

        if mca > Decimal('0.00') and devengado > mca:
            self.add_error(
                'monto_devengado',
                f'El Monto Devengado (${devengado:,.2f}) no puede superar al Monto Contractual Actualizado (${mca:,.2f}).'
            )

        return cleaned_data


class ValidacionResolucionForm(forms.Form):
    """
    Formulario para resolver tareas en estado 'PARA_VALIDAR'.
    Permite Aprobar (Finalizada) o Rechazar (Vuelve a En Ejecución con motivo obligatorio).
    """
    ACCION_APROBAR = 'APROBAR'
    ACCION_RECHAZAR = 'RECHAZAR'

    ACCIONES = [
        (ACCION_APROBAR, 'Aprobar y Finalizar Tarea'),
        (ACCION_RECHAZAR, 'Rechazar Validación (Regresa a Ejecución)'),
    ]

    accion = forms.ChoiceField(
        choices=ACCIONES,
        widget=forms.RadioSelect(attrs={'class': 'form-radio'}),
        label="Resolución"
    )
    motivo_rechazo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Obligatorio en caso de rechazo: explique qué observaciones o documentación faltan...'
        }),
        label="Motivo / Observaciones del Rechazo"
    )

    def clean(self):
        cleaned_data = super().clean()
        accion = cleaned_data.get('accion')
        motivo = cleaned_data.get('motivo_rechazo') or ''

        if accion == self.ACCION_RECHAZAR and not motivo.strip():
            self.add_error(
                'motivo_rechazo',
                'Debe ingresar obligatoriamente un motivo para rechazar la validación de la tarea.'
            )

        return cleaned_data


class ComentarioForm(forms.ModelForm):
    """
    Formulario para agregar comentarios y requerimientos al timeline.
    """
    class Meta:
        model = ComentarioActualizacion
        fields = ['mensaje', 'quien_comenta', 'requiere_respuesta']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Ej.: Visita de obra. Se completó el adoquinado del primer tramo...'
            }),
            'quien_comenta': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej.: Asesoría Técnica / Secretaría de Obras'
            }),
            'requiere_respuesta': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ActualizacionSeguimientoForm(forms.ModelForm):
    """
    Formulario unificado para registrar la novedad/comentario junto con evidencias multimedia.
    """
    class Meta:
        model = ComentarioActualizacion
        fields = ['mensaje', 'quien_comenta', 'requiere_respuesta']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Ej.: Visita de obra. Se completó el adoquinado del primer tramo...'
            }),
            'quien_comenta': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej.: Asesoría Técnica / Secretaría de Obras'
            }),
            'requiere_respuesta': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ArchivoAdjuntoForm(forms.ModelForm):
    """
    Formulario de carga de archivos adjuntos con validación estricta de 40MB.
    """
    class Meta:
        model = ArchivoAdjunto
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': '.pdf,.jpg,.jpeg,.png,.webp,.mp4,.mov,.xlsx,.docx'
            })
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Límite de 40MB (40 * 1024 * 1024 bytes)
            LIMITE_40MB = 40 * 1024 * 1024
            if archivo.size > LIMITE_40MB:
                raise ValidationError(
                    f'El archivo "{archivo.name}" supera el tamaño máximo permitido de 40MB (tamaño: {archivo.size / (1024*1024):.1f}MB).'
                )
        return archivo


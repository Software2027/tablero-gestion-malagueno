"""
Señales de Django para auditoría automática y trazabilidad (AuditLog).
Captura modificaciones de campos críticos en el ciclo de vida de cada Tarea.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Tarea, AuditLog


# Campos sensibles a auditar en la Tarea
CAMPOS_AUDITABLES = [
    'estado',
    'prioridad',
    'prioritario_intendencia',
    'porcentaje_general',
    'porcentaje_fisico',
    'porcentaje_financiero',
    'presupuesto_oficial',
    'monto_adjudicado',
    'redeterminaciones',
    'ampliaciones',
    'monto_devengado',
    'monto_pagado',
    'pagos_en_tramite',
    'fecha_limite',
    'responsable_operativo',
    'barrio_principal',
    'observaciones',
    'archivado',
]


@receiver(pre_save, sender=Tarea)
def capturar_cambios_tarea(sender, instance, **kwargs):
    """
    Compara el estado previo del registro en la base de datos con los nuevos valores.
    Guarda los cambios detectados en una propiedad temporal `_cambios_auditoria`.
    """
    if not instance.pk:
        # Tarea nueva
        instance._cambios_auditoria = [{'accion': AuditLog.ACCION_CREACION, 'campo': 'id', 'anterior': None, 'nuevo': instance.titulo}]
        return

    try:
        instancia_anterior = Tarea.objects.get(pk=instance.pk)
    except Tarea.DoesNotExist:
        return

    cambios = []
    usuario = getattr(instance, '_current_user', None)

    for campo in CAMPOS_AUDITABLES:
        valor_antiguo = getattr(instancia_anterior, campo)
        valor_nuevo = getattr(instance, campo)

        # Si el campo es ForeignKey
        if hasattr(valor_antiguo, 'pk') or hasattr(valor_nuevo, 'pk'):
            valor_antiguo_str = str(valor_antiguo) if valor_antiguo else ''
            valor_nuevo_str = str(valor_nuevo) if valor_nuevo else ''
            ha_cambiado = (valor_antiguo_str != valor_nuevo_str)
        else:
            ha_cambiado = (valor_antiguo != valor_nuevo)
            valor_antiguo_str = str(valor_antiguo) if valor_antiguo is not None else ''
            valor_nuevo_str = str(valor_nuevo) if valor_nuevo is not None else ''

        if ha_cambiado:
            accion = AuditLog.ACCION_MODIFICACION
            if campo == 'archivado' and valor_nuevo is True:
                accion = AuditLog.ACCION_ARCHIVADO
            elif campo == 'archivado' and valor_nuevo is False:
                accion = AuditLog.ACCION_DESARCHIVADO
            elif campo == 'estado' and valor_nuevo == Tarea.ESTADO_FINALIZADA:
                accion = AuditLog.ACCION_VALIDACION

            cambios.append({
                'accion': accion,
                'campo': campo,
                'anterior': valor_antiguo_str,
                'nuevo': valor_nuevo_str,
                'usuario': usuario,
            })

    instance._cambios_auditoria = cambios


@receiver(post_save, sender=Tarea)
def registrar_audit_logs(sender, instance, created, **kwargs):
    """
    Persiste en la tabla inmutable AuditLog los cambios detectados en pre_save.
    """
    cambios = getattr(instance, '_cambios_auditoria', [])
    usuario = getattr(instance, '_current_user', None)

    for c in cambios:
        AuditLog.objects.create(
            tarea=instance,
            usuario=c.get('usuario') or usuario,
            accion=c['accion'],
            campo_modificado=c['campo'],
            valor_anterior=c['anterior'],
            valor_nuevo=c['nuevo']
        )

    # Limpiar lista de cambios de la instancia
    instance._cambios_auditoria = []


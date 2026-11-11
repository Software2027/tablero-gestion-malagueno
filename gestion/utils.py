"""
Módulo de Utilidades y Reglas de Negocio - Tablero de Gestión Municipal Malagueño 4.0.
Centraliza algoritmos de cálculo de salud operativa (semáforo), métricas financieras
y agregaciones territoriales.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from django.db.models import Sum, Count, Q
from .models import Tarea, Area, Direccion, Barrio


# ==============================================================================
# 1. MOTOR DEL SEMÁFORO DE SALUD OPERATIVA
# ==============================================================================
SEMAFORO_ROJO = 'ROJO'        # Crítico: al menos 1 tarea vencida
SEMAFORO_AMARILLO = 'AMARILLO'  # Atención: tareas bloqueadas o vencimiento en <= 7 días
SEMAFORO_VERDE = 'VERDE'      # Saludable: al día
SEMAFORO_GRIS = 'GRIS'        # Sin tareas asignadas

COLOR_SEMAFORO_HEX = {
    SEMAFORO_ROJO: '#dc2626',
    SEMAFORO_AMARILLO: '#d97706',
    SEMAFORO_VERDE: '#338c33',
    SEMAFORO_GRIS: '#9ca3af',
}

COLOR_SEMAFORO_BG = {
    SEMAFORO_ROJO: '#fee2e2',
    SEMAFORO_AMARILLO: '#fef3c7',
    SEMAFORO_VERDE: '#eaf4ea',
    SEMAFORO_GRIS: '#f1f5f9',
}


def calcular_semaforo_area(area: Area) -> Dict[str, Any]:
    """
    Evalúa la salud operativa de una Secretaría según las tareas asignadas.
    Reglas:
    - Rojo: Tiene al menos una tarea vencida (fecha_limite < hoy y estado != FINALIZADA).
    - Amarillo: Sin vencidas, pero con tareas BLOQUEADA o que vencen en <= 7 días.
    - Verde: Tareas activas en curso normal o finalizadas sin alertas.
    - Gris: 0 tareas registradas en el área.
    """
    hoy = date.today()
    limite_alerta = hoy + timedelta(days=7)

    # Tareas propias no archivadas
    tareas = Tarea.objects.filter(area_principal=area, archivado=False)
    total_tareas = tareas.count()

    if total_tareas == 0:
        return {
            'estado': SEMAFORO_GRIS,
            'color_hex': COLOR_SEMAFORO_HEX[SEMAFORO_GRIS],
            'color_bg': COLOR_SEMAFORO_BG[SEMAFORO_GRIS],
            'mensaje': 'Sin intervenciones asignadas',
            'total_tareas': 0,
            'vencidas': 0,
            'bloqueadas': 0,
            'por_vencer': 0,
            'finalizadas': 0,
            'porcentaje_cumplimiento': 0.0,
        }

    # 1. ¿Tiene al menos una tarea VENCIDA?
    vencidas = tareas.filter(
        fecha_limite__lt=hoy
    ).exclude(
        estado=Tarea.ESTADO_FINALIZADA
    ).count()

    if vencidas > 0:
        estado = SEMAFORO_ROJO
        mensaje = f'Crítico: {vencidas} tarea(s) vencida(s)'
    else:
        # 2. ¿Tiene tareas BLOQUEADAS o que vencen en los próximos 7 días?
        bloqueadas = tareas.filter(estado=Tarea.ESTADO_BLOQUEADA).count()
        por_vencer = tareas.filter(
            fecha_limite__gte=hoy,
            fecha_limite__lte=limite_alerta
        ).exclude(
            estado=Tarea.ESTADO_FINALIZADA
        ).count()

        if bloqueadas > 0 or por_vencer > 0:
            estado = SEMAFORO_AMARILLO
            detalles = []
            if bloqueadas > 0:
                detalles.append(f"{bloqueadas} bloqueada(s)")
            if por_vencer > 0:
                detalles.append(f"{por_vencer} por vencer en 7 días")
            mensaje = f"Atención: {', '.join(detalles)}"
        else:
            estado = SEMAFORO_VERDE
            mensaje = 'Al día: Ejecución en cronograma'

    finalizadas = tareas.filter(estado=Tarea.ESTADO_FINALIZADA).count()
    porcentaje_cumplimiento = round((finalizadas / total_tareas) * 100, 1) if total_tareas > 0 else 0.0

    return {
        'estado': estado,
        'color_hex': COLOR_SEMAFORO_HEX[estado],
        'color_bg': COLOR_SEMAFORO_BG[estado],
        'mensaje': mensaje,
        'total_tareas': total_tareas,
        'vencidas': vencidas,
        'bloqueadas': tareas.filter(estado=Tarea.ESTADO_BLOQUEADA).count(),
        'por_vencer': tareas.filter(
            fecha_limite__gte=hoy,
            fecha_limite__lte=limite_alerta
        ).exclude(estado=Tarea.ESTADO_FINALIZADA).count(),
        'finalizadas': finalizadas,
        'porcentaje_cumplimiento': porcentaje_cumplimiento,
    }


# ==============================================================================
# 2. CONSOLIDACIÓN FINANCIERA INSTITUCIONAL
# ==============================================================================
def consolidar_metricas_financieras(queryset=None) -> Dict[str, Any]:
    """
    Calcula los totales financieros consolidados para un conjunto de tareas o todo el municipio.
    MCA = Adjudicado + Redeterminaciones + Ampliaciones
    Devengado Pendiente = max(0, Devengado - Pagado)
    Avance Financiero % = (Pagado / MCA) * 100
    """
    if queryset is None:
        queryset = Tarea.objects.filter(archivado=False)

    agregaciones = queryset.aggregate(
        total_presupuesto_oficial=Sum('presupuesto_oficial'),
        total_adjudicado=Sum('monto_adjudicado'),
        total_redeterminaciones=Sum('redeterminaciones'),
        total_ampliaciones=Sum('ampliaciones'),
        total_devengado=Sum('monto_devengado'),
        total_pagado=Sum('monto_pagado'),
        total_en_tramite=Sum('pagos_en_tramite'),
    )

    oficial = agregaciones['total_presupuesto_oficial'] or Decimal('0.00')
    adjudicado = agregaciones['total_adjudicado'] or Decimal('0.00')
    redet = agregaciones['total_redeterminaciones'] or Decimal('0.00')
    ampl = agregaciones['total_ampliaciones'] or Decimal('0.00')
    devengado = agregaciones['total_devengado'] or Decimal('0.00')
    pagado = agregaciones['total_pagado'] or Decimal('0.00')
    en_tramite = agregaciones['total_en_tramite'] or Decimal('0.00')

    mca = adjudicado + redet + ampl
    pendiente_pago = max(Decimal('0.00'), devengado - pagado)
    saldo_por_ejecutar = max(Decimal('0.00'), mca - pagado)

    if mca > Decimal('0.00'):
        porcentaje_ejecutado = round(min((pagado / mca) * Decimal('100.00'), Decimal('100.00')), 2)
    else:
        porcentaje_ejecutado = Decimal('0.00')

    return {
        'presupuesto_oficial': oficial,
        'monto_adjudicado': adjudicado,
        'redeterminaciones': redet,
        'ampliaciones': ampl,
        'monto_contractual_actualizado': mca,
        'monto_devengado': devengado,
        'monto_pagado': pagado,
        'pagos_en_tramite': en_tramite,
        'devengado_pendiente_pago': pendiente_pago,
        'saldo_por_ejecutar': saldo_por_ejecutar,
        'porcentaje_ejecucion_financiera': porcentaje_ejecutado,
    }


# ==============================================================================
# 3. CONSOLIDACIÓN DE KPIS DEL DASHBOARD
# ==============================================================================
def obtener_kpis_dashboard(usuario=None) -> Dict[str, Any]:
    """
    Obtiene los indicadores ejecutivos principales:
    - Total de tareas activas
    - En Ejecución
    - Vencidas
    - Para Validar
    - Bloqueadas
    - Finalizadas
    """
    hoy = date.today()
    qs = Tarea.objects.filter(archivado=False)

    # Filtrado según alcance del rol
    if usuario and hasattr(usuario, 'perfil') and usuario.perfil.rol == 'SECRETARIA':
        area_usuario = usuario.perfil.area
        qs = qs.filter(Q(area_principal=area_usuario) | Q(areas_intervinientes=area_usuario)).distinct()

    total = qs.count()
    en_ejecucion = qs.filter(estado=Tarea.ESTADO_EN_EJECUCION).count()
    para_validar = qs.filter(estado=Tarea.ESTADO_PARA_VALIDAR).count()
    bloqueadas = qs.filter(estado=Tarea.ESTADO_BLOQUEADA).count()
    finalizadas = qs.filter(estado=Tarea.ESTADO_FINALIZADA).count()
    pendientes = qs.filter(estado=Tarea.ESTADO_PENDIENTE).count()

    vencidas = qs.filter(
        fecha_limite__lt=hoy
    ).exclude(
        estado=Tarea.ESTADO_FINALIZADA
    ).count()

    finanzas = consolidar_metricas_financieras(qs)

    return {
        'total': total,
        'en_ejecucion': en_ejecucion,
        'para_validar': para_validar,
        'bloqueadas': bloqueadas,
        'finalizadas': finalizadas,
        'pendientes': pendientes,
        'vencidas': vencidas,
        'finanzas': finanzas,
    }


# ==============================================================================
# 4. IMPACTO TERRITORIAL POR BARRIO
# ==============================================================================
def consolidar_impacto_barrial() -> List[Dict[str, Any]]:
    """
    Agrupa la inversión y beneficiarios por barrio principal.
    Cumple con la regla de negocio: el Barrio Principal absorbe el 100% de la inversión
    para evitar duplicaciones presupuestarias.
    """
    barrios = Barrio.objects.all()
    resultado = []

    for b in barrios:
        tareas_principales = Tarea.objects.filter(barrio_principal=b, archivado=False)
        inversion = Decimal('0.00')
        beneficiarios_totales = 0

        for t in tareas_principales:
            inversion += t.monto_contractual_actualizado
            beneficiarios_totales += t.beneficiarios_calculados

        # Tareas adicionales donde el barrio interviene pero sin sumar monto
        tareas_adicionales_count = Tarea.objects.filter(barrios_adicionales=b, archivado=False).count()

        resultado.append({
            'barrio': b,
            'total_inversion': inversion,
            'beneficiarios_estimados': beneficiarios_totales,
            'tareas_principales_count': tareas_principales.count(),
            'tareas_adicionales_count': tareas_adicionales_count,
            'total_intervenciones': tareas_principales.count() + tareas_adicionales_count,
        })

    # Ordenar por mayor inversión
    resultado.sort(key=lambda x: x['total_inversion'], reverse=True)
    return resultado


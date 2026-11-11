/**
 * Validaciones y Cálculos en Tiempo Real para Formularios de Gestión Municipal
 * Tablero de Gestión Municipal - Malagueño 4.0
 * 
 * Funcionalidades:
 * 1. Cálculo en tiempo real de MCA (Monto Contractual Actualizado).
 * 2. Cálculo en tiempo real de % Avance Financiero: (Pagado / MCA) * 100.
 * 3. Cálculo de Devengado Pendiente de Pago: (Devengado - Pagado).
 * 4. Control de consistencia contable: Pagado <= Devengado <= MCA con advertencias en vivo.
 * 5. Estimación comunitaria: Viviendas * 3.5 personas.
 * 6. Validación mandatoria de motivo de bloqueo si estado es BLOQUEADA.
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('taskForm') || document.getElementById('formTarea');
    if (!form) return;

    // Elementos de formulario
    const inputAdjudicado = document.getElementById('id_monto_adjudicado');
    const inputRedet = document.getElementById('id_redeterminaciones');
    const inputAmpl = document.getElementById('id_ampliaciones');
    const inputDevengado = document.getElementById('id_monto_devengado');
    const inputPagado = document.getElementById('id_monto_pagado');
    const inputEnTramite = document.getElementById('id_pagos_en_tramite');

    const inputAvanceFin = document.getElementById('live_avance_financiero');
    const liveMca = document.getElementById('liveMca');
    const liveDevengado = document.getElementById('liveDevengado');
    const livePagado = document.getElementById('livePagado');
    const livePendiente = document.getElementById('livePendiente');
    const liveWarning = document.getElementById('liveFinancialWarning');

    const selectModalidad = document.getElementById('id_modalidad_beneficiarios');
    const inputCantidadBenef = document.getElementById('id_cantidad_beneficiarios_input');
    const liveBenefPreview = document.getElementById('liveBeneficiariosPreview');

    const selectEstado = document.getElementById('id_estado');
    const textareaObservaciones = document.getElementById('id_observaciones');

    function fmtMoney(num) {
        return '$' + (Number(num) || 0).toLocaleString('es-AR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // =========================================================================
    // 1. CÁLCULOS FINANCIEROS EN VIVO
    // =========================================================================
    function actualizarCalculosFinancieros() {
        const adjudicado = parseFloat(inputAdjudicado?.value) || 0;
        const redet = parseFloat(inputRedet?.value) || 0;
        const ampl = parseFloat(inputAmpl?.value) || 0;
        const devengado = parseFloat(inputDevengado?.value) || 0;
        const pagado = parseFloat(inputPagado?.value) || 0;
        const enTramite = parseFloat(inputEnTramite?.value) || 0;

        const mca = adjudicado + redet + ampl;
        const pendiente = Math.max(0, devengado - pagado);
        const pctFinanciero = mca > 0 ? Math.min(100, Math.max(0, (pagado / mca) * 100)) : 0;

        // Actualizar valores en pantalla
        if (inputAvanceFin) {
            inputAvanceFin.value = `${pctFinanciero.toFixed(2)}%`;
        }
        if (liveMca) liveMca.textContent = fmtMoney(mca);
        if (liveDevengado) liveDevengado.textContent = fmtMoney(devengado);
        if (livePagado) livePagado.textContent = fmtMoney(pagado);
        if (livePendiente) livePendiente.textContent = fmtMoney(pendiente);

        // Alertas de inconsistencia contable en vivo
        if (liveWarning) {
            if (pagado > devengado) {
                liveWarning.style.display = 'block';
                liveWarning.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                        <span>
                            <i class="fa-solid fa-triangle-exclamation"></i>
                            <b>Inconsistencia contable:</b> El Monto Pagado (${fmtMoney(pagado)}) supera al Monto Devengado (${fmtMoney(devengado)}).
                        </span>
                        <button type="button" id="btnAjustarDevengado" class="btn alt btn-sm" style="border-color: #fca5a5; background: #fff;">
                            <i class="fa-solid fa-wrench"></i> Ajustar Devengado a ${fmtMoney(pagado)}
                        </button>
                    </div>
                `;

                const btnFix = document.getElementById('btnAjustarDevengado');
                if (btnFix) {
                    btnFix.addEventListener('click', () => {
                        if (inputDevengado) {
                            inputDevengado.value = pagado.toFixed(2);
                            actualizarCalculosFinancieros();
                        }
                    });
                }
            } else if (mca > 0 && devengado > mca) {
                liveWarning.style.display = 'block';
                liveWarning.innerHTML = `
                    <span>
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <b>Inconsistencia contable:</b> El Monto Devengado (${fmtMoney(devengado)}) supera al Monto Contractual Actualizado (${fmtMoney(mca)}).
                    </span>
                `;
            } else {
                liveWarning.style.display = 'none';
                liveWarning.innerHTML = '';
            }
        }
    }

    // Escuchar eventos en todos los inputs financieros
    const financialInputs = [
        inputAdjudicado, inputRedet, inputAmpl,
        inputDevengado, inputPagado, inputEnTramite
    ];
    financialInputs.forEach(inp => {
        if (inp) {
            inp.addEventListener('input', actualizarCalculosFinancieros);
            inp.addEventListener('change', actualizarCalculosFinancieros);
        }
    });

    // Auto-ajuste sugerido: si el usuario escribe Pagado y Devengado está en 0, sincronizar
    if (inputPagado && inputDevengado) {
        inputPagado.addEventListener('blur', () => {
            const dev = parseFloat(inputDevengado.value) || 0;
            const pag = parseFloat(inputPagado.value) || 0;
            if (pag > 0 && dev === 0) {
                inputDevengado.value = pag.toFixed(2);
                actualizarCalculosFinancieros();
            }
        });
    }

    // =========================================================================
    // 2. IMPACTO TERRITORIAL Y BENEFICIARIOS EN VIVO CON CATASTRO OFICIAL
    // =========================================================================
    const selectBarrioPrincipal = document.getElementById('id_barrio_principal');
    const mapaBarriosEl = document.getElementById('mapaBarriosData');
    const alertaBarrioRef = document.getElementById('alertaBarrioReferencia');
    const refBarrioNombre = document.getElementById('refBarrioNombre');
    const refBarrioViviendas = document.getElementById('refBarrioViviendas');

    const bloqueViviendas = document.getElementById('bloqueModalidadViviendas');
    const bloquePersonas = document.getElementById('bloqueModalidadPersonas');
    const bloqueSinDato = document.getElementById('bloqueModalidadSinDato');

    const inputVivDirectas = document.getElementById('id_viviendas_directas');
    const inputVivIndirectas = document.getElementById('id_viviendas_indirectas');
    const calcHabDirectos = document.getElementById('calc_habitantes_directos');
    const calcHabIndirectos = document.getElementById('calc_habitantes_indirectos');

    const inputPersDirectas = document.getElementById('id_personas_directas');
    const inputPersIndirectas = document.getElementById('id_personas_indirectas');

    let mapaBarrios = {};
    if (mapaBarriosEl) {
        try {
            mapaBarrios = JSON.parse(mapaBarriosEl.textContent || '{}');
        } catch (err) {
            console.error('Error al parsear mapa de barrios:', err);
        }
    }

    function actualizarCalculosBeneficiarios() {
        const modalidad = selectModalidad ? selectModalidad.value : 'VIVIENDAS';

        if (modalidad === 'VIVIENDAS') {
            const vDir = parseInt(inputVivDirectas?.value, 10) || 0;
            const vInd = parseInt(inputVivIndirectas?.value, 10) || 0;
            const habDir = Math.round(vDir * 3.5);
            const habInd = Math.round(vInd * 3.5);

            if (calcHabDirectos) calcHabDirectos.value = habDir.toLocaleString('es-AR');
            if (calcHabIndirectos) calcHabIndirectos.value = habInd.toLocaleString('es-AR');

            if (inputCantidadBenef) {
                inputCantidadBenef.value = (vDir + vInd);
            }
        } else if (modalidad === 'PERSONAS') {
            const pDir = parseInt(inputPersDirectas?.value, 10) || 0;
            const pInd = parseInt(inputPersIndirectas?.value, 10) || 0;

            if (inputCantidadBenef) {
                inputCantidadBenef.value = (pDir + pInd);
            }
        } else {
            if (inputCantidadBenef) {
                inputCantidadBenef.value = 0;
            }
        }
    }

    function alternarBloquesModalidad() {
        const modalidad = selectModalidad ? selectModalidad.value : 'VIVIENDAS';

        if (bloqueViviendas) bloqueViviendas.style.display = (modalidad === 'VIVIENDAS') ? 'block' : 'none';
        if (bloquePersonas) bloquePersonas.style.display = (modalidad === 'PERSONAS') ? 'block' : 'none';
        if (bloqueSinDato) bloqueSinDato.style.display = (modalidad === 'SIN_DATO') ? 'block' : 'none';

        actualizarCalculosBeneficiarios();
    }

    function actualizarAlertaBarrio() {
        if (!selectBarrioPrincipal || !alertaBarrioRef) return;
        const barrioId = selectBarrioPrincipal.value;
        const barrioData = barrioId ? mapaBarrios[barrioId] : null;

        if (barrioData) {
            if (refBarrioNombre) refBarrioNombre.textContent = barrioData.nombre;
            if (refBarrioViviendas) refBarrioViviendas.textContent = barrioData.viviendas;
            alertaBarrioRef.style.display = 'block';
        } else {
            alertaBarrioRef.style.display = 'none';
        }
    }

    if (selectBarrioPrincipal) {
        selectBarrioPrincipal.addEventListener('change', actualizarAlertaBarrio);
        actualizarAlertaBarrio();
    }

    if (selectModalidad) {
        selectModalidad.addEventListener('change', alternarBloquesModalidad);
        alternarBloquesModalidad();
    }

    // Escuchar inputs de viviendas
    [inputVivDirectas, inputVivIndirectas].forEach(inp => {
        if (inp) {
            inp.addEventListener('input', actualizarCalculosBeneficiarios);
            inp.addEventListener('change', actualizarCalculosBeneficiarios);
        }
    });

    // Escuchar inputs de personas
    [inputPersDirectas, inputPersIndirectas].forEach(inp => {
        if (inp) {
            inp.addEventListener('input', actualizarCalculosBeneficiarios);
            inp.addEventListener('change', actualizarCalculosBeneficiarios);
        }
    });

    // =========================================================================
    // 3. ESTADO BLOQUEADA Y MOTIVO MANDATORIO
    // =========================================================================
    function verificarEstadoBloqueada() {
        if (!selectEstado || !textareaObservaciones) return;
        if (selectEstado.value === 'BLOQUEADA') {
            textareaObservaciones.style.borderColor = '#d97706';
            textareaObservaciones.style.backgroundColor = '#fffbeb';
            if (!textareaObservaciones.value.trim()) {
                textareaObservaciones.placeholder = 'ATENCIÓN OBLIGATORIA: Ingrese aquí el motivo, impedimento o traba que bloquea la tarea...';
            }
        } else {
            textareaObservaciones.style.borderColor = '';
            textareaObservaciones.style.backgroundColor = '';
        }
    }

    if (selectEstado && textareaObservaciones) {
        selectEstado.addEventListener('change', verificarEstadoBloqueada);
        verificarEstadoBloqueada();
    }

    // =========================================================================
    // 4. VALIDACIÓN PREVENTIVA ANTES DE ENVIAR (SUBMIT)
    // =========================================================================
    form.addEventListener('submit', (e) => {
        // Regla 1: Justificación obligatoria en bloqueo
        if (selectEstado && selectEstado.value === 'BLOQUEADA') {
            if (!textareaObservaciones.value.trim()) {
                e.preventDefault();
                alert('Es obligatorio documentar el motivo o justificación en "Observaciones" para guardar una tarea en estado BLOQUEADA.');
                textareaObservaciones.focus();
                return false;
            }
        }

        // Regla 2: Pagado <= Devengado
        const devengado = parseFloat(inputDevengado?.value) || 0;
        const pagado = parseFloat(inputPagado?.value) || 0;
        const adjudicado = parseFloat(inputAdjudicado?.value) || 0;
        const redet = parseFloat(inputRedet?.value) || 0;
        const ampl = parseFloat(inputAmpl?.value) || 0;
        const mca = adjudicado + redet + ampl;

        if (pagado > devengado) {
            e.preventDefault();
            alert(`Inconsistencia Contable:\nEl Monto Pagado ($${pagado.toLocaleString('es-AR', {minimumFractionDigits: 2})}) no puede ser mayor al Monto Devengado ($${devengado.toLocaleString('es-AR', {minimumFractionDigits: 2})}).\n\nPor favor ingrese en Devengado un valor igual o superior al Pagado.`);
            inputDevengado?.focus();
            return false;
        }

        // Regla 3: Devengado <= MCA
        if (mca > 0 && devengado > mca) {
            e.preventDefault();
            alert(`Inconsistencia Presupuestaria:\nEl Monto Devengado ($${devengado.toLocaleString('es-AR', {minimumFractionDigits: 2})}) supera al Monto Contractual Actualizado ($${mca.toLocaleString('es-AR', {minimumFractionDigits: 2})}).\n\nEl devengado no puede superar el contrato.`);
            inputDevengado?.focus();
            return false;
        }
    });

    // Ejecutar cálculos iniciales
    actualizarCalculosFinancieros();
    actualizarCalculosBeneficiarios();

    // =========================================================================
    // 5. FILTRADO DINÁMICO DE DIRECCIONES Y SUBDIRECCIONES POR ÁREA
    // =========================================================================
    const selectArea = document.getElementById('id_area_principal');
    const selectDireccion = document.getElementById('id_direccion');
    const mapaDataEl = document.getElementById('mapaDireccionesData');

    if (selectArea && selectDireccion && mapaDataEl) {
        let mapaDirecciones = {};
        try {
            mapaDirecciones = JSON.parse(mapaDataEl.textContent || '{}');
        } catch (err) {
            console.error('Error al parsear mapa de dependencias:', err);
        }

        const direccionInicial = selectDireccion.value;

        function filtrarDireccionesPorArea(esCargaInicial = false) {
            const areaId = selectArea.value;
            const dirSeleccionada = esCargaInicial ? direccionInicial : selectDireccion.value;

            selectDireccion.innerHTML = '<option value="">---------</option>';

            if (!areaId || !mapaDirecciones[areaId]) {
                return;
            }

            const dependencias = mapaDirecciones[areaId];
            dependencias.forEach(dep => {
                const opt = document.createElement('option');
                opt.value = dep.id;
                opt.textContent = dep.nombre;
                if (String(dep.id) === String(dirSeleccionada)) {
                    opt.selected = true;
                }
                selectDireccion.appendChild(opt);
            });
        }

        selectArea.addEventListener('change', () => filtrarDireccionesPorArea(false));

        if (selectArea.value) {
            filtrarDireccionesPorArea(true);
        }
    }
});

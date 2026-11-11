# Manual Integral de Operación y Roles del Sistema
**Plataforma de Control de Gestión Municipal · MALAGUEÑO**  
*Gestión 2023 - 2027 · Intendente Marcos Fey*

---

## 1. Objetivo del Sistema

### 1.1. Objetivo General
Centralizar, monitorear y auditar en tiempo real la planificación, ejecución operativa, impacto territorial e inversión económica de todas las obras, proyectos y servicios ejecutados por el Municipio de Malagueño, brindando a la conducción ejecutiva y a las secretarías una herramienta unificada para la toma de decisiones estratégicas.

### 1.2. Objetivos Específicos
1. **Trazabilidad y Transparencia:** Registrar de manera inmutable el historial completo de cambios, responsables, fechas y montos de cada intervención municipal.
2. **Control Preventivo de Plazos:** Detectar desvíos y cuellos de botella tempranamente mediante un sistema algorítmico de semáforos de salud operativa.
3. **Control Financiero Consolidado:** Distinguir con precisión el presupuesto oficial, los compromisos contractuales actualizados (MCA), el devengado contable y los desembolsos reales de Tesorería.
4. **Equidad y Cobertura Territorial:** Medir el impacto presupuestario y la cantidad de vecinos beneficiados en cada uno de los 31 barrios y parajes catastrados de Malagueño.
5. **Circuitos de Validación Superior:** Garantizar que ningún proyecto de alta prioridad estratégica sea cerrado sin la auditoría y certificación formal de Intendencia o Asesoría Técnica.

---

## 2. Alcance del Sistema

El sistema abarca la totalidad del aparato ejecutivo municipal de Malagueño:

- **Cobertura Institucional:** Comprende las **14 Secretarías Municipales** y sus Direcciones ejecutoras dependientes.
- **Cobertura Territorial:** Registra intervenciones geolocalizadas en los **31 barrios oficiales** (urbanizaciones abiertas y barrios cerrados), computando viviendas y personas alcanzadas.
- **Gestión Presupuestaria:** Imputación de contratos, redeterminaciones por inflación, ampliaciones, certificaciones de obra y órdenes de pago.
- **Instrumentos de Salida:**
  - Panel Ejecutivo en vivo con métricas, gráficos y semáforos de salud.
  - Informe Ejecutivo de Estado de Situación en PDF (estructura oficial de 5 secciones).
  - Exportación de bases de datos a planillas CSV (compatible con Excel).
  - Módulo de respaldo y restauración atómica en formato JSON.

---

## 3. Matriz de Roles y Permisos del Sistema

El sistema implementa un modelo de control de acceso basado en roles (RBAC) con tres perfiles jerárquicos:

| Característica / Acción | INTENDENCIA | ASESORÍA TÉCNICA | SECRETARÍA |
| :--- | :---: | :---: | :---: |
| **Nivel Jerárquico** | Nivel 1 (Superior) | Nivel 2 (Supervisión) | Nivel 3 (Operativo) |
| **Ámbito de Visibilidad de Tareas** | Total (Todas las áreas) | Total (Todas las áreas) | Solo su Secretaría + Áreas intervinientes |
| **Creación y Edición de Tareas** | Sí (Todas las áreas) | Sí (Todas las áreas) | Sí (Solo de su Secretaría) |
| **Marcar Prioritario para Intendencia (★)** | **Sí** | **Sí** | No (Restringido) |
| **Finalizar Tareas Ordinarias** | Sí | Sí | Sí |
| **Finalizar Tareas Prioritarias de Intendencia** | **Sí (Exclusivo)** | **Sí (Exclusivo)** | **No (Debe enviar a 'Para Validar')** |
| **Aprobar / Rechazar Resoluciones** | **Sí** | **Sí** | No |
| **Acceso a Panel Ejecutivo Global** | Sí | Sí | Sí (Vista ejecutiva) |
| **Acceso a Módulo Datos y Respaldo JSON** | **Sí** | **Sí** | No (Oculto) |
| **Exportación de Reportes PDF y CSV** | Sí | Sí | Sí (Filtrado a su ámbito) |

---

## 4. Funcionamiento Paso a Paso según el Rol

### 4.1. Flujo de Trabajo: Rol SECRETARÍA (Usuario Sectorial)

Este rol es utilizado por Secretarios, Directores y personal técnico de cada dependencia municipal para gestionar el día a día de sus proyectos.

#### Paso 1: Ingreso a la Plataforma
- El usuario ingresa a la URL del panel e inicia sesión con su usuario sectorial (ej. `sec.obras`, `sec.salud`).
- El sistema detecta su secretaría y adapta el menú y las listas automáticamente.

#### Paso 2: Creación o Modificación de Tareas
- Al hacer clic en **"Nueva tarea municipal"**, completa el formulario estructurado en sus 5 secciones obligatorias:
  1. **Identificación y Responsables:** Título claro, descripción, dirección ejecutora, responsable operativo y secretarías intervinientes si es un trabajo conjunto.
  2. **Planificación y Avances:** Define el estado inicial (`Pendiente` o `En ejecución`), la fecha límite prevista y el porcentaje de avance general y físico.
  3. **Presupuesto y Ejecución Financiera:** Carga los montos en moneda nacional (Presupuesto Oficial, Monto Adjudicado, Redeterminaciones, Ampliaciones, Devengado, Pagado y Pagos en Trámite). Si la tarea no tiene presupuesto asignado, los campos pueden dejarse en `$ 0,00`.
  4. **Impacto Territorial y Beneficiarios:** Selecciona el barrio principal (donde se imputa la inversión económica) y la modalidad de beneficiarios:
     - *Por viviendas:* Ingresa viviendas directas e indirectas (el sistema multiplica automáticamente por 3,5 hab/vivienda).
     - *Por personas:* Para capacitaciones, atención médica o eventos sociales.
     - *Sin beneficiarios cuantificados:* Para tareas administrativas o de mantenimiento menor.
  5. **Observaciones:** Notas aclaratorias o justificación de bloqueo.

#### Paso 3: Seguimiento y Actualización
- A medida que la obra o servicio avanza en territorio, el responsable actualiza periódicamente el porcentaje de avance físico y registra los nuevos pagos emitidos por Tesorería.
- Si un proyecto se frena por causas externas (ej. demoras climáticas, falta de insumos), el usuario cambia el estado a **"Bloqueada"** y el formulario le exige ingresar obligatoriamente el motivo de bloqueo en *Observaciones*.

#### Paso 4: Cierre del Proyecto
- **Si la tarea es Ordinaria:** Al terminar los trabajos, la Secretaría selecciona el estado **"Finalizada"** y guarda. La tarea queda concluida.
- **Si la tarea tiene el marcador Prioritario para Intendencia (★):**
  - La opción *"Finalizada"* se encuentra deshabilitada y oculta en el selector.
  - La Secretaría debe cambiar el estado a **"Para Validar"**.
  - El sistema notifica al área superior que los trabajos concluyeron y que el expediente está listo para certificación formal.

---

### 4.2. Flujo de Trabajo: Roles INTENDENCIA y ASESORÍA TÉCNICA (Conducción Superior)

Estos roles están destinados al Intendente Municipal, Secretario de Gobierno, Jefe de Gabinete y Asesores Técnicos de Planificación Estratégica.

#### Paso 1: Monitoreo Estratégico y Tablero de Control
- Al acceder al **Panel Ejecutivo**, visualizan:
  - Métricas consolidadas del Municipio: Total de tareas, finalizadas, en ejecución y vencidas.
  - Balance presupuestario global: MCA comprometido, monto devengado, pagado y deuda flotante.
  - **Semáforo de Salud Operativa de las 14 Secretarías:** Identifica al instante dependencias con alertas rojas (tareas vencidas) o amarillas (tareas bloqueadas o próximas a vencer).
  - **Matriz de Inversión por Barrio:** Dónde se está invirtiendo el presupuesto y cuántos habitantes han sido beneficiados en cada sector de Malagueño.

#### Paso 2: Asignación de Prioridad de Intendencia
- Desde la ficha de cualquier tarea municipal, Intendencia y Asesoría Técnica pueden activar el interruptor:  
  `★ PRIORITARIO PARA INTENDENCIA`.
- Esta acción destaca automáticamente la tarea en la parte superior del tablero y en la **Sección 3 del Informe Oficial**, e impone el candado de validación obligatoria.

#### Paso 3: Circuito de Auditoría y Validación de Tareas
- Cuando una Secretaría pasa una tarea prioritaria al estado **"Para Validar"**, la conducción superior ingresa a la ficha de la tarea y cuenta con el módulo de **Resolución de Validación**:
  1. **Aprobar Finalización:** Si la obra cumple con los pliegos técnicos, certificaciones y recepción provisoria/definitiva, se certifica el cierre y el sistema pasa la tarea a **"Finalizada"**, registrando la firma digital del auditor.
  2. **Rechazar Finalización:** Si faltan tareas pendientes o la documentación contable es incompleta, el auditor selecciona rechazo e ingresa obligatoriamente el motivo técnico. La tarea regresa automáticamente a **"En ejecución"** para que la Secretaría subsane los desvíos.

#### Paso 4: Generación de Informes y Respaldo de Seguridad
- **Informes Ejecutivos Oficiales:** En la sección *Reportes*, pueden emitir el documento PDF de estado de situación con las 5 secciones oficiales consolidadas.
- **Datos y Respaldo:** En el módulo exclusivo de *Datos y Respaldo*, pueden:
  - Descargar la instantánea completa de la base de datos municipal en archivo JSON (`Descargar respaldo JSON`).
  - Importar respaldos anteriores en transacciones atómicas seguras.
  - Exportar la planilla de tareas y la matriz de inversión barrial en CSV.

---

## 5. Reglas de Negocio y Circuitos Blindados

### 5.1. Regla Contable Presupuestaria
El sistema verifica en todo momento la consistencia lógica de los importes ingresados:
$$\text{Monto Pagado} \le \text{Monto Devengado} \le \text{Monto Contractual Actualizado (MCA)}$$
- Si un operador intenta cargar un monto pagado superior al devengado, el sistema bloquea el guardado y emite una alerta contable.

### 5.2. Regla Territorial Anti-Duplicación
- Todo el presupuesto de una tarea se computa **únicamente en su Barrio Principal**.
- Si una obra vial o red de agua atraviesa múltiples barrios, estos se vinculan en el campo *"Barrios adicionales"* solo con propósitos de georreferenciación, impidiendo que el dinero se sume dos o más veces en el presupuesto municipal.

### 5.3. Auditoría Automática Inmutable (`AuditLog`)
Toda modificación sobre campos críticos (cambios de estado, alteraciones presupuestarias, fechas límites, responsables o archivado) es registrada de forma transparente e irreversible en la base de datos, almacenando:
- Fecha y hora exacta del movimiento.
- Usuario que realizó la acción.
- Campo modificado, valor anterior y valor nuevo.


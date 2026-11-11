# 09 - Registro de Pruebas de Usuario y Modificaciones

Documento de seguimiento para anotar observaciones, ajustes visuales o cambios funcionales detectados durante las pruebas operativas en el entorno local.

---

## 1. Estado Inicial del Entorno de Pruebas
- **Base de datos:** `tablero_gestion` (MySQL / MariaDB en XAMPP).
- **Datos iniciales:** Catálogo de 13 barrios y 6 secretarías cargado; tareas operativas en 0.
- **Usuarios disponibles para pruebas:**
  - `intendente` (Rol: Intendencia) — `Malagueno2026!`
  - `asesor.tecnico` (Rol: Asesoría Técnica) — `Malagueno2026!`
  - `secretario.obras` (Rol: Secretaría de Obras) — `Malagueno2026!`
  - `secretaria.hacienda` (Rol: Secretaría de Hacienda) — `Malagueno2026!`

---

## 2. Flujo de Casos de Prueba

| # | Módulo / Caso de Prueba | Rol Recomendado | Estado | Observaciones / Modificaciones Detectadas |
| :-: | :--- | :--- | :-: | :--- |
| **01** | Inicio de sesión y navegación en Sidebar | `intendente` | Pendiente | |
| **02** | Creación de Tarea Simple (Básica) | `secretario.obras` | Pendiente | |
| **03** | Creación de Tarea con Presupuesto y Barrio | `secretario.obras` | Pendiente | |
| **04** | Carga de Seguimiento (Comentario y Foto/PDF) | `secretario.obras` | Pendiente | |
| **05** | Marcador Prioritario para Intendencia | `intendente` | Pendiente | |
| **06** | Solicitud de Validación (Pase a PARA_VALIDAR)| `secretario.obras` | Pendiente | |
| **07** | Aprobación / Rechazo de Validación | `intendente` | Pendiente | |
| **08** | Verificación de Semáforos en Dashboard | `intendente` | Pendiente | |
| **09** | Filtros y Búsqueda en Tareas | Cualquier rol | Pendiente | |
| **10** | Generación de Reportes e Impresión PDF | `intendente` | Pendiente | |

---

## 3. Bitácora de Modificaciones Solicitadas
*(Se registrarán aquí los pedidos de cambio detallados con su fecha y resolución técnica).*

### [Fecha: 2026-11-04]
- **Observación 1 (Sidebar - Doble Foco Activo):** Al crear o editar tareas, el enlace de *"Áreas municipales"* también se marcaba como activo.
  - *Causa:* La condición `{% if 'area' in request.resolver_match.url_name %}` coincidía accidentalmente con `'tarea'` porque contiene la subcadena `'area'`.
  - *Solución:* Se especificaron las URLs exactas (`request.resolver_match.url_name in 'areas_lista area_detalle'`) en `templates/includes/sidebar_panel.html`.
- **Observación 2 (Formulario - Cálculos en Tiempo Real):** Los cálculos de MCA, porcentaje financiero y estimación comunitaria no se actualizaban en vivo mientras el usuario escribía.
  - *Causa:* Desconexión por ID del formulario (`taskForm` vs `formTarea`).
  - *Solución:* Se programó `validaciones_form.js` con cálculo reactivo inmediato de MCA (Adjudicado + Redeterminaciones + Ampliaciones), Avance Financiero `(Pagado / MCA) * 100`, Devengado Pendiente y conversor automático de Viviendas a Habitantes directos (× 3,5).
  - *Prevención Contable:* Se incorporó un aviso visual en vivo y botón de ajuste automático si el Monto Pagado supera al Devengado (`Pagado <= Devengado <= MCA`).
- **Observación 3 (Listado de Tareas - Tarjeta de Filtrado y Checkboxes Gigantes):** En la pantalla de tareas, los checkboxes de *"Prioritario Intendencia"* y *"Solo vencidas"* aparecían como cajas vacías gigantescas de 44px de alto y la disposición de los filtros estaba desalineada.
  - *Causa:* La regla global `.filters input` en `gestion_panel.css` forzaba `width: 100%`, `min-height: 44px` y padding a todos los `input`, incluyendo los checkbox.
  - *Solución:* 
    1. Se restringieron los selectores en `static/css/pages/gestion_panel.css` mediante `:not([type="checkbox"]):not([type="radio"])`.
    2. Se rediseñó la tarjeta de filtros (`.filter-card`) con una fila superior en cuadrícula limpia (buscador con lupa integrada y selects con anchos armoniosos) y una fila inferior separada con chips conmutadores estilizados para *"Prioritario Intendencia"* (dorado) y *"Solo vencidas"* (alerta roja), junto con los botones de acción *"Limpiar"* y *"Filtrar"* alineados a la derecha.
- **Observación 4 (Formularios y Paneles - Alineación y Color Verde de Iconos en `.panel h3`):** En los paneles y formularios, los títulos `<h3>` separaban el icono a la izquierda y el texto a la derecha debido a `justify-content: space-between`, y los iconos tenían colores dispares o azules.
  - *Causa:* `.panel h3` aplicaba `justify-content: space-between` en lugar de agrupar el icono y texto a la izquierda, y no unificaba el color institucional en los iconos.
  - *Solución:* En `static/css/pages/panel_layout.css`, se configuró `justify-content: flex-start; gap: 12px;` y se definió que todos los iconos dentro de `.panel h3` adopten el verde municipal oficial (`#0C3613`), enviando a la derecha solo los botones o pills secundarios (`margin-left: auto;`). Se retiraron además los estilos inline residuales en las plantillas de formulario (`tarea_form.html`, `seguimiento_modal.html`, etc.).
- **Observación 5 (Módulo de Seguimiento y Bitácora - Formulario Unificado, Normalización y Estructura por Tarea/Fecha):** Se reemplazó el esquema previo de dos formularios separados por una interfaz unificada idéntica a las especificaciones y capturas del sistema Malagueño 4.0.
  - *Estructura visual:* 4 tarjetas continuas: 1. Avances declarados con barras de progreso (general, físico y financiero) y acceso a edición; 2. Seguimiento de novedades con evidencias adjuntas; 3. Formulario de nueva actualización con comentario, firmante, selección múltiple de archivos y un solo botón *"Publicar actualización"*; 4. Línea de tiempo histórica vertical.
  - *Normalización y Almacenamiento:* Se implementó la función `ruta_archivo_seguimiento` que almacena en `media/seguimiento/<nombre_tarea_normalizado>/%Y/%m/<archivo_normalizado.ext>`, convirtiendo a minúsculas, reemplazando espacios por `_` y eliminando acentos y caracteres especiales tanto en el nombre de la subcarpeta como en cada archivo adjunto.
- **Observación 6 (Barras de Progreso - Desborde al 100% por Formato Regional de Coma Decimal):** En `seguimiento_modal.html` (y en el dashboard), las barras de porcentaje de avance (30%) se mostraban llenas al 100%.
  - *Causa:* Debido a la localización regional en español (`USE_L10N=True`), Django formateaba los valores numéricos como `30,00` (con coma). En CSS, `width: 30,00%;` es una sintaxis no válida que los navegadores descartan, haciendo que el `div` se expanda por defecto al 100% del contenedor padre.
  - *Solución:* Se cargó `{% load l10n %}` y se aplicó el filtro `|unlocalize` (`width: {{ valor|unlocalize }}%;`), asegurando que siempre se genere con punto decimal (`30.00%`), permitiendo que el navegador renderice la proporción exacta sobre el 100%. Se extendió la solución a `panel_ejecutivo.html`, `area_detalle.html` y `reportes.html`.
- **Observación 7 (Catálogo Oficial de Áreas Municipales):** Se reemplazó el listado genérico inicial por las 14 áreas y dependencias oficiales solicitadas para el organigrama de Malagueño 4.0:
  1. Intendencia
  2. Gobierno, Seguridad Ciudadana y Auditoría Interna
  3. Desarrollo Económico y Análisis Financiero
  4. Prevención y Atención de Salud Comunitaria
  5. Desarrollo Urbano, Obras y Servicios Públicos
  6. Desarrollo Humano y Formación para el Empleo
  7. Coordinación
  8. Direccion de Secretaria Privada y Participacion Ciudadana
  9. Asesoría Económico Financiera
  10. Asesoría Letrada y Procuración
  11. Instituto de Planificación Municipal
  12. Asesoría Técnica
  13. Honorable Concejo Deliberante (HCD)
  14. Honorable Tribunal de Cuentas (HTC)
- **Observación 8 (Seguridad por Rol y Ámbito de Creación de Tareas):** 
  - *Regla:* Una Secretaría (`rol=SECRETARIA`) únicamente puede crear y gestionar tareas de su propia área. No debe tener autorización para crear tareas a nombre de otras secretarías.
  - *Solución:*
    1. Si el usuario tiene rol `SECRETARIA`, el campo `area_principal` se restringe exclusivamente a su propia secretaría (`Area.objects.filter(pk=area_usuario.pk)`), y el selector de *Dirección ejecutora* a las dependencias de su área.
    2. Se implementó validación estricta en el método `clean_area_principal` del backend para rechazar peticiones POST que intenten asignar otra secretaría.
    3. Los roles de supervisión general (`INTENDENCIA` y `ASESORIA`) son los únicos habilitados para elegir cualquiera de las 14 secretarías.

- **Observación 11 (Alerta de Referencia Catastral y Formulario Dinámico por Modalidad de Beneficiarios):**
  - *Mensaje de Alerta en Rojo al Seleccionar Barrio:* Se diseñó un panel de advertencia institucional con borde rojo (`#dc2626`) y tipografía destacada que se dispara de inmediato al seleccionar cualquier barrio principal en `id_barrio_principal`:
    `ATENCIÓN — DATO DE REFERENCIA: <Barrio> tiene <X> viviendas edificadas según el relevamiento municipal. Esto NO significa que todas estén beneficiadas por esta tarea. Ingresá únicamente las viviendas efectivamente alcanzadas de forma directa o indirecta. Si es una capacitación, reparación puntual u otra actividad sin viviendas beneficiadas, dejá ambos campos en 0. No se calculan beneficiarios automáticamente por elegir un barrio.`
  - *Formularios Dinámicos según Modalidad:*
    1. **Por viviendas alcanzadas (estimación de habitantes × 3,5):**
       - Campos de entrada: *Viviendas beneficiadas directamente* y *Viviendas beneficiadas indirectamente*.
       - Campos de cálculo en vivo: *Habitantes beneficiados directamente (× 3,5)* y *Habitantes beneficiados indirectamente (× 3,5)* (actualizados automáticamente con factor de 3.5 redondeado a enteros).
       - Texto de ayuda y advertencia inferior institucional.
    2. **Por personas individuales (capacitaciones, salud, programas sociales):**
       - Campos de entrada: *Personas beneficiadas directamente* (placeholder *"Ej.: 35 asistentes"*) y *Personas beneficiadas indirectamente* (placeholder *"0"*).
       - Nota aclaratoria de unicidad y no conversión en viviendas.
    3. **Sin beneficiarios cuantificados por el momento:**
       - Oculta los campos numéricos y exhibe el texto informativo: *"Esta tarea todavía no tiene una cantidad de beneficiarios informada."*
  - *Modelo y Migraciones:* Se crearon las migraciones `0005` y `0006` en `Tarea` incorporando `viviendas_directas`, `viviendas_indirectas`, `personas_directas` y `personas_indirectas` con retrocompatibilidad plena sobre `cantidad_beneficiarios_input` y suite de 9 tests aprobada.

- **Observación 12 (Campos Financieros y Porcentuales Opcionales):**
  - *Causa:* Los campos decimales de presupuesto y porcentajes (`presupuesto_oficial`, `monto_adjudicado`, `redeterminaciones`, `ampliaciones`, `monto_devengado`, `monto_pagado`, `pagos_en_tramite`, `porcentaje_general`, `porcentaje_fisico`) tenían valor por defecto `0.00` pero carecían de `blank=True` en el modelo, provocando que Django los tratara como requeridos por defecto en el formulario e impidiera el guardado si se dejaban vacíos.
  - *Solución:* Se agregó `blank=True` en `gestion/models.py` (migración `0007_alter_tarea_ampliaciones_and_more.py`), se configuró explícitamente `required=False` en `gestion/forms.py` y se normalizó la limpieza para que cualquier campo decimal vacío se guarde automáticamente con `0.00`, permitiendo guardar tareas sin exigir montos presupuestarios en actividades o proyectos que no lo requieran.

- **Observación 13 (Blindaje de Circuito de Validación Superior para Tareas Prioritarias):**
  - *Requerimiento del documento:* Las Secretarías pueden finalizar sus tareas ordinarias, pero las tareas con prioridad de Intendencia (`prioritario_intendencia=True`) requieren validación y cierre exclusivo por parte de Intendencia / Asesoría Técnica.
  - *Blindaje implementado:*
    1. Si un usuario con rol `SECRETARIA` abre una tarea prioritaria para Intendencia, el selector de *Estado actual* excluye automáticamente la opción `Finalizada`.
    2. Debajo del selector se despliega el aviso institucional: *"★ Tarea Prioritaria para Intendencia: Al concluir los trabajos, seleccione 'Para Validar' para que Intendencia audite y certifique su finalización formal."*
    3. Validación estricta en el método `clean()` de `TareaForm` que rechaza cualquier petición POST de una Secretaría que intente forzar el estado `FINALIZADA` en tareas prioritarias.
    4. Se incorporó prueba unitaria automatizada `test_secretaria_no_puede_finalizar_tarea_prioritaria` alcanzando 10 tests aprobados (`OK`).

- **Observación 14 (Rediseño Pixel-Perfect del Informe Ejecutivo PDF / Estado de Situación):**
  - *Estructura oficial de 5 secciones implementada exactamente:*
    1. **Encabezado Institucional:** Escudo/logo municipal, título MALAGUEÑO 4.0, fecha/hora exacta y alcance dinámico (General o Secretaría).
    2. **4 Cajas Superiores de Métricas:** Tareas, Finalizados, En ejecución y Vencidos en fila única.
    3. **Sección 1 (Situación general):** Línea financiera (MCA, Comprometido, Devengado, Pagado, Pagos en trámite) y barra segmentada apilada continua con leyenda de colores y porcentajes.
    4. **Sección 2 (Semáforo y estado por área):** Tabla comparativa de las 14 secretarías con punto de semáforo (`Sin tareas`, `Rojo · vencidas`, `Amarillo · atención`, `Al día`), tareas totales, finalizados, vencidos y barra fina de avance.
    5. **Sección 3 (Cinco temas prioritarios):** Tareas abiertas ordenadas por prioridad de Intendencia, prioridad operativa y fecha límite.
    6. **Sección 4 (Cinco próximos a vencer):** Tareas abiertas ordenadas por cercanía a la fecha límite.
    7. **Sección 5 (Inversión e impacto por barrio):** Matriz barrial con Monto MCA, Pagado, y desglose de beneficiarios en 4 columnas: *Viviendas directas*, *Viviendas indirectas*, *Personas directas* y *Personas indirectas*.

- **Observación 15 (Retiro de la Denominación de Versión "4.0"):**
  - Se eliminaron todas las referencias a la versión "4.0" en los títulos institucionales, pantallas de acceso, encabezados de reporte, pies de página y plantillas del sistema, unificando la identidad sobria e institucional bajo la denominación **MALAGUEÑO** y **Municipalidad de Malagueño**.

- **Observación 16 (Componente Oficial de Respaldo de Datos y Limpieza de Sidebar):**
  - *Retiro de Panel Django Admin:* En `templates/includes/sidebar_panel.html` se quitó el enlace a Django Admin para mantener el menú limpio y enfocado exclusivamente en las herramientas operativas de gestión.
  - *Tarjeta Oficial de Respaldo de Datos:* Se rediseñó `gestion/templates/gestion/datos_respaldo.html` con los 4 botones exactos:
    1. **Descargar respaldo JSON:** Descarga de instantánea completa del sistema.
    2. **Importar respaldo JSON:** Selección y restauración inmediata en transacción atómica.
    3. **Exportar tareas CSV:** Generación de planilla completa de intervenciones en UTF-8-SIG para Excel.
    4. **Exportar inversión por barrio CSV:** Nueva vista `ExportarBarriosCSVView` (`/reportes/exportar/barrios/csv/`) que exporta la matriz completa de los 31 barrios oficiales con tipo de urbanización, viviendas, población, tareas asociadas, montos MCA, montos pagados y cómputo de beneficiarios directos e indirectos.

- **Observación 17 (Identidad Visual Verde Municipal, Rediseño de Login, Tarjeta de Usuario y Menú Hamburguesa Móvil):**
  - *Paleta Verde en Respaldo de Datos:* En `gestion/templates/gestion/datos_respaldo.html`, se actualizó el botón primario *Descargar respaldo JSON* a verde institucional (`#338c33` con hover `#276e27`) y los botones secundarios *Importar respaldo JSON*, *Exportar tareas CSV* y *Exportar inversión por barrio CSV* adoptaron bordes, textos y acentos con hover verde institucional (`#338c33` y fondo `#f4faf4`), unificando la identidad visual.
  - *Pantalla de Inicio de Sesión (Login Limpio y Blanco):* En `gestion/templates/gestion/login.html`, se retiró el fondo degradado oscuro reemplazándolo por fondo blanco puro (`#ffffff`) con tarjeta con sutil borde gris (`#e2e8f0`) y sombra suave. Los campos de texto (*Usuario municipal* y *Contraseña*) cuentan con estados `:hover` y `:focus` con borde verde `#338c33` y resplandor `rgba(51, 140, 51, 0.22)`, y el botón de ingreso se consolidó en verde institucional.
  - *Optimización de Tarjeta de Usuario en Sidebar:* En `templates/includes/sidebar_panel.html` y `static/css/pages/panel_layout.css`, se jerarquizó la tarjeta `.sidebar-user-info` con un avatar circular con icono institucional, nombre legible destacado, badge de rol con fondo verde suave y borde esmeralda (`#8bf29c`), indicador de dependencia/secretaría con icono `fa-building` y botón de cierre de sesión estilizado e integrado.
  - *Menú Hamburguesa para Dispositivos Móviles:* 
    1. En `templates/base/base_panel.html`, se integró la barra superior `.mobile-topbar` visible exclusivamente en pantallas `< 950px` con botón hamburguesa (`#mobileMenuToggle`), isotipo oficial municipal y badge de sesión.
    2. En `templates/includes/sidebar_panel.html`, se incorporó el botón de cierre `#mobileMenuClose` con icono `fa-xmark`.
    3. En `static/css/pages/panel_layout.css`, el `aside` en móviles se comporta como un cajón deslizante off-canvas con animación fluida `transform: translateX(-105%)` a `translateX(0)`, con overlay de fondo desenfocado `.sidebar-backdrop` y cierre automático con botón, clic exterior o tecla Escape.

- **Observación 18 (Gestión y Asignación de Roles de Usuario en Django Admin):**
  - *Integración en Ficha de Usuario:* En `gestion/admin.py` se extendió el modelo `User` de Django (`CustomUserAdmin`) incorporando `PerfilUsuarioInline` (`admin.StackedInline`). Al crear o editar cualquier usuario en `/admin/auth/user/`, el administrador dispone de la sección integrada **"Perfil y Rol Municipal"** para definir:
    1. **Rol Operativo:** `Intendencia`, `Asesoría Técnica` o `Secretaría`.
    2. **Área Asignada:** Selector de las dependencias municipales.
    3. **Dirección Asignada** y **Teléfono de Contacto**.
  - *Visualización y Filtros en la Lista de Usuarios:* La tabla principal de usuarios exhibe el badge de color institucional del rol (`get_rol_badge`), el área asignada (`get_area`), y filtros laterales directos por rol (`perfil__rol`) y área (`perfil__area`).
  - *Edición Rápida en Lote en Perfiles de Usuario:* En `/admin/gestion/perfilusuario/` se configuró `list_editable = ('rol', 'area')`, permitiendo modificar los roles y secretarías directamente en la grilla sin tener que abrir cada ficha individual.
  - *Suite de Pruebas:* Se incorporó la prueba unitaria `test_admin_asignacion_rol_usuario` en `gestion/tests.py`, totalizando **11 tests automatizados aprobados** (`Ran 11 tests, OK`).




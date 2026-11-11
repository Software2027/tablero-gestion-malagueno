# 🎨 06 - Especificaciones de Interfaz y UX-UI
#ui #ux #diseno #ubuntu #estilos #frontend

Guía de diseño visual, sistema de diseño, directrices de usabilidad y especificaciones de componentes frontend para el Tablero de Gestión Municipal.

Vínculos: [[00 - Tablero General (Home)]] | [[01 - Arquitectura y Tecnologías]] | [[05 - Reglas de Negocio y Fórmulas]]

---

## 🏛️ Identidad Visual y Tipografía

### Tipografía Oficial
- **Familia tipográfica:** `'Ubuntu', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Importación Webfont:** Google Fonts (`weights: 300, 400, 500, 700`)
- **Justificación:** Alta legibilidad en pantallas gubernamentales, estilo contemporáneo e institucional.

### Paleta Cromática Institucional

| Rol del Color | Valor Hex | Muestra | Uso en la Interfaz |
| :--- | :---: | :---: | :--- |
| **Primario Institucional** | `#338c33` | 🟢 | Barras superiores, botones principales, acentos de marca, bordes activos |
| **Primario Oscuro (Hover)** | `#276f27` | 🌲 | Estados hover y active en botones primarios |
| **Primario Claro (Superficie)** | `#eaf4ea` | 🍃 | Fondos de tarjetas destacadas, badges de éxito, selección activa |
| **Fondo General (Body)** | `#f8fafc` | ⚪ | Fondo general del panel y vistas |
| **Fondo de Tarjetas / Modales** | `#ffffff` | ⬜ | Contenedores, tablas y ventanas emergentes |
| **Texto Principal** | `#1e293b` | ⚫ | Encabezados y texto informativo de alto contraste |
| **Texto Secundario** | `#64748b` | 🔘 | Fechas, subtítulos, etiquetas y metadatos |
| **Bordes y Divisores** | `#e2e8f0` | ◽ | Líneas de división de tablas y bordes de inputs |

### Colores Semánticos y Semáforos

| Estado | Color Hex | Color Fondo Badge | Aplicación |
| :--- | :---: | :---: | :--- |
| **Rojo (Crítico / Vencida)** | `#dc2626` | `#fee2e2` | Tareas vencidas, errores de validación, alertas |
| **Amarillo (Atención / Bloqueada)** | `#d97706` | `#fef3c7` | Tareas bloqueadas, vencimientos próximos (≤ 7 días) |
| **Verde (Al día / Finalizada)** | `#338c33` | `#eaf4ea` | Tareas en curso óptimo, tareas finalizadas |
| **Azul (Para Validar / Info)** | `#2563eb` | `#dbeafe` | Tareas elevadas para revisión jerárquica |
| **Gris (Pendiente / Neutro)** | `#64748b` | `#f1f5f9` | Tareas sin inicio, áreas sin proyectos asignados |

---

## 💻 Variables CSS Globales (`panel_layout.css`)

```css
:root {
  /* Tipografía */
  --font-family-base: 'Ubuntu', -apple-system, BlinkMacSystemFont, sans-serif;
  
  /* Paleta Institucional Malagueño */
  --color-primary: #338c33;
  --color-primary-hover: #276f27;
  --color-primary-light: #eaf4ea;
  --color-primary-border: #80c480;

  /* Neutros y Superficies */
  --color-bg-body: #f8fafc;
  --color-bg-card: #ffffff;
  --color-border: #e2e8f0;
  --color-text-main: #1e293b;
  --color-text-muted: #64748b;

  /* Estados y Semáforos */
  --color-status-red: #dc2626;
  --color-status-red-bg: #fee2e2;
  --color-status-yellow: #d97706;
  --color-status-yellow-bg: #fef3c7;
  --color-status-green: #338c33;
  --color-status-green-bg: #eaf4ea;
  --color-status-blue: #2563eb;
  --color-status-blue-bg: #dbeafe;
  --color-status-gray: #64748b;
  --color-status-gray-bg: #f1f5f9;

  /* Sombras y Elevación */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
}
```

---

## 📐 Vistas y Componentes Principales

### 1. Panel Ejecutivo (Dashboard)
- **Bloque Superior de KPIs:** Tarjetas estadísticas con icono, cifra grande y comparador porcentual: Total de Tareas, En Ejecución, Vencidas, Pendientes de Validación.
- **Gráficos de Distribución:** Gráfico de dona de estados y gráfico de barras por área ejecutora.
- **Consolidado Financiero:** Barra de progreso triple (Monto Contratado vs. Devengado vs. Pagado).
- **Semáforo por Secretaría:** Grilla interactiva con tarjetas por secretaría con su color indicador y acceso al detalle.

### 2. Tabla Dinámica de Tareas
- **Barra de Herramientas:** Buscador en tiempo real por texto/responsable, selector múltiple de área, filtro rápido de estado (incluyendo el switch "Solo Vencidas"), toggle "Prioritarias Intendencia".
- **Columnas:** Estado / Semáforo, Título y Barrio, Área Responsable, Avances (% Físico / % Financiero), Monto Pagado / MCA, Fecha Límite, Acciones Rápidas (Seguimiento, Editar, Archivar).

### 3. Modal de Formulario de Tarea
- Estructurado en bloques visuales claros:
  1. *Datos Generales:* Título, Área Principal, Dirección, Responsable Operativo, Prioridad, Switch "Prioritario Intendencia".
  2. *Articulación Interáreas:* Selector de secretarías participantes.
  3. *Cronograma y Avance:* Fecha límite, Estado, barras de % General, % Físico, % Financiero.
  4. *Cuadro Económico:* Presupuesto Oficial, Adjudicado, Redeterminaciones, Ampliaciones, Devengado, Pagado, En Trámite.
  5. *Territorio:* Barrio Principal, Barrios Adicionales, Modalidad Beneficiarios y Cantidad, Ubicación Google Maps.
  6. *Observaciones:* Obligatorio si el estado es `BLOQUEADA`.

### 4. Modal de Seguimiento Multimedia y Novedades
- **Línea de Tiempo (Timeline):** Hitos cronológicos con autor, fecha/hora y avatar.
- **Zona de Carga (Drag & Drop):** Validación inmediata en cliente (`validaciones_form.js`) de archivos hasta 40MB (fotos JPG/PNG/WebP, videos MP4, documentos PDF).
- **Control de Requerimientos:** Casilla "Requiere respuesta" que añade un badge de aviso hasta que otro usuario marque como "Resuelto".


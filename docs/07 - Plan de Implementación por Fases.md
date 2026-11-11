# 🚀 07 - Plan de Implementación por Fases
#roadmap #planificacion #fases #implementacion #hitos

Cronograma paso a paso para el desarrollo, pruebas e implementación gradual del Tablero de Gestión Municipal de Malagueño 4.0.

Vínculos: [[00 - Tablero General (Home)]] | [[01 - Arquitectura y Tecnologías]] | [[02 - Modelo de Datos y Entidades]]

---

## 🧭 Resumen de Fases

```mermaid
flowchart LR
    Fase1[Fase 1: Base y Configuración] --> Fase2[Fase 2: Modelos y Base de Datos]
    Fase2 --> Fase3[Fase 3: Lógica y Reglas de Negocio]
    Fase3 --> Fase4[Fase 4: Frontend y UX/UI]
    Fase4 --> Fase5[Fase 5: Permisos y Auditoría]
    Fase5 --> Fase6[Fase 6: Reportes y Respaldos]
    Fase6 --> Fase7[Fase 7: QA y Despliegue]
```

---

## 📌 Detalle Paso a Paso de las Fases

### 🔹 Fase 1: Entorno, Andamiaje y Configuración Inicial (COMPLETADA)
- [x] Creación del entorno virtual `venv/` e instalación de dependencias aisladas.
- [x] Creación de `requirements.txt` con versiones exactas (`Django>=4.2.14,<5.2`, `PyMySQL>=1.1.2`, `Pillow>=10.4.0`, `reportlab`, `xhtml2pdf`).
- [x] Configuración del proyecto Django `core/` y app `gestion/`.
- [x] Configuración de `core/__init__.py` para inyección de PyMySQL (`pymysql.install_as_MySQLdb()`).
- [x] Ajuste de `settings.py`: conexión MySQL, directorios `STATICFILES_DIRS`, `MEDIA_ROOT`, `MEDIA_URL`, `TEMPLATES`, zonas horarias en español (`America/Argentina/Cordoba`, `es-ar`), subida de archivos de 50MB.
- [x] Creación de `.gitignore` completo.
- [x] Creación del sistema de diseño inicial en `static/css/` (Tipografía **Ubuntu**, Color primario `#338c33`).
- **Hito de Validación:** `.\venv\Scripts\python.exe manage.py check` ejecutado con éxito sin incidencias (0 errores).

---

### 🔹 Fase 2: Modelado ORM y Migraciones (COMPLETADA)
- [x] Implementación de modelos en `gestion/models.py`:
  - `Area` y `Direccion`.
  - `PerfilUsuario` con relación `OneToOneField(User)` y roles `INTENDENCIA`, `ASESORIA`, `SECRETARIA`.
  - `Barrio` con viviendas y cálculo de población.
  - `Tarea` con todos los campos (generales, interáreas, avances tripartitos, finanzas, territorio, observaciones, soft delete, validaciones de negocio).
  - `ComentarioActualizacion` y `ArchivoAdjunto` (con límite de 40MB).
  - `AuditLog` inmutable para trazabilidad obligatoria.
- [x] Generación y ejecución de migraciones iniciales (`makemigrations` y `migrate`).
- [x] Creación del comando de administración `seed_datos_iniciales.py` con 13 barrios de Malagueño, 6 secretarías, 16 direcciones y usuarios con perfiles operativos.
- [x] Configuración del panel de administración `gestion/admin.py` con inlines, badges de colores, barras de progreso y filtros avanzados.
- **Hito de Validación:** Base de datos poblada con catálogo inicial y verificada mediante consultas ORM sin errores.

---

### 🔹 Fase 3: Reglas de Negocio, Validaciones y Utilidades (COMPLETADA)
- [x] Desarrollo de `gestion/utils.py`:
  - Cálculo de Monto Contractual Actualizado ($MCA$).
  - Cálculo de Devengado Pendiente y Avance Financiero %.
  - Algoritmo del semáforo de salud institucional (Rojo, Amarillo, Verde, Gris).
  - Cálculo dinámico de tareas vencidas y tareas próximas a vencer.
  - Consolidación de impacto territorial (inversión por barrio principal y beneficiarios calculados).
- [x] Formularios en `gestion/forms.py` con validaciones de negocio:
  - `TareaForm`: Justificación obligatoria si `estado == 'BLOQUEADA'`, restricción financiera ($Pagado \le Devengado \le MCA$), adaptación dinámica por rol (Secretarías no pueden marcar prioritario intendencia ni editar tareas de otras áreas).
  - `ValidacionResolucionForm`: Aprobación o rechazo con motivo mandatorio.
  - `ComentarioForm` y `ArchivoAdjuntoForm` (validación estricta de 40MB).
- [x] Creación de `core/settings_test.py` y suite de pruebas unitarias en `gestion/tests.py`.
- **Hito de Validación:** 4/4 pruebas unitarias de fórmulas y validaciones ejecutadas y aprobadas (OK).

---

### 🔹 Fase 4: Frontend, Sistema de Diseño e Identidad Visual (COMPLETADA)
- [x] Configuración de CSS global en `static/css/pages/panel_layout.css`, `gestion_panel.css`, `gestion_modal.css`, `header_gestion.css` y `footer_gestion.css`:
  - Tipografía oficial **Ubuntu** (Google Fonts).
  - Color corporativo principal `#338c33` y paleta complementaria (superficies, bordes y semáforos).
- [x] Estructuración de plantillas base y navegación:
  - `templates/base/base_panel.html`, `templates/headers/header_gestion.html`, `templates/footers/footer_gestion.html`, `templates/includes/sidebar_panel.html`.
- [x] Implementación de pantallas y componentes:
  - `login.html`: Pantalla de acceso corporativa con identidad de Malagueño 4.0.
  - `panel_ejecutivo.html`: KPIs, barra financiera triple, semáforos por secretaría y tareas prioritarias.
  - `tareas_lista.html`: Tabla dinámica con buscador por texto, filtros de área, estado, prioridad, switch "Solo Vencidas", badges y acciones.
  - `tarea_form.html`: Formulario estructurado por bloques con validaciones de negocio en vivo.
  - `areas_lista.html` y `area_detalle.html`: Directorio y fichas de secretarías con balances presupuestarios y tareas propias/interáreas.
  - `seguimiento_modal.html`: Línea de tiempo cronológica, badges de requerimientos y subida de archivos (límite 40MB).
  - `tarea_validar_modal.html`: Resolución de validación (aprobación/rechazo con motivo).
- [x] JavaScript auxiliar: `validaciones_form.js` y `seguimiento_media.js` (control estricto de 40MB).
- **Hito de Validación:** 5/5 pruebas de renderizado, autenticación y vistas ejecutadas y aprobadas (OK).

---

### 🔹 Fase 5: Permisos, Jerarquías y Trazabilidad (COMPLETADA)
- [x] Implementación de señales en `gestion/signals.py`:
  - Receptores `pre_save` y `post_save` para capturar cualquier cambio en los 18 campos clave de `Tarea`.
  - Inserción automática e inmutable en `AuditLog` registrando usuario, timestamp, acción, campo modificado, valor anterior y nuevo.
- [x] Doble capa de seguridad y restricciones por rol en backend (`gestion/views.py`):
  - Filtro estricto de ámbito de consulta (`ScopeTareaQuerysetMixin`).
  - Restricción en `TareaUpdateView`: Secretaría no puede alterar tareas de otra secretaría (403 Forbidden).
  - Bloqueo de solo lectura para tareas en revisión (`PARA_VALIDAR`).
  - Restricción en `TareaValidarView`: Solo Intendente puede aprobar tareas prioritarias de Intendencia (403 Forbidden para otros roles).
  - Soft delete protegido en `TareaArchivarView`.
- **Hito de Validación:** 6/6 pruebas unitarias de auditoría, trazabilidad y restricciones de seguridad ejecutadas y aprobadas (OK).

---

### 🔹 Fase 6: Módulo de Reportes y Respaldo de Datos (COMPLETADA)
- [x] Vista consolidada `reportes.html`:
  - Matriz de ejecución física, financiera y semáforos por Secretaría.
  - Matriz de impacto barrial y cobertura poblacional sin duplicación monetaria.
  - Resumen macrofinanciero de Malagueño 4.0.
- [x] Generador imprimible `reportes_pdf.html`:
  - Maquetación CSS `@media print` optimizada para A4 apaisado con tipografía **Ubuntu** y color `#338c33`.
- [x] Exportaciones dinámicas de datos:
  - Exportación en CSV delimitado con encoding `utf-8-sig` (Excel compatible) en `ExportarCSVView`.
  - Exportación en JSON estructurado en `ExportarJSONView`.
- [x] Módulo `datos_respaldo.html` con control estricto de acceso (exclusivo para Intendencia y Asesoría Técnica):
  - Descarga de instantánea integral de base de datos en JSON.
  - Formulario de restauración e importación atómica con control de integridad.
- **Hito de Validación:** 7/7 pruebas unitarias de reportes, exportaciones (CSV, JSON, PDF) y seguridad de respaldos ejecutadas y aprobadas (OK).

---

### 🔹 Fase 7: Pruebas Integrales, Aseguramiento de Calidad y Puesta a Punto (COMPLETADA)
- [x] Pruebas cruzadas de ciclo de vida completo de una tarea (E2E):
  - Creación (Pendiente) &rarr; Inicio de ejecución &rarr; Carga física/financiera &rarr; Bloqueo con justificación obligatoria &rarr; Pase a "Para Validar" (Modo solo lectura) &rarr; Aprobación final por Intendente &rarr; Tarea Finalizada al 100%.
- [x] Validación de límites de archivos multimedia:
  - Rechazo automático de archivos que superen los 40MB en cliente y servidor.
- [x] Verificación de diseño responsive, tipografía oficial **Ubuntu** y paleta institucional **`#338c33`** en todas las pantallas.
- [x] Verificación de consistencia del catálogo inicial sembrado (`seed_datos_iniciales`).
- [x] Documentación exhaustiva en el vault de Obsidian (`docs/`).
- **Hito de Validación:** 9/9 pruebas integrales y unitarias ejecutadas con éxito (0 fallos, 0 errores) en 11.8 segundos. Sistema completamente operativo.


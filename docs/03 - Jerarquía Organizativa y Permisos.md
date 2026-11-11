# 👥 03 - Jerarquía Organizativa y Permisos
#roles #permisos #rbac #seguridad #intendencia #secretarias

Especificación del modelo de control de acceso basado en roles (RBAC), jerarquías operativas y matriz de atribuciones para la primera etapa del sistema.

Vínculos: [[00 - Tablero General (Home)]] | [[02 - Modelo de Datos y Entidades]] | [[04 - Flujo de Trabajo y Ciclo de Vida de Tareas]]

---

## 🏛️ Estructura de Perfiles

El sistema contempla **tres perfiles de usuario operativos** con credenciales de acceso directo, junto con roles operativos sin cuenta propia y órganos externos.

```
                    ┌─────────────────────────┐
                    │       INTENDENCIA       │ (Control Total y Visibilidad Global)
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    ASESORÍA TÉCNICA     │ (Visibilidad Global, Gestión y Soporte)
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
┌───────────────────────┐                   ┌───────────────────────┐
│     SECRETARÍA A      │                   │     SECRETARÍA B      │ (Ámbito Propio e Interáreas)
└──────────┬────────────┘                   └──────────┬────────────┘
           │                                           │
  [ Resp. Operativos ]                        [ Resp. Operativos ]    (Directores / Personal sin usuario)
```

---

## 📑 Matriz de Permisos

| Acción / Operación | Intendencia | Asesoría Técnica | Secretarías | Directores / Personal |
| :--- | :---: | :---: | :---: | :---: |
| **Tiene usuario de acceso al sistema** | ✅ Sí | ✅ Sí | ✅ Sí | ❌ No (solo asignable como texto/responsable) |
| **Visibilidad de tareas** | 🌐 Todas (Global) | 🌐 Todas (Global) | 🏢 Su área + Interáreas | ❌ Sin acceso |
| **Crear nuevas tareas** | ✅ Sí | ✅ Sí | ✅ Sí (para su área) | ❌ |
| **Editar tareas propias** | ✅ Sí | ✅ Sí | ✅ Sí | ❌ |
| **Editar tareas de otras secretarías** | ✅ Sí | ✅ Sí | ❌ No | ❌ |
| **Reasignar área responsable** | ✅ Sí | ✅ Sí | ❌ No | ❌ |
| **Marcar / Desmarcar "Prioritario Intendencia"** | ✅ Sí | ✅ Sí | ❌ No | ❌ |
| **Finalizar tareas ordinarias** | ✅ Sí | ✅ Sí | ✅ Sí | ❌ |
| **Validar tareas prioritarias de Intendencia** | ✅ Sí (Exclusivo) | ❌ No (Requiere Intendente) | ❌ No | ❌ |
| **Eliminar tareas físicamente** | ❌ Nadie (Soft Delete) | ❌ Nadie (Soft Delete) | ❌ Nadie (Soft Delete) | ❌ |
| **Archivar tareas (Soft Delete)** | ✅ Sí | ✅ Sí | ✅ Sí (de su área) | ❌ |
| **Exportar reportes (CSV / JSON / PDF)** | ✅ Sí | ✅ Sí | ✅ Sí (alcance su área) | ❌ |
| **Importar respaldos de base de datos** | ✅ Sí | ✅ Sí | ❌ No | ❌ |

---

## 🔍 Detalle por Perfil

### 1. Intendencia
- **Alcance:** Máxima autoridad municipal. Visibilidad irrestricta de todas las Secretarías y Direcciones.
- **Capacidades Especiales:**
  - Puede fijar el indicador de "Prioritario para Intendencia".
  - Autoridad final de aprobación para tareas prioritarias elevadas para validación.
  - Importación y restauración de datos.

### 2. Asesoría Técnica
- **Alcance:** Coordinación estratégica transversal y soporte de gestión.
- **Capacidades Especiales:**
  - Visibilidad de todos los registros y métricas de todas las áreas.
  - Puede validar tareas por delegación directa de Intendencia (salvo las marcadas como prioritarias para el Intendente).
  - Marcado de prioridades y soporte a Secretarías.

### 3. Secretarías
- **Alcance:** Departamentos ejecutivos (ej. Secretaría de Obras Públicas, Secretaría de Hacienda, Secretaría de Salud, etc.).
- **Reglas de Acceso:**
  - Solo visualizan y gestionan tareas donde su área sea la **Área Principal** o figure en **Áreas Intervinientes**.
  - No pueden alterar ni consultar tareas confidenciales o exclusivas de otras secretarías ajenas.
  - Tienen autonomía para crear tareas y cargar responsables operativos.

### 4. Directores y Personal Administrativo
- En esta etapa inicial **NO** cuentan con credenciales de inicio de sesión.
- Se registran en el campo de texto descriptivo `responsable_operativo` de la tarea o vinculados a la `Direccion` correspondiente.

### 5. Organismos Independientes (HCD y HTC)
- **Honorable Concejo Deliberante (HCD)** y **Honorable Tribunal de Cuentas (HTC)**:
  - No poseen usuario ni acceso a la plataforma.
  - El sistema permite documentar tareas de articulación institucional donde intervengan, pero sin darles acceso a la plataforma.

---

## 🛡️ Doble Capa de Seguridad

1. **Frontend (Capa de Presentación):** Ocultamiento condicional de botones, formularios de carga y enlaces de validación/importación según el rol en sesión.
2. **Backend (Capa de Control - Django):** Mixins personalizados (`IntendenciaRequiredMixin`, `AsesoriaOrIntendenciaMixin`, `SecretariaScopeQuerysetMixin`) y validaciones en métodos `save()` y `clean()` que impiden el bypass de seguridad vía manipulación de requests HTTP.


# 🏛️ Tablero de Gestión Municipal - Malagueño 4.0
#tablero-gestion #malagueño #arquitectura #indice

Bienvenido a la base de conocimiento y documentación técnica del **Tablero de Gestión Municipal de Malagueño 4.0**. Esta documentación está organizada para ser consultada y navegada mediante [[Obsidian]].

---

## 🎯 Visión General del Proyecto

El sistema es una plataforma web centralizada para el control, monitoreo y gestión pública de las distintas Secretarías y Direcciones de la Municipalidad de Malagueño. Permite realizar seguimiento tripartito de las tareas (**general, físico y financiero**), medir el impacto territorial en barrios y coordinar transversalmente las acciones de gobierno.

> [!NOTE] Identidad Visual Clave
> - **Tipografía Institucional:** `Ubuntu`, sans-serif.
> - **Color Primario de Marca:** `#338c33` (Verde Institucional Malagueño).
> - **Variantes y Acentos:** Paleta complementaria para estados de semáforo (Verde, Amarillo, Rojo, Gris) y paneles contrastados.

---

## 🗺️ Mapa de Contenidos (MOC)

Explora la documentación estructurada en los siguientes módulos:

1. **[[01 - Arquitectura y Tecnologías]]**:
   Stack base (Django, MySQL, PyMySQL), arquitectura de directorios, configuración de core y app `gestion`.

2. **[[02 - Modelo de Datos y Entidades]]**:
   Diseño de la base de datos relacional, modelos ORM (`Area`, `Direccion`, `PerfilUsuario`, `Barrio`, `Tarea`, `ComentarioActualizacion`, `ArchivoAdjunto`, `AuditLog`), relaciones y tipos.

3. **[[03 - Jerarquía Organizativa y Permisos]]**:
   Matriz de control de acceso basada en roles (RBAC): Intendencia, Asesoría Técnica, Secretarías, Directores/Operativos y tratamiento de HCD/HTC.

4. **[[04 - Flujo de Trabajo y Ciclo de Vida de Tareas]]**:
   Estados (`Pendiente`, `En Ejecución`, `Bloqueada`, `Para Validar`, `Finalizada`), cálculo de `Vencida`, reglas de validación y rechazo.

5. **[[05 - Reglas de Negocio y Fórmulas]]**:
   Cálculo financiero (Monto contractual actualizado, devengado, pagos), impacto territorial (barrio principal y secundarios, beneficiarios personas/viviendas) y motor del semáforo de salud.

6. **[[06 - Especificaciones de Interfaz y UX-UI]]**:
   Diseño visual, tipografía **Ubuntu**, paleta `#338c33`, componentes modales, tablas dinámicas y layout responsive.

7. **[[07 - Plan de Implementación por Fases]]**:
   Cronograma y plan de ejecución paso a paso con hitos verificables para el desarrollo del sistema.

---

## 📌 Enlaces Rápidos y Metadatos

- **Framework Backend:** Django `>= 4.2.14, < 5.2`
- **Motor de Base de Datos:** MySQL `8.0+`
- **Conector:** `PyMySQL >= 1.1.2`
- **Librería de Multimedia:** `Pillow >= 10.4.0`
- **Auditoría:** Trazabilidad obligatoria sin borrado físico (Soft Delete + `AuditLog`)


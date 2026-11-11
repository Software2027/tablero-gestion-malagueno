# ⚙️ 01 - Arquitectura y Tecnologías
#arquitectura #tecnologia #django #mysql #directorio

Documento técnico que detalla la arquitectura de software, el stack tecnológico seleccionado y la organización del árbol de directorios del proyecto.

Vínculos: [[00 - Tablero General (Home)]] | [[02 - Modelo de Datos y Entidades]] | [[07 - Plan de Implementación por Fases]]

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología / Versión | Propósito / Justificación |
| :--- | :--- | :--- |
| **Lenguaje** | Python 3.10+ | Lenguaje base para backend y procesamiento de datos |
| **Framework Web** | Django (`>= 4.2.14, < 5.2`) | Framework robusto con ORM integrado, seguridad nativa y sistema de plantillas |
| **Base de Datos** | MySQL 8.0+ | Motor relacional estándar corporativo municipal |
| **Conector DB** | PyMySQL (`>= 1.1.2`) | Conector de MySQL para Python (inyectado como MySQLdb en `core/__init__.py`) |
| **Procesamiento Gráfico** | Pillow (`>= 10.4.0`) | Manejo y validación de imágenes de evidencia adjunta |
| **Frontend Base** | HTML5, CSS3 moderno, Vanilla JS | Ligero, sin frameworks pesados, carga instantánea |
| **Tipografía** | **Ubuntu** (Google Fonts) | Fuente institucional legible, moderna y corporativa |
| **Color Primario** | `#338c33` | Identidad cromática institucional (Verde Malagueño) |

---

## 📂 Estructura de Directorios del Proyecto

El sistema se organiza bajo una estructura modular que separa la configuración nuclear (`core`), la lógica de negocio (`gestion`), las plantillas (`templates`), los recursos estáticos (`static`) y los archivos subidos (`media`):

```text
proyecto_municipal/
│
├── manage.py                           # CLI de administración de Django
├── requirements.txt                    # Dependencias del proyecto (Django, PyMySQL, Pillow)
├── .gitignore                          # Exclusión de archivos (venv, db, media, __pycache__)
│
├── core/                               # Proyecto principal de Django (Configuración)
│   ├── __init__.py                     # Inicializador con pymysql.install_as_MySQLdb()
│   ├── asgi.py                         # Entrada ASGI para producción
│   ├── settings.py                     # Configuración de MySQL, Apps, Templates, Static y Media
│   ├── urls.py                         # Enrutador principal de URLs
│   └── wsgi.py                         # Entrada WSGI para producción
│
├── gestion/                            # App del Tablero de Gestión Municipal
│   ├── migrations/                     # Historial de migraciones de base de datos
│   │   └── __init__.py
│   │
│   ├── management/                     # Comandos personalizados de administración
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_datos_iniciales.py # Script para poblar catálogo de Barrios, Áreas y Direcciones
│   │
│   ├── templates/
│   │   └── gestion/                    # Vistas HTML específicas del negocio
│   │       ├── panel_ejecutivo.html    # Dashboard principal con KPIs y semáforos
│   │       ├── tareas_lista.html       # Tabla dinámica de tareas con filtros
│   │       ├── tarea_form_modal.html   # Formulario modal de creación/edición
│   │       ├── areas_lista.html        # Directorio de Secretarías y Direcciones
│   │       ├── area_detalle.html       # Detalle de situación y salud operativa por área
│   │       ├── reportes.html           # Matriz comparativa e indicadores de gestión
│   │       ├── reportes_pdf.html       # Layout limpio imprimible (Generador PDF)
│   │       ├── datos_respaldo.html     # Importación y exportación de respaldos (CSV/JSON)
│   │       └── seguimiento_modal.html  # Modal de historial, comentarios y multimedia
│   │
│   ├── __init__.py
│   ├── admin.py                        # Registro de modelos en el panel Admin de Django
│   ├── apps.py                         # Configuración de la app ('gestion')
│   ├── forms.py                        # Formularios Django (TareaForm, ComentarioForm, ArchivoForm)
│   ├── models.py                       # Modelos ORM (Area, Direccion, PerfilUsuario, Barrio, Tarea, Comentario, Archivo, AuditLog)
│   ├── signals.py                      # Señales para auditoría automática (AuditLog)
│   ├── urls.py                         # Rutas internas de la app 'gestion'
│   ├── views.py                        # Vistas basadas en clases (CBV) y lógica de negocio
│   └── utils.py                        # Funciones auxiliares (cálculos financieros, semáforos, validaciones)
│
├── static/                             # Archivos estáticos en la raíz del proyecto
│   ├── css/
│   │   ├── footers/
│   │   │   └── footer_gestion.css      # Estilos del pie de página
│   │   ├── headers/
│   │   │   └── header_gestion.css      # Estilos de la cabecera superior
│   │   └── pages/
│   │       ├── panel_layout.css        # Layout global, shell grid y variables CSS (#338c33, Ubuntu)
│   │       ├── gestion_panel.css       # Estilos visuales de tarjetas, tablas y gráficos
│   │       └── gestion_modal.css       # Estilos para ventanas modales y diálogos
│   │
│   ├── IMG/                            # Recursos gráficos estáticos
│   │   ├── favicon.ico
│   │   └── logo_municipal.png          # Escudo o logo de la Municipalidad
│   │
│   └── js/
│       └── gestion/
│           ├── mapa_intervenciones.js  # Lógica de geolocalización y enlaces Google Maps
│           ├── seguimiento_media.js    # Manejo y previsualización de archivos subidos (validación de 40MB)
│           └── validaciones_form.js    # Validaciones en tiempo real del formulario (Reglas de negocio)
│
├── templates/                          # Templates globales en la raíz del proyecto
│   ├── base/
│   │   └── base_panel.html             # Shell principal con sidebar, header y bloques {% block %}
│   ├── footers/
│   │   └── footer_gestion.html         # Pie de página institucional
│   ├── headers/
│   │   └── header_gestion.html         # Cabecera con selector de perfil y botón de acción
│   └── includes/
│       └── sidebar_panel.html          # Menú lateral de navegación con filtro por ROL
│
└── media/                              # Carpeta de almacenamiento de archivos dinámicos
    └── seguimiento/                    # Archivos subidos en el seguimiento de tareas
        └── %Y/%m/                      # Organizados automáticamente por año y mes
```

---

## 🔒 Convenciones Clave de Configuración

1. **Inyección PyMySQL:**
   En `core/__init__.py`:
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

2. **Límite de Carga de Archivos:**
   Configurar en `settings.py` el parámetro `DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800` (50MB) y validación en formulario de 40MB máximo por archivo.

3. **Zona Horaria y Localización:**
   `TIME_ZONE = 'America/Argentina/Cordoba'`
   `LANGUAGE_CODE = 'es-ar'`
   `USE_I18N = True`
   `USE_TZ = True`


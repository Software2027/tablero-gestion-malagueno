"""
Configuración de Django para el proyecto Tablero de Gestión Municipal - Malagueño 4.0.
"""

from pathlib import Path
import os

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta para desarrollo
SECRET_KEY = 'django-insecure-muni-malagueno-4.0-control-gestion-clave-secreta-2026'

# Modo depuración
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = ['*']

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Aplicación principal del negocio
    'gestion.apps.GestionConfig',
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Configuración de Base de Datos (MySQL 8.0+ según requerimientos técnicos)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tablero_gestion',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Alternativa directa con SQLite (descomentar si se desea trabajar en local sin servicio MySQL activo):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internacionalización y Localización
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Cordoba'
USE_I18N = True
USE_TZ = True

# Archivos Estáticos (CSS, JavaScript, Imágenes institucionales)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Archivos Dinámicos / Multimedia (Evidencias, fotos, videos, PDFs)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Límites de carga de archivos (40MB de archivo útil + margen para multipart: 50MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB

# Tipo de clave primaria por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rutas de autenticación
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'panel_ejecutivo'
LOGOUT_REDIRECT_URL = 'login'


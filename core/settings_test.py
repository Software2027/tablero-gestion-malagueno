"""
Configuración de pruebas unitarias para ejecución aislada ultrarrápida.
"""
from .settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


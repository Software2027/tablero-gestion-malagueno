from django.apps import AppConfig


class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'
    verbose_name = 'Tablero de Gestión Municipal'

    def ready(self):
        # Compatibilidad con MariaDB 10.4.x (versión estándar en XAMPP)
        try:
            from django.db.backends.mysql.base import DatabaseWrapper
            DatabaseWrapper.check_database_version_supported = lambda self: None
        except Exception:
            pass

        # Conectar señales de auditoría cuando los modelos estén listos
        try:
            import gestion.signals  # noqa
        except ImportError:
            pass

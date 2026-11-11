#!/usr/bin/env python
"""Utilidad de línea de comandos de Django para tareas administrativas."""
import os
import sys

def main():
    """Ejecuta tareas administrativas de Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # Parche de compatibilidad universal con MariaDB 10.4.x (XAMPP)
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        from django.db.backends.base.base import BaseDatabaseWrapper
        from django.db.backends.mysql.features import DatabaseFeatures

        BaseDatabaseWrapper.check_database_version_supported = lambda self: None
        DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
        DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)
    except Exception:
        pass

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Asegúrate de que esté instalado y "
            "disponible en tu variable PYTHONPATH."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

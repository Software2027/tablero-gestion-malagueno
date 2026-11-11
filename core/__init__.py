"""
Inicializador del paquete core.
Inyecta PyMySQL como conector compatible con MySQLdb para Django y
habilita compatibilidad total con MariaDB 10.4.x (versión estándar en XAMPP).
"""
import pymysql
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Inyectar conector PyMySQL
pymysql.install_as_MySQLdb()

# 1. Deshabilitar restricción de versión mínima (permite MariaDB 10.4.x)
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# 2. Deshabilitar cláusula RETURNING en INSERT como data descriptor (MariaDB 10.4.x no soporta RETURNING)
DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)

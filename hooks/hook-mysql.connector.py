"""
PyInstaller hook for mysql-connector-python.

Ensures all mysql.connector modules and plugins are properly collected,
including authentication plugins that are dynamically loaded.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all mysql.connector submodules including plugins
hiddenimports = collect_submodules('mysql.connector')

# Specifically include authentication plugins that are loaded dynamically
hiddenimports += [
    'mysql.connector.plugins',
    'mysql.connector.plugins.mysql_native_password',
    'mysql.connector.plugins.caching_sha2_password',
    'mysql.connector.plugins.sha256_password',
]

# Collect any data files (e.g., localization files)
datas = collect_data_files('mysql.connector')

"""
PyInstaller hook for oracledb to handle OpenSSL compatibility issues.

This hook ensures that OpenSSL libraries are handled correctly for
manylinux_2_28 compatibility (glibc 2.28 / OpenSSL 3.0).
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all oracledb submodules
hiddenimports = collect_submodules('oracledb')

# Collect any data files
datas = collect_data_files('oracledb')

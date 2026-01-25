"""
PyInstaller hook for _cffi_backend module.

CFFI (C Foreign Function Interface) is required by cryptography.
This hook ensures the native extension is properly collected.
"""

from PyInstaller.utils.hooks import collect_dynamic_libs

# Collect the _cffi_backend native extension
binaries = collect_dynamic_libs('_cffi_backend')

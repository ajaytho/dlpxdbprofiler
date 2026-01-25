"""
PyInstaller hook for cryptography package.

This hook ensures that all cryptography submodules and backends are
properly included in the PyInstaller binary.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# Collect all cryptography submodules
hiddenimports = collect_submodules('cryptography')

# Explicitly include important submodules that may be dynamically loaded
hiddenimports += [
    'cryptography.hazmat.backends',
    'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.backends.openssl.backend',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.ciphers',
    'cryptography.hazmat.primitives.ciphers.aead',
    'cryptography.hazmat.primitives.asymmetric',
    'cryptography.hazmat.primitives.kdf',
    'cryptography.hazmat.bindings',
    'cryptography.hazmat.bindings.openssl',
    'cryptography.hazmat.bindings.openssl.binding',
    '_cffi_backend',
]

# Collect any data files and binaries
datas = collect_data_files('cryptography')

# Collect dynamic libraries (shared objects)
binaries = collect_dynamic_libs('cryptography')



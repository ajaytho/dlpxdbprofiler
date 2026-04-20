# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Collect all charset_normalizer files (data, binaries, hiddenimports)
cn_datas, cn_binaries, cn_hiddenimports = collect_all('charset_normalizer')

a = Analysis(
    ['run_dlpxdbprofiler.py'],
    pathex=[],
    binaries=cn_binaries,
    datas=cn_datas,
    hiddenimports=[
        'dlpxdbprofiler',
        'dlpxdbprofiler.ce_client',
        'dlpxdbprofiler.db_oracle',
        'dlpxdbprofiler.db_mssql',
        'dlpxdbprofiler.db_postgres',
        'dlpxdbprofiler.db_mysql',
        'mysql.connector.plugins.mysql_native_password',
        'mysql.connector.plugins.caching_sha2_password',
        'mysql.connector.locales.eng',
        'cryptography',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.primitives.ciphers.aead',
        '_cffi_backend',
        # charset_normalizer - comprehensive imports
        'charset_normalizer',
        'charset_normalizer.md',
        'charset_normalizer.constant',
        'charset_normalizer.utils',
        'charset_normalizer.models',
        'charset_normalizer.cd',
        'charset_normalizer.api',
    ] + cn_hiddenimports,  # Add collected hiddenimports
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dlpxdbprofiler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

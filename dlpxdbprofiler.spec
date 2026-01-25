# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_dlpxdbprofiler.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    ],
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

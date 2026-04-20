# PyInstaller hook for charset_normalizer
# This ensures charset_normalizer is properly bundled

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('charset_normalizer')


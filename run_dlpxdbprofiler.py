#!/usr/bin/env python3

"""
Entry point for dlpxdbprofiler when running as a script or via PyInstaller.
"""

import os

# Set environment variable to avoid OpenSSL legacy provider errors with OpenSSL 3.x
# This must be set before any cryptography/oracledb imports
os.environ.setdefault('CRYPTOGRAPHY_OPENSSL_NO_LEGACY', '1')

from dlpxdbprofiler.main import main


if __name__ == "__main__":
    main()

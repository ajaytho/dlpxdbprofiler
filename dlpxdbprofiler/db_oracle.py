"""
db_oracle.py

Simple Oracle helper for listing schemas and tables using python-oracledb.

We support two mutually exclusive connection modes:
  - SID mode        -> DSN created with sid=<value>
  - SERVICE_NAME    -> DSN created with service_name=<value>
"""

from __future__ import annotations

import logging
from typing import List
import os

import oracledb



class OracleDBError(Exception):
    """Custom exception for Oracle DB helper."""

_THICK_MODE_INITIALIZED = False

def _init_oracle_client_if_needed(logger: logging.Logger) -> None:
    """Initialize python-oracledb in thick mode when requested.

    Some Oracle servers enforce Native Network Encryption / Data Integrity.
    That requires python-oracledb *thick* mode (otherwise you see DPY-3001).

    We switch to thick mode when the environment variable
    DBP_ORACLE_DRIVER_MODE is set to "thick" or "auto_thick".

    Optionally, DBP_ORACLE_CLIENT_LIB_DIR can be set to the directory
    containing Oracle Client / Instant Client libraries.
    """
    global _THICK_MODE_INITIALIZED

    if _THICK_MODE_INITIALIZED:
        return

    mode = os.environ.get("DBP_ORACLE_DRIVER_MODE", "").strip().lower()
    if mode not in ("thick", "auto_thick"):
        # Default is thin mode; only try thick when explicitly requested.
        return

    lib_dir = os.environ.get("DBP_ORACLE_CLIENT_LIB_DIR")
    try:
        if lib_dir:
            logger.info(
                f"Initializing python-oracledb in thick mode using lib_dir='{lib_dir}'"
            )
            oracledb.init_oracle_client(lib_dir=lib_dir)
        else:
            logger.info(
                "Initializing python-oracledb in thick mode using default Oracle "
                "client libraries (ORACLE_HOME / PATH / LD_LIBRARY_PATH)."
            )
            oracledb.init_oracle_client()
        _THICK_MODE_INITIALIZED = True
    except Exception as e:
        raise OracleDBError(
            "Failed to initialize Oracle Client in thick mode. "
            "Check that the Instant Client / ORACLE_HOME is installed and that "
            "DBP_ORACLE_CLIENT_LIB_DIR is correct. "
            f"Original error: {e}"
        )


class OracleDB:
    def __init__(
        self,
        host: str,
        port: int,
        sid: str | None,
        service_name: str | None,
        username: str,
        password: str,
        logger: logging.Logger,
    ):
        """
        Exactly one of 'sid' or 'service_name' must be non-None.
        No fallback / retry magic here.
        """
        self.host = host
        self.port = port
        self.sid = sid
        self.service_name = service_name
        self.username = username
        self.password = password
        self.logger = logger
        self.connection = None

        if self.sid and self.service_name:
            raise OracleDBError(
                "Both SID and SERVICE_NAME were provided to OracleDB. "
                "They must be mutually exclusive."
            )
        if not self.sid and not self.service_name:
            raise OracleDBError(
                "Neither SID nor SERVICE_NAME was provided to OracleDB. "
                "One of them must be set."
            )
        _init_oracle_client_if_needed(self.logger)
        try:
            if self.sid:
                dsn = oracledb.makedsn(self.host, self.port, sid=self.sid)
                mode_str = f"SID='{self.sid}'"
            else:
                dsn = oracledb.makedsn(
                    self.host, self.port, service_name=self.service_name
                )
                mode_str = f"SERVICE_NAME='{self.service_name}'"

            self.connection = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=dsn,
            )
            self.logger.info(
                f"Connected to Oracle {self.username}@{self.host}:{self.port} using {mode_str}."
            )
        except Exception as e:
            raise OracleDBError(
                f"Failed to connect to Oracle {self.username}@{self.host}:{self.port} "
                f"using {mode_str}: {e}"
            )

    def list_schemas(self) -> List[str]:
        """
        Return a list of non-system schemas.
        """
        system_schemas = {
            "ANONYMOUS",
            "APEX_040000",
            "APEX_040200",
            "APEX_050000",
            "APEX_050100",
            "APEX_PUBLIC_USER",
            "APPQOSSYS",
            "AUDSYS",
            "CTXSYS",
            "DBSNMP",
            "DIP",
            "DVF",
            "DVSYS",
            "EXFSYS",
            "FLOWS_FILES",
            "GSMADMIN_INTERNAL",
            "GSMCATUSER",
            "GSMUSER",
            "HR",
            "IX",
            "LBACSYS",
            "MDDATA",
            "MDSYS",
            "OE",
            "OLAPSYS",
            "ORACLE_OCM",
            "ORDDATA",
            "ORDPLUGINS",
            "ORDSYS",
            "OUTLN",
            "OWBSYS",
            "PM",
            "SCOTT",
            "SH",
            "SI_INFORMTN_SCHEMA",
            "SPATIAL_CSW_ADMIN_USR",
            "SPATIAL_WFS_ADMIN_USR",
            "SYS",
            "SYSBACKUP",
            "SYSDG",
            "SYSKM",
            "SYSMAN",
            "SYSTEM",
            "WKPROXY",
            "WKSYS",
            "WK_TEST",
            "WMSYS",
            "XDB",
            "XS$NULL",
            "OPS$ORACLE"
        }

        sql = """
            SELECT DISTINCT OWNER
            FROM ALL_TABLES
            ORDER BY OWNER
        """

        cur = self.connection.cursor()
        cur.execute(sql)
        rows = [r[0] for r in cur]
        cur.close()

        return [r for r in rows if r not in system_schemas]

    def list_tables_for_schema(self, schema: str) -> List[str]:
        """
        Return a list of table names for the given schema.
        """
        sql = """
            SELECT TABLE_NAME
            FROM ALL_TABLES
            WHERE OWNER = :owner
            ORDER BY TABLE_NAME
        """

        cur = self.connection.cursor()
        cur.execute(sql, owner=schema)
        rows = [r[0] for r in cur]
        cur.close()
        return rows

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None

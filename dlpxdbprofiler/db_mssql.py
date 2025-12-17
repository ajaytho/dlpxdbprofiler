import logging
from typing import List, Optional

# Use python-tds (pytds) instead of pyodbc so we don't need unixODBC
try:
    import pytds  # from python-tds
    _PYTDS_IMPORT_ERROR = None
except Exception as e:
    pytds = None  # type: ignore
    _PYTDS_IMPORT_ERROR = e


class MSSQLDBError(Exception):
    pass


class MSSQLDB:
    """
    MSSQL DB client using python-tds (pytds), which is pure Python
    and does not require unixODBC or system-level ODBC drivers.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        logger: Optional[logging.Logger] = None,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)

    def _log(self, msg: str):
        self.logger.info(msg)

    def _error(self, msg: str):
        self.logger.error(msg)
        raise MSSQLDBError(msg)

    def _ensure_pytds_available(self):
        if pytds is None:
            raise MSSQLDBError(
                "python-tds (pytds) is not available or failed to import. "
                f"Underlying error: {_PYTDS_IMPORT_ERROR!r}"
            )

    def connect(self):
        """
        Connect to SQL Server using python-tds.
        No unixODBC or system driver required.
        """
        self._ensure_pytds_available()
        try:
            conn = pytds.connect(
                server=self.host,
                database=self.database,
                user=self.username,
                password=self.password,
                port=self.port,
                as_dict=False,
                timeout=30,
            )
            return conn
        except Exception as e:
            self._error(
                f"Failed to connect to MSSQL {self.username}@{self.host}:{self.port}/{self.database}: {e}"
            )

    def list_schemas(self) -> List[str]:
        """Return non-system schemas from sys.schemas."""
        self._log("Discovering schemas from MSSQL...")
        conn = self.connect()
        try:
            cur = conn.cursor()
            sql = """
                SELECT name
                FROM sys.schemas
                WHERE name NOT IN ('sys','INFORMATION_SCHEMA')
                ORDER BY name
            """
            cur.execute(sql)
            rows = cur.fetchall()
            schemas = [r[0] for r in rows]
            if not schemas:
                self._log("No eligible schemas found.")
            else:
                self._log(f"Schemas found: {' '.join(schemas)}")
            return schemas
        finally:
            conn.close()

    def list_tables_for_schema(self, schema: str) -> List[str]:
        """Return tables in a given schema using INFORMATION_SCHEMA.TABLES."""
        schema_name = schema  # keep original case
        self._log(f"Discovering tables for schema '{schema_name}'...")
        conn = self.connect()
        try:
            cur = conn.cursor()
            sql = """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
            """
            cur.execute(sql, (schema_name,))
            rows = cur.fetchall()
            tables = [r[0] for r in rows]
            if not tables:
                self._log(f"No tables found for schema {schema_name}.")
            else:
                self._log(f"Tables in {schema_name}: {' '.join(tables)}")
            return tables
        finally:
            conn.close()

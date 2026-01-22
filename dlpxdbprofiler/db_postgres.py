import logging
import os
from typing import List, Optional

# Use psycopg2 for PostgreSQL connectivity
try:
    import psycopg2
    _PSYCOPG2_IMPORT_ERROR = None
except Exception as e:
    psycopg2 = None  # type: ignore
    _PSYCOPG2_IMPORT_ERROR = e


class PostgresDBError(Exception):
    pass


class PostgresDB:
    """
    PostgreSQL DB client using psycopg2.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        schema: str,
        username: str,
        password: str,
        logger: Optional[logging.Logger] = None,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.schema = schema
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)

    def _log(self, msg: str):
        self.logger.info(msg)

    def _error(self, msg: str):
        self.logger.error(msg)
        raise PostgresDBError(msg)

    def _ensure_psycopg2_available(self):
        if psycopg2 is None:
            raise PostgresDBError(
                "psycopg2 is not available or failed to import. "
                f"Underlying error: {_PSYCOPG2_IMPORT_ERROR!r}"
            )

    def connect(self):
        """
        Connect to PostgreSQL using psycopg2.
        Connection timeout can be configured via DBP_POSTGRES_CONNECT_TIMEOUT
        environment variable (default: 30 seconds).
        """
        self._ensure_psycopg2_available()

        # Get connection timeout from environment variable, default to 30 seconds
        timeout_str = os.environ.get("DBP_POSTGRES_CONNECT_TIMEOUT", "30")
        try:
            connect_timeout = int(timeout_str)
        except ValueError:
            self.logger.warning(
                f"Invalid DBP_POSTGRES_CONNECT_TIMEOUT value '{timeout_str}', using default 30 seconds"
            )
            connect_timeout = 30

        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                connect_timeout=connect_timeout,
            )
            return conn
        except Exception as e:
            self._error(
                f"Failed to connect to PostgreSQL {self.username}@{self.host}:{self.port}/{self.database}: {e}"
            )

    def list_schemas(self) -> List[str]:
        """Return non-system schemas from pg_catalog.pg_namespace."""
        self._log("Discovering schemas from PostgreSQL...")
        conn = self.connect()
        try:
            cur = conn.cursor()
            sql = """
                SELECT nspname
                FROM pg_catalog.pg_namespace
                WHERE nspname NOT LIKE 'pg_%'
                  AND nspname != 'information_schema'
                ORDER BY nspname
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
        """Return tables in a given schema using information_schema.tables."""
        schema_name = schema

        self._log(f"Discovering tables for schema '{schema_name}'...")
        conn = self.connect()
        try:
            cur = conn.cursor()
            sql = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            cur.execute(sql, (schema_name,))
            rows = cur.fetchall()
            tables = [r[0] for r in rows]
            if not tables:
                self._log(f"No tables found in schema '{schema_name}'.")
            else:
                self._log(
                    f"Found {len(tables)} table(s) in '{schema_name}': "
                    f"{', '.join(tables[:5])}"
                    + (f" ... and {len(tables) - 5} more" if len(tables) > 5 else "")
                )
            return tables
        finally:
            conn.close()

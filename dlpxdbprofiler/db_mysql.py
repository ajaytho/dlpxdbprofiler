import logging
import os
from typing import List, Optional

# Use mysql-connector-python for MySQL connectivity
try:
    import mysql.connector
    _MYSQL_IMPORT_ERROR = None
except Exception as e:
    mysql = None  # type: ignore
    _MYSQL_IMPORT_ERROR = e


class MySQLDBError(Exception):
    pass


class MySQLDB:
    """
    MySQL DB client using mysql-connector-python.
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
        raise MySQLDBError(msg)

    def _ensure_mysql_available(self):
        if mysql is None:
            raise MySQLDBError(
                "mysql-connector-python is not available or failed to import. "
                f"Underlying error: {_MYSQL_IMPORT_ERROR!r}"
            )

    def connect(self):
        """
        Connect to MySQL using mysql-connector-python.
        Connection timeout can be configured via DBP_MYSQL_CONNECT_TIMEOUT
        environment variable (default: 30 seconds).
        """
        self._ensure_mysql_available()

        # Get connection timeout from environment variable, default to 30 seconds
        timeout_str = os.environ.get("DBP_MYSQL_CONNECT_TIMEOUT", "30")
        try:
            connect_timeout = int(timeout_str)
        except ValueError:
            self.logger.warning(
                f"Invalid DBP_MYSQL_CONNECT_TIMEOUT value '{timeout_str}', using default 30 seconds"
            )
            connect_timeout = 30

        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                connection_timeout=connect_timeout,
            )
            return conn
        except Exception as e:
            self._error(
                f"Failed to connect to MySQL {self.username}@{self.host}:{self.port}/{self.database}: {e}"
            )

    def list_tables(self) -> List[str]:
        """Return tables in the connected database using information_schema.tables."""
        self._log(f"Discovering tables for database '{self.database}'...")
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
            cur.execute(sql, (self.database,))
            rows = cur.fetchall()
            tables = [r[0] for r in rows]
            if not tables:
                self._log(f"No tables found in database '{self.database}'.")
            else:
                self._log(
                    f"Found {len(tables)} table(s) in '{self.database}': "
                    f"{', '.join(tables[:5])}"
                    + (f" ... and {len(tables) - 5} more" if len(tables) > 5 else "")
                )
            return tables
        finally:
            conn.close()

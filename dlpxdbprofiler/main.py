import argparse
import logging
import os
import sys
import time
import warnings
from dataclasses import dataclass
from typing import Optional

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# ---------------------------------------------------------------------------
# Version handling
# ---------------------------------------------------------------------------

# When run as a package (import dlpxdbprofiler.main), __package__ == "dlpxdbprofiler"
# When run as a script (python dlpxdbprofiler/main.py), __package__ is None or ""
if __package__:
    from . import __version__ as VERSION  # type: ignore[attr-defined]
else:
    # Running as a script from inside the dlpxdlpxdbprofiler folder
    from __init__ import __version__ as VERSION  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Suppress Python 3.6 deprecation warnings from oracledb + cryptography
# (only relevant for the CentOS 7 / Python 3.6 build)
# ---------------------------------------------------------------------------

warnings.filterwarnings(
    "ignore",
    message="Python 3.6 is no longer supported by the Python core team.*",
)

try:
    from cryptography.utils import CryptographyDeprecationWarning  # type: ignore

    warnings.filterwarnings(
        "ignore",
        category=CryptographyDeprecationWarning,
    )
except Exception:
    # cryptography may change layout; ignore if not importable
    pass

# ---------------------------------------------------------------------------
# Local imports – handle both package and script usage
# ---------------------------------------------------------------------------

if __package__:
    from .ce_client import CEClient, CEError
    from .db_oracle import OracleDB, OracleDBError
    from .db_mssql import MSSQLDB, MSSQLDBError
else:
    from ce_client import CEClient, CEError
    from db_oracle import OracleDB, OracleDBError
    from db_mssql import MSSQLDB, MSSQLDBError

# Disable SSL warnings for verify=False (like curl -k)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

LOG_FILE = os.path.join(os.getcwd(), "dlpxdlpxdbprofiler.log")


@dataclass
class OracleConfig:
    host: str = ""
    port: int = 1521
    sid: str | None = None           # used when connecting via SID
    service_name: str | None = None  # used when connecting via SERVICE_NAME
    username: str = ""
    password: str = ""


@dataclass
class MSSQLConfig:
    host: str = ""
    port: int = 1433
    database: str = ""
    username: str = ""
    password: str = ""


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("dlpxdlpxdbprofiler")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # No banner logs here; banner will be printed in main()
    return logger


def prompt_non_empty(prompt: str, default: Optional[str] = None) -> str:
    while True:
        if default is not None:
            val = input(f"{prompt} [{default}]: ").strip()
            if not val:
                val = default
        else:
            val = input(f"{prompt}: ").strip()
        if val:
            return val
        print("Value cannot be empty.")


def prompt_secret(prompt: str) -> str:
    import getpass

    while True:
        val = getpass.getpass(f"{prompt}: ").strip()
        if val:
            return val
        print("Value cannot be empty.")


def get_value_from_env_or_prompt(
    name: str,
    env_var: str,
    prompt: str,
    default: Optional[str] = None,
    secret: bool = False,
    logger: Optional[logging.Logger] = None,
) -> str:
    """
    If env var is set, use that.
    Otherwise, prompt the user (secret = use getpass).
    """
    env_val = os.getenv(env_var)

    if env_val is not None and env_val != "":
        if logger:
            # Do NOT log secret values
            if secret:
                logger.info(f"{name} loaded from environment variable {env_var}.")
            else:
                logger.info(
                    f"{name} loaded from environment variable {env_var}: {env_val}"
                )
        return env_val

    # Env not set → fall back to interactive prompt
    if secret:
        return prompt_secret(prompt)
    else:
        return prompt_non_empty(prompt, default=default)


def prepare_ce_client(logger: logging.Logger) -> CEClient:
    # Use environment variables if present, otherwise prompt
    base_url = get_value_from_env_or_prompt(
        name="Compliance Engine base URL",
        env_var="DBP_CE_BASE_URL",
        prompt="Compliance Engine base URL (e.g. http://uvo1sc1lhi8ypfunlcp.vm.cld.sr)",
        logger=logger,
    )

    username = get_value_from_env_or_prompt(
        name="Compliance Engine username",
        env_var="DBP_CE_USERNAME",
        prompt="Compliance Engine username",
        logger=logger,
    )

    password = get_value_from_env_or_prompt(
        name="Compliance Engine password",
        env_var="DBP_CE_PASSWORD",
        prompt="Compliance Engine password",
        secret=True,
        logger=logger,
    )

    api_version = get_value_from_env_or_prompt(
        name="Compliance Engine API Version",
        env_var="DBP_CE_API_VERSION",
        prompt="Compliance Engine API Version (e.g. v5.1.46)",
        default="v5.1.46",
        logger=logger,
    )

    logger.info(f"CE base URL: {base_url}")
    logger.info(f"CE API version: {api_version}")

    ce = CEClient(
        base_url=base_url,
        api_version=api_version,
        username=username,
        password=password,
        verify_ssl=False,
        logger=logger,
    )
    ce.login()
    return ce



def prepare_oracle_config(logger: logging.Logger) -> OracleConfig:
    host = get_value_from_env_or_prompt(
        name="Oracle host",
        env_var="DBP_ORACLE_HOST",
        prompt="Oracle host",
        logger=logger,
    )
    port_str = get_value_from_env_or_prompt(
        name="Oracle port",
        env_var="DBP_ORACLE_PORT",
        prompt="Oracle port",
        default="1521",
        logger=logger,
    )

    # ----- SID vs SERVICE_NAME (mutually exclusive) -----
    sid_env = os.getenv("DBP_ORACLE_SID", "").strip()
    svc_env = os.getenv("DBP_ORACLE_SERVICE_NAME", "").strip()

    sid: str | None = None
    service_name: str | None = None

    if sid_env and svc_env:
        # Both set -> explicit error
        logger.error(
            "Both DBP_ORACLE_SID and DBP_ORACLE_SERVICE_NAME are set. "
            "Please set only one of them."
        )
        raise ValueError(
            "Both DBP_ORACLE_SID and DBP_ORACLE_SERVICE_NAME are set. "
            "Please set only one of them."
        )
    elif sid_env:
        sid = sid_env  # do NOT uppercase; let user control exact casing if needed
        logger.info(f"Oracle connection will use SID='{sid}' from DBP_ORACLE_SID.")
    elif svc_env:
        service_name = svc_env
        logger.info(
            f"Oracle connection will use SERVICE_NAME='{service_name}' from DBP_ORACLE_SERVICE_NAME."
        )
    else:
        # No env var -> interactive choice
        print("Oracle connection identifier:")
        print("  1) SID (e.g. ORAMASK)")
        print("  2) SERVICE_NAME (e.g. appservice)")
        choice = input("Connect using [1-2, default 1]: ").strip() or "1"

        if choice == "2":
            service_name = prompt_non_empty("Oracle SERVICE_NAME")
            logger.info(f"Oracle connection will use SERVICE_NAME='{service_name}'.")
        else:
            sid = prompt_non_empty("Oracle SID")
            logger.info(f"Oracle connection will use SID='{sid}'.")

    username = get_value_from_env_or_prompt(
        name="Oracle connector username",
        env_var="DBP_ORACLE_USER",
        prompt="Oracle connector username",
        logger=logger,
    ).upper()
    password = get_value_from_env_or_prompt(
        name="Oracle connector user password",
        env_var="DBP_ORACLE_PASSWORD",
        prompt="Oracle connector user password",
        secret=True,
        logger=logger,
    )

    try:
        port = int(port_str)
    except ValueError:
        logger.error("Port must be an integer.")
        raise

    logger.info(f"DB host: {host}")
    logger.info(f"DB port: {port}")
    if sid:
        logger.info(f"DB identifier type: SID = {sid}")
    elif service_name:
        logger.info(f"DB identifier type: SERVICE_NAME = {service_name}")
    else:
        # defensive, should not happen
        logger.error("Neither SID nor SERVICE_NAME is set for Oracle.")
        raise ValueError("Neither SID nor SERVICE_NAME is set for Oracle.")

    logger.info(f"DB connector user (uppercased): {username}")

    return OracleConfig(
        host=host,
        port=port,
        sid=sid,
        service_name=service_name,
        username=username,
        password=password,
    )


def prepare_mssql_config(logger: logging.Logger) -> MSSQLConfig:
    host = get_value_from_env_or_prompt(
        name="MSSQL host",
        env_var="DBP_MSSQL_HOST",
        prompt="MSSQL host",
        logger=logger,
    )

    port_str = get_value_from_env_or_prompt(
        name="MSSQL port",
        env_var="DBP_MSSQL_PORT",
        prompt="MSSQL port",
        default="1433",
        logger=logger,
    )

    database = get_value_from_env_or_prompt(
        name="MSSQL database name",
        env_var="DBP_MSSQL_DATABASE",
        prompt="MSSQL database name",
        logger=logger,
    )

    username = get_value_from_env_or_prompt(
        name="MSSQL connector username",
        env_var="DBP_MSSQL_USER",
        prompt="MSSQL connector username",
        logger=logger,
    )

    password = get_value_from_env_or_prompt(
        name="MSSQL connector user password",
        env_var="DBP_MSSQL_PASSWORD",
        prompt="MSSQL connector user password",
        secret=True,
        logger=logger,
    )

    try:
        port = int(port_str)
    except ValueError:
        logger.error("Port must be an integer.")
        raise

    logger.info(f"DB host: {host}")
    logger.info(f"DB port: {port}")
    logger.info(f"DB database: {database}")
    logger.info(f"DB connector user: {username}")

    return MSSQLConfig(
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
    )



def choose_db_engine(logger: logging.Logger) -> str:
    print("Select database engine:")
    print("  1) Oracle")
    print("  2) MSSQL")
    choice = input("Enter choice [1-2]: ").strip()
    if choice == "2":
        logger.info("DB engine: MSSQL")
        return "MSSQL"
    logger.info("DB engine: Oracle")
    return "ORACLE"


def choose_connector_scope(logger: logging.Logger) -> str:
    print("Connector creation scope:")
    print("  1) Single schema only")
    print("  2) All schemas in database (default)")
    choice = input("Enter choice [1-2]: ").strip()
    if choice == "1":
        logger.info("Connector scope: single schema")
        return "SCHEMA"
    logger.info("Connector scope: all schemas in database")
    return "DB"


def choose_oracle_connector_type(logger: logging.Logger) -> str:
    print("Oracle connector type:")
    print("  1) Native (host/port/sid)")
    print("  2) JDBC (jdbc:oracle:thin:@//host:port/SID)")
    choice = input("Enter choice [1-2]: ").strip()
    if choice == "2":
        logger.info("Oracle connector type: JDBC")
        return "JDBC"
    logger.info("Oracle connector type: NATIVE")
    return "NATIVE"


def choose_profile_run_scope(logger: logging.Logger) -> str:
    print("Profile run scope:")
    print("  1) Single profile job only")
    print("  2) All profile jobs in environment (default)")
    choice = input("Enter choice [1-2]: ").strip()
    if choice == "1":
        logger.info("Profile run scope: SINGLE")
        return "SINGLE"
    logger.info("Profile run scope: ALL")
    return "ALL"


# ------------- operations -------------

def op_create_application(logger: logging.Logger):
    ce = prepare_ce_client(logger)
    app_name = prompt_non_empty("Application name")
    logger.info("Application operation selected.")
    ce.ensure_application(app_name)


def op_create_environment(logger: logging.Logger):
    ce = prepare_ce_client(logger)
    app_name = prompt_non_empty("Application name")
    env_name = prompt_non_empty("Environment name")

    logger.info("Environment operation selected.")
    app_id = ce.ensure_application(app_name)
    ce.ensure_environment(app_id, env_name)


def _create_connectors_for_engine(
    logger: logging.Logger,
    ce: CEClient,
    db_engine: str,
    app_name: str,
    env_name: str,
    profile_set_id: int,
):
    app_id = ce.ensure_application(app_name)
    env_id = ce.ensure_environment(app_id, env_name)

    connector_scope = choose_connector_scope(logger)

    if db_engine == "ORACLE":
        oracle_cfg = prepare_oracle_config(logger)
        oracle_db = OracleDB(
            host=oracle_cfg.host,
            port=oracle_cfg.port,
            sid=oracle_cfg.sid,
            service_name=oracle_cfg.service_name,
            username=oracle_cfg.username,
            password=oracle_cfg.password,
            logger=logger,
        )

        connector_type = choose_oracle_connector_type(logger)

        # Common identifier string for JDBC URL
        oracle_identifier = oracle_cfg.service_name or oracle_cfg.sid

        schemas = oracle_db.list_schemas()
        if connector_scope == "SCHEMA":
            schema_name = prompt_non_empty("Schema name to use for connector").upper()
            if schema_name not in schemas:
                logger.error(f"Schema {schema_name} not found in database.")
                return
            schemas = [schema_name]

        for schema in schemas:
            connector_name = f"CONNECTOR_{schema}"
            logger.info(
                f"Processing Oracle connector {connector_name} for schema {schema} "
                f"(type={connector_type})"
            )
            existing_id = ce.find_connector_by_name(env_id, connector_name)
            if existing_id is not None:
                logger.info(
                    f"Connector '{connector_name}' already exists (ID={existing_id}). "
                    f"Will still create ruleset/profile job."
                )
                connector_id = existing_id
            else:
                if connector_type == "JDBC":
                    # Use the same identifier (SID or SERVICE_NAME) that OracleDB used.
                    # If you need a slightly different format for CE, adjust here.
                    jdbc_id = oracle_identifier
                    # You earlier mentioned wanting "jdbc:oracle:thin:@//host:port/ID"
                    # If that's required, keep the // here.
                    jdbc_url = f"jdbc:oracle:thin:@//{oracle_cfg.host}:{oracle_cfg.port}/{jdbc_id}"

                    logger.info(f"Using JDBC URL for connector '{connector_name}': {jdbc_url}")

                    connector_id = ce.create_connector_oracle_jdbc(
                        name=connector_name,
                        env_id=env_id,
                        jdbc_url=jdbc_url,
                        schema=schema,
                        username=oracle_cfg.username,
                        password=oracle_cfg.password,
                    )
                else:
                    connector_id = ce.create_connector_oracle_native(
                        name=connector_name,
                        env_id=env_id,
                        host=oracle_cfg.host,
                        port=oracle_cfg.port,
                        sid=oracle_cfg.sid or "",  # native connect currently expects SID path
                        schema=schema,
                        username=oracle_cfg.username,
                        password=oracle_cfg.password,
                    )

            if connector_id is None:
                logger.info(
                    f"Skipping ruleset/profile creation for schema {schema} "
                    f"due to missing connector id."
                )
                continue

            ruleset_id = ce.create_ruleset(connector_id, schema)
            tables = oracle_db.list_tables_for_schema(schema)
            ce.bulk_add_tables_to_ruleset(ruleset_id, tables)
            ce.create_profile_job(ruleset_id, schema, profile_set_id)

    elif db_engine == "MSSQL":
        mssql_cfg = prepare_mssql_config(logger)
        mssql_db = MSSQLDB(
            host=mssql_cfg.host,
            port=mssql_cfg.port,
            database=mssql_cfg.database,
            username=mssql_cfg.username,
            password=mssql_cfg.password,
            logger=logger,
        )

        schemas = mssql_db.list_schemas()
        if connector_scope == "SCHEMA":
            schema_name = prompt_non_empty("Schema name to use for connector")
            if schema_name not in schemas:
                logger.error(f"Schema {schema_name} not found in database.")
                return
            schemas = [schema_name]

        for schema in schemas:
            connector_name = f"CONNECTOR_{schema}"
            logger.info(
                f"Processing MSSQL connector {connector_name} for schema {schema}"
            )
            existing_id = ce.find_connector_by_name(env_id, connector_name)
            if existing_id is not None:
                logger.info(
                    f"Connector '{connector_name}' already exists (ID={existing_id}). "
                    f"Will still create ruleset/profile job."
                )
                connector_id = existing_id
            else:
                connector_id = ce.create_connector_mssql(
                    name=connector_name,
                    env_id=env_id,
                    host=mssql_cfg.host,
                    port=mssql_cfg.port,
                    database_name=mssql_cfg.database,
                    schema=schema,
                    username=mssql_cfg.username,
                    password=mssql_cfg.password,
                )

            if connector_id is None:
                logger.info(
                    f"Skipping ruleset/profile creation for schema {schema} "
                    f"due to missing connector id."
                )
                continue

            ruleset_id = ce.create_ruleset(connector_id, schema)
            tables = mssql_db.list_tables_for_schema(schema)
            ce.bulk_add_tables_to_ruleset(ruleset_id, tables)
            ce.create_profile_job(ruleset_id, schema, profile_set_id)


def op_create_connectors(logger: logging.Logger, include_app_env_text: bool):
    ce = prepare_ce_client(logger)
    app_name = prompt_non_empty("Application name")
    env_name = prompt_non_empty("Environment name")
    #profile_set_id_str = prompt_non_empty("Profile Set ID", default="20")
    profile_set_id_str = get_value_from_env_or_prompt(
        name="Profile Set ID",
        env_var="DBP_PROFILE_SET_ID",
        prompt="Profile Set ID",
        default="20",
        logger=logger,
    )
    profile_set_id = int(profile_set_id_str)

    db_engine = choose_db_engine(logger)

    if include_app_env_text:
        logger.info(
            "All operations selected (App + Env + Connectors + Rulesets + Profile jobs)."
        )
    else:
        logger.info("Connector + Ruleset + Profile job operation selected.")

    _create_connectors_for_engine(
        logger=logger,
        ce=ce,
        db_engine=db_engine,
        app_name=app_name,
        env_name=env_name,
        profile_set_id=profile_set_id,
    )


def op_delete_environment(logger: logging.Logger):
    ce = prepare_ce_client(logger)
    env_id_str = prompt_non_empty("Environment ID to delete")
    env_id = int(env_id_str)
    logger.info("Delete Environment operation selected.")
    ce.delete_environment(env_id)


def op_delete_application(logger: logging.Logger):
    ce = prepare_ce_client(logger)
    app_id_str = prompt_non_empty("Application ID to delete")
    app_id = int(app_id_str)
    logger.info("Delete Application operation selected.")
    ce.delete_application(app_id)


def op_list_environments(logger: logging.Logger):
    ce = prepare_ce_client(logger)
    logger.info("List all environments operation selected.")
    rows = ce.list_all_environments_grouped()

    print(
        f"{'ENVIRONMENT_ID':<15} {'ENVIRONMENT_NAME':<25} "
        f"{'APPLICATION_ID':<15} {'APPLICATION_NAME':<25}"
    )
    print(
        f"{'-' * 13:<15} {'-' * 24:<25} "
        f"{'-' * 14:<15} {'-' * 24:<25}"
    )
    for env_id, env_name, app_id, app_name in rows:
        print(f"{env_id:<15} {env_name:<25} {app_id:<15} {app_name:<25}")


def op_list_schemas(logger: logging.Logger):
    db_engine = choose_db_engine(logger)
    if db_engine == "ORACLE":
        cfg = prepare_oracle_config(logger)
        db = OracleDB(
            host=cfg.host,
            port=cfg.port,
            sid=cfg.sid,
            service_name=cfg.service_name,  # <-- added this line
            username=cfg.username,
            password=cfg.password,
            logger=logger,
        )
    else:
        cfg = prepare_mssql_config(logger)
        db = MSSQLDB(
            host=cfg.host,
            port=cfg.port,
            database=cfg.database,
            username=cfg.username,
            password=cfg.password,
            logger=logger,
        )

    logger.info("List all schemas operation selected.")
    schemas = db.list_schemas()
    print(f"{'SCHEMA_NAME':<25}")
    print(f"{'-' * 11:<25}")
    for s in schemas:
        print(f"{s:<25}")


def op_list_profile_sets(logger: logging.Logger):
    ce = prepare_ce_client(logger)
    logger.info("List profile sets operation selected.")
    sets = ce.list_profile_sets()

    print(f"{'PROFILESET_ID':<15} {'PROFILESET_NAME':<30} {'CREATED_BY':<15}")
    print(f"{'-' * 13:<15} {'-' * 28:<30} {'-' * 10:<15}")
    for ps in sorted(sets, key=lambda x: int(x["profileSetId"])):
        pid = ps.get("profileSetId")
        name = ps.get("profileSetName")
        created_by = ps.get("createdBy", "")
        print(f"{pid:<15} {name:<30} {created_by:<15}")

def op_list_applications(logger: logging.Logger):
    """
    List all applications in the masking engine:
      APPLICATION_ID  APPLICATION_NAME
    """
    ce = prepare_ce_client(logger)
    logger.info("List applications operation selected.")
    apps = ce.list_applications()

    if not apps:
        print("No applications found.")
        return

    print(f"{'APPLICATION_ID':<15} {'APPLICATION_NAME':<30}")
    print(f"{'-' * 13:<15} {'-' * 16:<30}")
    for app in apps:
        app_id = app.get("applicationId", "")
        app_name = app.get("applicationName", "")
        print(f"{app_id:<15} {app_name:<30}")


def _run_single_profile_job(
    logger: logging.Logger, ce: CEClient, job_id: int, job_name: str
):
    logger.info(f"Starting profile job ID={job_id}, name='{job_name}' ...")
    exec_id = ce.start_profile_execution(job_id)

    while True:
        data = ce.get_execution_status(exec_id)
        status = data.get("status")
        logger.info(f"Job {job_id}, executionId={exec_id} status: {status}")
        if status == "SUCCEEDED":
            logger.info(f"Profile job {job_id} SUCCEEDED.")
            break
        elif status in ("FAILED", "ERROR"):
            logger.error(f"Profile job {job_id} FAILED. Response: {data}")
            break
        elif status == "CANCELLED":
            logger.error(f"Profile job {job_id} CANCELLED. Response: {data}")
            break
        else:
            time.sleep(5)



def _run_profile_jobs_parallel(
    logger: logging.Logger, ce: CEClient, jobs: list[dict], max_parallel: int
):
    """
    Start and monitor profile jobs in parallel batches up to max_parallel.
    Jobs themselves run in parallel on the engine; this function just
    submits them and polls their execution status.
    """
    if max_parallel <= 0:
        max_parallel = 1

    # Sort jobs by profileJobId for deterministic behavior
    pending = sorted(jobs, key=lambda x: int(x["profileJobId"]))
    running: list[dict] = []
    index = 0

    logger.info(f"Submitting {len(pending)} profile jobs in batches of {max_parallel}.")

    while index < len(pending) or running:
        # Start new executions up to max_parallel
        while index < len(pending) and len(running) < max_parallel:
            job = pending[index]
            job_id = int(job["profileJobId"])
            job_name = job["jobName"]
            logger.info(f"Submitting profile job ID={job_id}, name='{job_name}' ...")
            exec_id = ce.start_profile_execution(job_id)
            running.append(
                {
                    "jobId": job_id,
                    "jobName": job_name,
                    "executionId": exec_id,
                }
            )
            index += 1

        # Nothing running yet (should not happen) - safety
        if not running:
            break

        # Poll status for running executions
        time.sleep(5)
        for item in list(running):
            exec_id = item["executionId"]
            job_id = item["jobId"]
            job_name = item["jobName"]

            data = ce.get_execution_status(exec_id)
            status = data.get("status")
            logger.info(
                f"[PARALLEL] Job {job_id} ('{job_name}'), executionId={exec_id} status: {status}"
            )

            if status == "SUCCEEDED":
                logger.info(f"[PARALLEL] Profile job {job_id} SUCCEEDED.")
                running.remove(item)
            elif status in ("FAILED", "ERROR"):
                logger.error(
                    f"[PARALLEL] Profile job {job_id} FAILED. Response: {data}"
                )
                running.remove(item)
            elif status == "CANCELLED":
                logger.error(
                    f"[PARALLEL] Profile job {job_id} CANCELLED. Response: {data}"
                )
                running.remove(item)
            # else: keep it in running list and check again on next loop


def op_run_profile_jobs(logger: logging.Logger):
    ce = prepare_ce_client(logger)
    app_name = prompt_non_empty("Application name")
    env_name = prompt_non_empty("Environment name")

    logger.info("Run profile jobs (single/all) operation selected.")
    app_id = ce.ensure_application(app_name)
    env_id = ce.ensure_environment(app_id, env_name)

    scope = choose_profile_run_scope(logger)
    jobs = ce.list_profile_jobs_for_env(env_id)
    if not jobs:
        logger.info("No profile jobs found for this environment.")
        return

    # --- SINGLE JOB MODE ---
    if scope == "SINGLE":
        print(f"{'JOB_ID':<15} {'JOB_NAME':<40}")
        print(f"{'-' * 6:<15} {'-' * 35:<40}")
        for j in sorted(jobs, key=lambda x: int(j["profileJobId"])):
            print(f"{j['profileJobId']:<15} {j['jobName']:<40}")

        sel_id_str = prompt_non_empty("Enter profile job ID to run")
        sel_id = int(sel_id_str)
        job = next(
            (j for j in jobs if int(j["profileJobId"]) == sel_id),
            None,
        )
        if not job:
            logger.error(f"Profile job ID {sel_id} not found in this environment.")
            return

        _run_single_profile_job(logger, ce, sel_id, job["jobName"])
        return

    # --- ALL JOBS MODE (SERIAL OR PARALLEL) ---
    # Ask user whether to run serially (old behavior) or in parallel.
    print("\nRun mode for ALL profile jobs:")
    print("  1) Serial (default)")
    print("  2) Parallel (up to N concurrent jobs)")
    mode = input("Enter choice [1-2]: ").strip()

    if mode == "2":
        # Decide degree of parallelism from env or prompt
        env_parallel = os.getenv("DBP_PROFILE_MAX_PARALLEL", "").strip()
        default_parallel = None
        if env_parallel.isdigit() and int(env_parallel) > 0:
            default_parallel = int(env_parallel)
        else:
            # Sensible default: up to 3 or number of jobs, whichever is smaller
            default_parallel = min(3, len(jobs))

        parallel_str = prompt_non_empty(
            f"Max parallel profile jobs", default=str(default_parallel)
        )
        try:
            max_parallel = int(parallel_str)
        except ValueError:
            logger.error("Max parallel profile jobs must be an integer. Falling back to 1.")
            max_parallel = 1

        if max_parallel <= 0:
            logger.error("Max parallel profile jobs must be >= 1. Falling back to 1.")
            max_parallel = 1

        logger.info(
            f"Executing ALL profile jobs in environment in PARALLEL (max_parallel={max_parallel})."
        )
        _run_profile_jobs_parallel(logger, ce, jobs, max_parallel)
    else:
        # Original serial behavior
        logger.info("Executing ALL profile jobs in environment SERIALLY.")
        for j in sorted(jobs, key=lambda x: int(x["profileJobId"])):
            _run_single_profile_job(
                logger, ce, int(j["profileJobId"]), j["jobName"]
            )


def show_help():
    """Display help information for the dlpxdbprofiler tool."""
    help_text = f"""
dlpxdbprofiler v{VERSION} - Delphix Continuous Compliance Engine DB profiling helper

DESCRIPTION:
    A standalone CLI utility designed to automate profiling across an entire 
    database for the Delphix Continuous Compliance Engine (Masking Engine).
    
    Supports Oracle & MSSQL databases and performs:
    - Application creation
    - Environment creation  
    - Connector creation
    - Ruleset creation
    - Profile Job creation
    - Listing metadata (Applications, Environments, Profile Sets, Database Schemas)
    - Running Profile jobs (serial or parallel)
    - Environment cleanup (delete env/app)

USAGE:
    dlpxdbprofiler [OPTIONS]

OPTIONS:
    --help, -h      Show this help message and exit
    --version, -v   Show version information and exit

INTERACTIVE MODE:
    When run without arguments, dlpxdbprofiler starts in interactive mode
    with a menu-driven interface for selecting operations.

ENVIRONMENT VARIABLES:
    The tool can be configured using environment variables for non-interactive use:

    Compliance Engine:
        DBP_CE_BASE_URL         Compliance Engine base URL
        DBP_CE_USERNAME         Username for CE
        DBP_CE_PASSWORD         Password for CE
        DBP_CE_API_VERSION      API version (default: v5.1.46)

    Oracle Database (use either SID or SERVICE_NAME, not both):
        DBP_ORACLE_HOST         Oracle host
        DBP_ORACLE_PORT         Oracle port (default: 1521)
        DBP_ORACLE_SID          Oracle SID (for SID connection)
        DBP_ORACLE_SERVICE_NAME Oracle Service Name (for SERVICE_NAME connection)
        DBP_ORACLE_USER         Oracle username
        DBP_ORACLE_PASSWORD     Oracle password

    MSSQL Database:
        DBP_MSSQL_HOST          MSSQL host
        DBP_MSSQL_PORT          MSSQL port (default: 1433)
        DBP_MSSQL_DATABASE      MSSQL database name
        DBP_MSSQL_USER          MSSQL username
        DBP_MSSQL_PASSWORD      MSSQL password

EXAMPLES:
    # Show help
    ./dlpxdbprofiler --help

    # Show version
    ./dlpxdbprofiler --version

    # Run in interactive mode
    ./dlpxdbprofiler

    # Run with environment variables (non-interactive)
    export DBP_CE_BASE_URL="http://your-mask-engine"
    export DBP_CE_USERNAME="admin"
    export DBP_CE_PASSWORD="password"
    export DBP_ORACLE_HOST="10.10.10.10"
    export DBP_ORACLE_SID="ORCL"
    export DBP_ORACLE_USER="hr"
    export DBP_ORACLE_PASSWORD="password"
    ./dlpxdbprofiler

For more information, visit: https://github.com/delphix/dlpxdbprofiler
"""
    print(help_text)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Delphix Continuous Compliance Engine DB profiling helper",
        add_help=False  # We'll handle --help ourselves for custom formatting
    )
    parser.add_argument(
        "--help", "-h", 
        action="store_true",
        help="Show help message and exit"
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true", 
        help="Show version information and exit"
    )
    
    args = parser.parse_args()
    
    # Handle --help
    if args.help:
        show_help()
        sys.exit(0)
    
    # Handle --version  
    if args.version:
        print(f"dlpxdbprofiler version {VERSION}")
        sys.exit(0)

    logger = setup_logging()

    # Interactive menu mode
    while True:
        print("\nSelect operation:")
        print("  1) Create/Ensure Application")
        print("  2) Create/Ensure Environment")
        print("  3) Create Connectors (+ Rulesets + Profile Jobs)")
        print("  4) Create ALL (App + Env + Connectors + Rulesets + Profile Jobs)")
        print("  5) DELETE Environment")
        print("  6) DELETE Application")
        print("  7) LIST Applications")
        print("  8) LIST Environments")
        print("  9) LIST Profile Sets")
        print(" 10) LIST all Schemas in database")
        print(" 11) Run Profile jobs (single or all) for environment")
        print("  0) Exit")

        choice = input("Enter choice [0-11]: ").strip()

        try:
            if choice == "1":
                op_create_application(logger)
            elif choice == "2":
                op_create_environment(logger)
            elif choice == "3":
                op_create_connectors(logger, include_app_env_text=False)
            elif choice == "4":
                op_create_connectors(logger, include_app_env_text=True)
            elif choice == "5":
                op_delete_environment(logger)
            elif choice == "6":
                op_delete_application(logger)
            elif choice == "7":
                op_list_applications(logger)        # ⬅️ NEW
            elif choice == "8":
                op_list_environments(logger)
            elif choice == "9":
                op_list_profile_sets(logger)
            elif choice == "10":
                op_list_schemas(logger)
            elif choice == "11":
                op_run_profile_jobs(logger)
            elif choice == "0":
                logger.info("Exiting.")
                break
            else:
                print("Invalid choice.")
        except (CEError, OracleDBError, MSSQLDBError, ValueError) as e:
            logger.error(f"Operation failed: {e}")



if __name__ == "__main__":
    main()

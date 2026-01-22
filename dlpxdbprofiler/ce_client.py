
import json
import logging
from typing import List, Dict, Optional, Tuple

import requests
from requests.exceptions import RequestException


class CEError(Exception):
    pass


class CEClient:
    """Delphix Compliance Engine REST API client."""

    def __init__(
        self,
        base_url: str,
        api_version: str = "v5.1.46",
        username: str = "",
        password: str = "",
        verify_ssl: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.logger = logger or logging.getLogger(__name__)

        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.api_base = f"{self.base_url}/masking/api/{self.api_version}"

    # ------------- internal helpers -------------

    def _log(self, msg: str):
        self.logger.info(msg)

    def _error(self, msg: str):
        self.logger.error(msg)
        raise CEError(msg)

    def _headers(self) -> Dict[str, str]:
        if not self.auth_token:
            self._error("Authorization token is not set. Call login() first.")
        return {
            "Authorization": self.auth_token,
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
        use_auth: bool = True,
    ) -> Dict:
        url = f"{self.api_base}{path}"
        try:
            headers = (
                self._headers()
                if use_auth
                else {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                }
            )
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                headers=headers,
                verify=self.verify_ssl,
            )
        except RequestException as e:
            self._error(f"Request to {url} failed: {e}")

        if resp.status_code >= 400:
            try:
                data = resp.json()
            except json.JSONDecodeError:
                data = resp.text
            self._error(f"HTTP {resp.status_code} for {url}: {data}")

        try:
            return resp.json()
        except json.JSONDecodeError:
            return {}

    # ------------- auth -------------

    def login(self):
        self._log(f"Logging in as '{self.username}' ...")
        payload = {"username": self.username, "password": self.password}
        url = f"{self.api_base}/login"

        try:
            resp = self.session.post(
                url,
                json=payload,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                verify=self.verify_ssl,
            )
        except RequestException as e:
            self._error(f"Login request failed: {e}")

        if resp.status_code >= 400:
            try:
                data = resp.json()
            except json.JSONDecodeError:
                data = resp.text
            self._error(f"Login failed (HTTP {resp.status_code}): {data}")

        data = resp.json()
        token = data.get("Authorization")
        if not token:
            self._error(f"Login did not return Authorization token: {data}")

        self.auth_token = token
        self._log("Login successful.")

    # ------------- applications -------------

    def list_applications(self) -> List[Dict]:
        self._log("Fetching applications...")
        data = self._request("GET", "/applications", params={"page_number": 1})
        return data.get("responseList", [])

    def ensure_application(self, name: str) -> int:
        self._log(f"Checking Application '{name}' ...")
        apps = self.list_applications()
        for app in apps:
            if app.get("applicationName") == name:
                app_id = int(app["applicationId"])
                self._log(f"Application already exists. ID={app_id}")
                return app_id

        self._log(f"Creating application '{name}' ...")
        payload = {"applicationName": name}
        data = self._request("POST", "/applications", json_body=payload)
        app_id = data.get("applicationId")
        if app_id is None:
            self._error(f"Failed to create application: {data}")
        self._log(f"Application created. ID={app_id}")
        return int(app_id)

    def delete_application(self, app_id: int):
        self._log(f"Deleting application ID={app_id} ...")
        url = f"{self.api_base}/applications/{app_id}"
        try:
            resp = self.session.delete(
                url,
                headers=self._headers(),
                verify=self.verify_ssl,
            )
        except RequestException as e:
            self._error(f"Delete application failed: {e}")

        if resp.status_code not in (200, 204):
            try:
                data = resp.json()
            except json.JSONDecodeError:
                data = resp.text
            self._error(
                f"Delete application failed (HTTP {resp.status_code}): {data}"
            )
        self._log(f"Application ID={app_id} successfully deleted.")

    # ------------- environments -------------

    def list_environments_for_app(self, app_id: int) -> List[Dict]:
        self._log(f"Fetching environments for applicationId={app_id} ...")
        data = self._request(
            "GET",
            "/environments",
            params={"page_number": 1, "application_id": app_id},
        )
        return data.get("responseList", [])

    def ensure_environment(self, app_id: int, env_name: str) -> int:
        self._log(f"Checking Environment '{env_name}' for applicationId={app_id} ...")
        envs = self.list_environments_for_app(app_id)
        for env in envs:
            if env.get("environmentName") == env_name:
                env_id = int(env["environmentId"])
                self._log(f"Environment exists. ID={env_id}")
                return env_id

        self._log(f"Creating environment '{env_name}' ...")
        payload = {
            "environmentName": env_name,
            "applicationId": app_id,
            "purpose": "MASK",
        }
        data = self._request("POST", "/environments", json_body=payload)
        env_id = data.get("environmentId")
        if env_id is None:
            self._error(f"Failed to create environment: {data}")
        self._log(f"Environment created. ID={env_id}")
        return int(env_id)

    def delete_environment(self, env_id: int):
        self._log(f"Deleting environment ID={env_id} ...")
        url = f"{self.api_base}/environments/{env_id}"
        try:
            resp = self.session.delete(
                url,
                headers=self._headers(),
                verify=self.verify_ssl,
            )
        except RequestException as e:
            self._error(f"Delete environment failed: {e}")

        if resp.status_code not in (200, 204):
            try:
                data = resp.json()
            except json.JSONDecodeError:
                data = resp.text
            self._error(
                f"Delete environment failed (HTTP {resp.status_code}): {data}"
            )
        self._log(f"Environment ID={env_id} successfully deleted.")

    def list_all_environments_grouped(self) -> List[Tuple[int, str, int, str]]:
        """Returns list of (environmentId, environmentName,applicationId, applicationName)."""
        apps = self.list_applications()
        results: List[Tuple[int, str, int, str]] = []
        for app in apps:
            app_id = int(app["applicationId"])
            app_name = app["applicationName"]
            envs = self.list_environments_for_app(app_id)
            for env in envs:
                env_id = int(env["environmentId"])
                env_name = env["environmentName"]
                results.append((env_id, env_name, app_id, app_name))
        results.sort(key=lambda x: (x[0], x[2]))
        return results

    def list_applications(self) -> List[Dict]:
        """
        Return list of all applications from CE, sorted by applicationId.
        """
        self._log("Fetching applications...")
        data = self._request("GET", "/applications", params={"page_number": 1})
        apps = data.get("responseList", [])

        # Sort numerically by applicationId (CE returns them as strings)
        try:
            apps = sorted(apps, key=lambda a: int(a.get("applicationId", 0)))
        except Exception:
            # Fallback in case applicationId is missing or malformed
            apps = sorted(apps, key=lambda a: a.get("applicationId", ""))

        return apps


    # ------------- profile sets -------------

    def list_profile_sets(self) -> List[Dict]:
        self._log("Fetching profile sets...")
        data = self._request("GET", "/profile-sets", params={"page_number": 1})
        return data.get("responseList", [])

    # ------------- connectors -------------

    def list_connectors_for_env(self, env_id: int) -> List[Dict]:
        self._log(f"Fetching connectors for environmentId={env_id} ...")
        data = self._request(
            "GET",
            "/database-connectors",
            params={"page_number": 1, "environment_id": env_id},
        )
        return data.get("responseList", [])

    def find_connector_by_name(self, env_id: int, name: str) -> Optional[int]:
        connectors = self.list_connectors_for_env(env_id)
        for conn in connectors:
            if conn.get("connectorName") == name:
                return int(conn["databaseConnectorId"])
        return None

    def create_connector_oracle_native(
        self,
        name: str,
        env_id: int,
        host: str,
        port: int,
        sid: str,
        schema: str,
        username: str,
        password: str,
    ) -> int:
        self._log(f"Creating native Oracle connector '{name}' ...")
        payload = {
            "connectorName": name,
            "databaseType": "ORACLE",
            "environmentId": env_id,
            "host": host,
            "port": port,
            "schemaName": schema,
            "sid": sid,
            "username": username,
            "password": password,
        }
        data = self._request("POST", "/database-connectors", json_body=payload)
        conn_id = data.get("databaseConnectorId")
        if conn_id is None:
            self._error(f"Failed to create Oracle connector '{name}': {data}")
        self._log(f"Oracle connector '{name}' created. ID={conn_id}")
        return int(conn_id)

    def create_connector_oracle_jdbc(
        self,
        name: str,
        env_id: int,
        jdbc_url: str,
        schema: str,
        username: str,
        password: str,
    ) -> int:
        self._log(f"Creating JDBC Oracle connector '{name}' ...")
        self._log(f"Creating JDBC Oracle connector '{jdbc_url}' ...")
        payload = {
            "connectorName": name,
            "databaseType": "ORACLE",
            "environmentId": env_id,
            "jdbc": jdbc_url,
            "schemaName": schema,
            "username": username,
            "password": password,
            "kerberosAuth": False,
            "jdbcDriverId": 1,
            "enableLogger": False,
            "passwordVaultAuth": False,
        }
        data = self._request("POST", "/database-connectors", json_body=payload)
        conn_id = data.get("databaseConnectorId")
        if conn_id is None:
            self._error(f"Failed to create JDBC Oracle connector '{name}': {data}")
        self._log(f"JDBC Oracle connector '{name}' created. ID={conn_id}")
        return int(conn_id)

    def create_connector_mssql(
        self,
        name: str,
        env_id: int,
        host: str,
        port: int,
        database_name: str,
        schema: str,
        username: str,
        password: str,
    ) -> int:
        self._log(f"Creating MSSQL connector '{name}' ...")
        payload = {
            "connectorName": name,
            "databaseType": "MSSQL",
            "environmentId": env_id,
            "databaseName": database_name,
            "host": host,
            "port": port,
            "schemaName": schema,
            "username": username,
            "password": password,
            "kerberosAuth": False,
            "jdbcDriverId": 2,
            "enableLogger": False,
            "passwordVaultAuth": False,
        }
        data = self._request("POST", "/database-connectors", json_body=payload)
        conn_id = data.get("databaseConnectorId")
        if conn_id is None:
            self._error(f"Failed to create MSSQL connector '{name}': {data}")
        self._log(f"MSSQL connector '{name}' created. ID={conn_id}")
        return int(conn_id)

    def create_connector_postgres(
        self,
        name: str,
        env_id: int,
        host: str,
        port: int,
        database_name: str,
        schema: str,
        username: str,
        password: str,
    ) -> int:
        self._log(f"Creating PostgreSQL connector '{name}' ...")
        payload = {
            "connectorName": name,
            "databaseType": "POSTGRES",
            "environmentId": env_id,
            "databaseName": database_name,
            "host": host,
            "port": port,
            "schemaName": schema,
            "username": username,
            "password": password,
            "kerberosAuth": False,
            "jdbcDriverId": 5,
            "enableLogger": False,
            "passwordVaultAuth": False,
        }
        data = self._request("POST", "/database-connectors", json_body=payload)
        conn_id = data.get("databaseConnectorId")
        if conn_id is None:
            self._error(f"Failed to create PostgreSQL connector '{name}': {data}")
        self._log(f"PostgreSQL connector '{name}' created. ID={conn_id}")
        return int(conn_id)

    # ------------- rulesets & tables -------------

    def create_ruleset(self, connector_id: int, schema: str) -> int:
        ruleset_name = f"RULESET_{schema}"
        self._log(
            f"Creating ruleset '{ruleset_name}' for connectorId={connector_id} ..."
        )
        payload = {
            "rulesetName": ruleset_name,
            "databaseConnectorId": connector_id,
        }
        data = self._request("POST", "/database-rulesets", json_body=payload)
        rs_id = data.get("databaseRulesetId")
        if rs_id is None:
            self._error(f"Failed to create ruleset for connector {connector_id}: {data}")
        self._log(f"Ruleset created. ID={rs_id}")
        return int(rs_id)

    def bulk_add_tables_to_ruleset(self, ruleset_id: int, table_names: List[str]):
        if not table_names:
            self._log(
                f"No tables to add to ruleset {ruleset_id}; skipping bulk-table-update."
            )
            return
        self._log(
            f"Adding {len(table_names)} tables to ruleset {ruleset_id} via bulk-table-update ..."
        )
        table_metadata = [
            {"tableName": t, "rulesetId": ruleset_id} for t in table_names
        ]
        payload = {"tableMetadata": table_metadata}
        data = self._request(
            "PUT",
            f"/database-rulesets/{ruleset_id}/bulk-table-update",
            json_body=payload,
        )
        async_id = data.get("asyncTaskId")
        self._log(
            f"Bulk table update submitted for ruleset {ruleset_id}, asyncTaskId={async_id}"
        )

    # ------------- profile jobs & executions -------------

    def create_profile_job(
        self,
        ruleset_id: int,
        schema: str,
        profile_set_id: int,
    ) -> Optional[int]:
        job_name = f"PROFILEJOB_{schema}"
        desc = f"Profile job for schema {schema}, ruleset RULESET_{schema}"
        self._log(
            f"Creating profile job '{job_name}' (rulesetId={ruleset_id}, profileSetId={profile_set_id}) ..."
        )
        payload = {
            "jobName": job_name,
            "profileSetId": profile_set_id,
            "rulesetId": ruleset_id,
            "jobDescription": desc,
        }
        data = self._request("POST", "/profile-jobs", json_body=payload)
        job_id = data.get("profileJobId")
        if job_id is None:
            self._log(
                f"Failed to create profile job for schema {schema}: {data}"
            )
            return None
        self._log(f"Profile job created. ID={job_id}")
        return int(job_id)

    def list_profile_jobs_for_env(self, env_id: int) -> List[Dict]:
        self._log(f"Fetching profile jobs for environmentId={env_id} ...")
        data = self._request(
            "GET",
            "/profile-jobs",
            params={"page_number": 1, "environment_id": env_id},
        )
        return data.get("responseList", [])

    def start_profile_execution(self, job_id: int) -> int:
        self._log(f"Starting execution for profile jobId={job_id} ...")
        payload = {"jobId": job_id}
        data = self._request("POST", "/executions", json_body=payload)
        execution_id = data.get("executionId")
        status = data.get("status")
        if execution_id is None:
            self._error(f"Failed to start execution for job {job_id}: {data}")
        self._log(
            f"Execution started. executionId={execution_id}, initial status={status}"
        )
        return int(execution_id)

    def get_execution_status(self, execution_id: int) -> Dict:
        return self._request(
            "GET",
            f"/executions/{execution_id}",
        )

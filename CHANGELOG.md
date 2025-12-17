# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-11-17

### Added

- Initial public release of `dlpxdbprofiler`.
- Interactive CLI menu with operations:
  - Create/Ensure Application
  - Create/Ensure Environment
  - Create Connectors (+ Rulesets + Profile Jobs)
  - Create ALL (App + Env + Connectors + Rulesets + Profile Jobs)
  - Delete Environment
  - Delete Application
  - List all Applications
  - List all Environments
  - List all Schemas in database (Oracle or MSSQL)
  - List all Profile Sets
  - Run Profile jobs (single or all) for an environment
- Oracle target support:
  - Schema discovery using `oracledb` (thin mode).
  - Table discovery for a given schema.
  - Oracle native and JDBC connectors.
- MSSQL target support:
  - Schema and table discovery using `python-tds` (`pytds`).
  - MSSQL connectors using `databaseName` and `schemaName`.
- Automatic ruleset creation per connector and bulk table add.
- Automatic profile job creation per ruleset.
- Profile execution monitoring until `SUCCEEDED` / `FAILED` / `CANCELLED`.
- Logging to both console and `dlpxdbprofiler.log`.
- Environment variable support for CE, Oracle, MSSQL, and profile set ID.
- `--version` flag to print the current `dlpxdbprofiler` version.

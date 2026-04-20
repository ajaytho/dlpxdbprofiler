
# dlpxdbprofiler

`dlpxdbprofiler` is a standalone CLI utility designed to automate profiling across an entire database for the **Delphix Continuous Compliance Engine (Masking Engine)**.
It supports Oracle, MSSQL, PostgreSQL, and MySQL databases and performs:

- Application creation
- Environment creation
- Connector creation
- Ruleset creation
- Profile Job creation
- Listing metadata (Applications, Environments, Profile Sets, Database Schemas)
- Running Profile jobs (serial or **parallel**)
- Environment cleanup (delete env/app)

This README includes installation instructions, usage examples, environment variable configuration, and parallel‑execution documentation.

---

# 🚀 Features

### ✔ Works on:
- Linux (glibc 2.17 → CentOS/RHEL 7)
- Linux (modern/glibc ≥ 2.38)
- macOS (Intel & Apple Silicon)
- Windows 64‑bit
- **No Python required at runtime**  
- **No Oracle Client required** — uses python-oracledb thin mode by default. 
  - Thick mode supported via env var. Oracle Client must be installed separately. Oracle Instant Client supported.

### ✔ Supported Databases:
- **Oracle**
- **MSSQL**
- **PostgreSQL**
- **MySQL**

---

# 📦 Installation

Download your OS‑specific binary from the GitHub Releases page:

| OS | Binary |
|----|--------|
| Linux (universal glibc 2.17+) | `dlpxdbprofiler-linux` |
| Linux Modern glibc 2.38+ | `dlpxdbprofiler-linux-glibc2.38` |
| macOS | `dlpxdbprofiler-macos` |
| Windows | `dlpxdbprofiler-win64.exe` |

Then make it executable (Linux/macOS):

```bash
mv dlpxdbprofiler-linux dlpxdbprofiler # Rename file
chmod +x dlpxdbprofiler
```

---

# ⚙️ Environment Variables

dlpxdbprofiler allows running **non‑interactively** if environment variables are set.

## Compliance Engine
```
export DBP_CE_BASE_URL="http://your-mask-engine"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxx"
export DBP_CE_API_VERSION=v5.1.45
```

## Application and Environment (Optional)
```
export DBP_APPLICATION_NAME="Digital Bank CRM"
export DBP_ENVIRONMENT_NAME="Digital Bank CRM MASK"
```
⚠️ Note: If not set, you will be prompted to enter these values interactively.

## Oracle DB parameters
dlpxdbprofiler supports both SID and SERVICE_NAME, and they are mutually exclusive:  
✔ If SID is used → Native SID mode  
✔ If SERVICE_NAME is used → SERVICE mode  
✔ Internally constructs correct JDBC URL  

### Oracle (SID)
```
export DBP_ORACLE_HOST="10.10.10.10"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SID="ORCL"
export DBP_ORACLE_USER="hr"
export DBP_ORACLE_PASSWORD="xxxxxx"
```

This constructs:
``` 
jdbc:oracle:thin:@host:port/SID
```

### Oracle (SERVICE_NAME)
```
export DBP_ORACLE_HOST="10.10.10.10"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SERVICE_NAME="appservice"
export DBP_ORACLE_USER="hr"
export DBP_ORACLE_PASSWORD="xxxxxx"
```
This constructs:
``` 
jdbc:oracle:thin:@//host:port/service_name
```
⚠️ Note: SID and SERVICE_NAME cannot be set together.


## Oracle Thick Client ( If thick client is required. )
```
export DBP_ORACLE_DRIVER_MODE=thick
export DBP_ORACLE_CLIENT_LIB_DIR="/opt/homebrew/opt/instantclient-basic/lib"
```
In linux environment you may have to set `LD_LIBRARY_PATH` to point to the Oracle Instant Client lib directory.
```
export DBP_ORACLE_CLIENT_LIB_DIR="/path/to/instantclient"
export LD_LIBRARY_PATH="/path/to/instantclient:$LD_LIBRARY_PATH"
```

## MSSQL DB parameters
```
export DBP_MSSQL_HOST="10.10.10.10"
export DBP_MSSQL_PORT="1433"
export DBP_MSSQL_DATABASE="suitecrm-dev"
export DBP_MSSQL_USER="delphixdb"
export DBP_MSSQL_PASSWORD="xxxxxx"
```

## PostgreSQL DB parameters
```
export DBP_POSTGRES_HOST="10.10.10.10"
export DBP_POSTGRES_PORT="5432"
export DBP_POSTGRES_DATABASE="digitalbank"
export DBP_POSTGRES_SCHEMA="public"
export DBP_POSTGRES_USER="postgres"
export DBP_POSTGRES_PASSWORD="xxxxxx"
```

### PostgreSQL Connection Timeout (Optional)
```
export DBP_POSTGRES_CONNECT_TIMEOUT=60    # Connection timeout in seconds (default: 30)
```
⚠️ Note: If you experience connection timeouts due to network latency or firewall issues, increase this value.

## MySQL DB parameters
```
export DBP_MYSQL_HOST="10.10.10.10"
export DBP_MYSQL_PORT="3306"
export DBP_MYSQL_DATABASE="delphixdb"
export DBP_MYSQL_USER="root"
export DBP_MYSQL_PASSWORD="xxxxxx"
```

### MySQL Connection Timeout (Optional)
```
export DBP_MYSQL_CONNECT_TIMEOUT=60    # Connection timeout in seconds (default: 30)
```

## Profile Set
```
export DBP_PROFILE_SET_ID=4
```

## Degree of parallelism for profile jobs
```
export DBP_PROFILE_MAX_PARALLEL=3
```

## Operation Selection (Optional - for 100% Non-Interactive Mode)
```
export DBP_OPERATION=4    # or use descriptive names like "ALL"
```

Valid values:
- **Numeric**: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`
- **Descriptive**: `APP`, `ENV`, `CONNECTORS`, `ALL`, `DELETE_ENV`, `DELETE_APP`, `LIST_APPS`, `LIST_ENVS`, `LIST_PROFILE_SETS`, `LIST_SCHEMAS`, `RUN_PROFILE_JOBS`

Operation mapping:
- `1` or `APP` or `APPLICATION` = Create/Ensure Application
- `2` or `ENV` or `ENVIRONMENT` = Create/Ensure Environment
- `3` or `CONNECTORS` = Create Connectors (+ Rulesets + Profile Jobs)
- `4` or `ALL` = Create ALL (App + Env + Connectors + Rulesets + Profile Jobs)
- `5` or `DELETE_ENV` = DELETE Environment
- `6` or `DELETE_APP` = DELETE Application
- `7` or `LIST_APPS` = LIST Applications
- `8` or `LIST_ENVS` = LIST Environments
- `9` or `LIST_PROFILE_SETS` = LIST Profile Sets
- `10` or `LIST_SCHEMAS` = LIST all Schemas in database
- `11` or `RUN_PROFILE_JOBS` = Run Profile jobs (single or all) for environment

⚠️ **Note**: When `DBP_OPERATION` is set, the tool runs in **non-interactive mode**, executes the specified operation, and exits immediately. If not set, the interactive menu is displayed.

---

# ▶️ Running the Utility

## **Interactive Mode**

```bash
./dlpxdbprofiler
```

You will see the menu:

```
Starting dlpxdbprofiler v1.0.0

Select operation:
  1) Create/Ensure Application
  2) Create/Ensure Environment
  3) Create Connectors (+ Rulesets + Profile Jobs)
  4) Create ALL (App + Env + Connectors + Rulesets + Profile Jobs)
  5) DELETE Environment
  6) DELETE Application
  7) LIST all Applications
  8) LIST all eEvironments  
  9) LIST all Schemas in database
 10) LIST all Profile Sets
 11) Run profile jobs (single or all)
  0) Exit
```

You can enter options and follow prompts.

## **100% Non-Interactive Mode**

Set the `DBP_OPERATION` environment variable to run a specific operation without any prompts:

```bash
# Set all required environment variables
export DBP_CE_BASE_URL="http://your-mask-engine"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxx"
export DBP_CE_API_VERSION="v5.1.46"

export DBP_APPLICATION_NAME="My App"
export DBP_ENVIRONMENT_NAME="My Env"
export DBP_PROFILE_SET_ID=20

# Oracle configuration
export DBP_ORACLE_HOST="10.160.1.61"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SID="ORCL"
export DBP_ORACLE_USER="delphixdb"
export DBP_ORACLE_PASSWORD="xxxxxx"

# Database engine and connector scope
export DBP_DB_ENGINE="ORACLE"
export DBP_CONNECTOR_SCOPE="ALL"
export DBP_ORACLE_CONNECTOR_TYPE="NATIVE"

# Operation to run (no menu will be displayed)
export DBP_OPERATION="ALL"  # or use numeric: export DBP_OPERATION=4

# Run the tool - it will execute operation 4 and exit
./dlpxdbprofiler
```

The tool will:
1. Skip the interactive menu
2. Execute the specified operation
3. Exit immediately when complete

This is ideal for:
- CI/CD pipelines
- Automated scripts
- Scheduled jobs
- Docker containers

---

# ⚡ Parallel Execution of Profile Jobs

dlpxdbprofiler supports **parallel execution** of profile jobs.

### ✔ Default behavior  
Runs **serially** (1 job at a time)

### ✔ Enable Parallel Mode

There are **two ways**:

---

## 1️⃣ Using an environment variable (recommended)

```
export DBP_PROFILE_MAX_PARALLEL=3       # run max 3 profile jobs in parallel
```

---

## 2️⃣ When inside the menu → Option 10

You will be prompted:

```
Enter Degree Of Parallelism (DOP) [default: 1]:
```

Enter any value:

- `1`  → serial
- `2+` → parallel execution

The engine then schedules N jobs concurrently using a thread pool.

---

# 📘 Examples

## Example: Run all operations with env variables set

```
export DBP_CE_BASE_URL="http://your-mask-engine"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxx"
export DBP_CE_API_VERSION=v5.1.45

# Oracle DB parameters
export DBP_ORACLE_HOST="10.10.10.10"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SID="ORCL"
export DBP_ORACLE_USER="hr"
export DBP_ORACLE_PASSWORD="xxxxxx"

# Profile Set
export DBP_PROFILE_SET_ID=4

# Degree of parallelism for profile jobs
export DBP_PROFILE_MAX_PARALLEL=3

./dlpxdbprofiler
```

Then select:

```
4) Create ALL
11) RUN profile jobs
```

Jobs will run with *3 parallel workers*.

---

# 🔍 Checking Version

```
./dlpxdbprofiler --version
```

Example output:

```
dlpxdbprofiler 1.0.0
```

---

# 🧹 Cleanup Operations

## Delete Environment
```
Select option: 5
```

## Delete Application
```
Select option: 6
```

---

# 📋 Exclude List Feature

dlpxdbprofiler supports excluding specific tables from being added to rulesets using an exclude list file. This is useful for:
- Excluding system tables
- Skipping temporary tables
- Avoiding sensitive tables that shouldn't be profiled
- Filtering out backup or archive tables

## Setup

1. Create a file named `exclude_inventorylist.txt` in the same directory where you run dlpxdbprofiler
2. Add table patterns to exclude (one per line)
3. Run dlpxdbprofiler normally - it will automatically load and apply the exclusions

A sample configuration file `exclude_inventorylist.txt.sample` is provided with comprehensive examples.

## File Format

```
# Comments start with #
# Empty lines are ignored

# EXCLUDE MODE (default) - Tables matching these patterns will be excluded
DELPHIXDB.EMPLOYEES
HR.SALARY_INFO

# Exclude all tables in a schema
TEMP.*
STAGING.*

# Exclude specific table across all schemas
*.TEMP_TABLE
*.AUDIT_LOG

# INCLUDE-ONLY MODE (NEW!) - Prefix with ! to specify tables to INCLUDE
# Only tables matching these patterns will be included (all others excluded)
!*.DEMOCRM*           # Only include tables starting with DEMOCRM
!PRODUCTION.APP_*     # Only include APP_* tables in PRODUCTION schema

# MySQL: DATABASE.TABLE or just TABLE
mydb.users
audit_log

# Wildcards supported: * matches any characters
DELPHIXDB.TMP_*      # Tables starting with TMP_
*.*_BAK              # Tables ending with _BAK in any schema
*.*TEMP*             # Tables containing TEMP in any schema
```

## Pattern Rules

- **Case Sensitivity**: Patterns are case-sensitive but the matcher tries multiple case variations
- **Wildcards**: Use `*` to match zero or more characters
- **Schema Patterns**: 
  - `SCHEMA.TABLE` - Exact match
  - `SCHEMA.*` - All tables in schema
  - `*.TABLE` - Table in any schema
  - `*.*` - All tables (not recommended)
- **Table-only Patterns** (MySQL): 
  - `TABLE` - Treated as `*.TABLE`

## Examples

### Exclude Oracle System Schemas
```
SYS.*
SYSTEM.*
DBSNMP.*
MDSYS.*
```

### Exclude Temporary Tables
```
*.TMP_*
*.TEMP_*
*._TEMP
```

### Exclude Backup Tables
```
*.*_OLD
*.*_BACKUP
*.*_ARCHIVE
```

### Include-Only: Profile Only DemoCRM Tables (NEW!)
```
# Only include tables starting with DEMOCRM (all others excluded)
!*.DEMOCRM*
```

**Result:** Only `DEMOCRM_USERS`, `DEMOCRM_ORDERS`, etc. are profiled. All other tables are skipped.

### Include-Only: Profile Only Application Tables
```
# Only include application-specific tables
!*.MYAPP_*
!*.SHARED_*
```

### Include-Only with Additional Exclusions
```
# Include only DEMOCRM tables
!*.DEMOCRM*

# But exclude backup tables even if they match
*.*_BAK
*.*_BACKUP
```

**Result:** Profiles DEMOCRM tables except `DEMOCRM_DATA_BAK` (excluded by backup pattern).

## Pattern Rules

1. When dlpxdbprofiler starts connector creation, it looks for `exclude_inventorylist.txt` in the current directory
2. If found, it loads all patterns and logs them
3. For each schema/database being processed:
   - Lists all tables
   - Filters out tables matching any exclude pattern
   - Logs how many tables were excluded
   - **If all tables are excluded, skips connector/ruleset/profile job creation entirely for that schema**
   - Only creates connector, ruleset, and profile job if tables remain after filtering
   - Only adds remaining tables to the ruleset (if any remain)

## Logging

The tool logs exclude list operations:
```
2026-01-25 07:00:00 [INFO] Loading exclude list from /path/to/exclude_inventorylist.txt
2026-01-25 07:00:00 [INFO]   Exclude pattern: TEMP.*
2026-01-25 07:00:00 [INFO]   Exclude pattern: *.TMP_*
2026-01-25 07:00:00 [INFO] Loaded 2 exclude pattern(s) from exclude_inventorylist.txt
2026-01-25 07:00:01 [INFO] Excluded 5 table(s) from schema 'DELPHIXDB' based on exclude list. Remaining: 45
```

If no exclude file is found:
```
2026-01-25 07:00:00 [INFO] No exclude list file found at /path/to/exclude_inventorylist.txt. All tables will be included.
```

If all tables in a schema are excluded:
```
2026-01-25 07:00:01 [INFO] Excluded 15 table(s) from schema 'HR' based on exclude list. Remaining: 0
2026-01-25 07:00:01 [INFO] Skipping connector/ruleset/profile creation for schema HR - all tables were excluded by exclude list.
```
**Note**: No connector, ruleset, or profile job is created - the schema is completely skipped.

---

# 🔧 Troubleshooting

## Database Connection Timeout Errors

If you encounter connection timeout errors like:
```
Failed to connect to PostgreSQL postgres@10.160.1.74:5444/digitalbank: 
connection to server at "10.160.1.74", port 5444 failed: timeout expired
```

### Common Causes and Solutions:

1. **Network Connectivity Issues**
   - Verify the database host/IP is reachable: `ping <host>`
   - Check if the port is accessible: `telnet <host> <port>` or `nc -zv <host> <port>`
   - Ensure there are no firewall rules blocking the connection
   - If using VPN, ensure it's connected

2. **Incorrect Database Credentials**
   - Double-check the hostname, port, database name, and schema
   - Verify username and password are correct
   - Test connection using a database client (psql, sqlplus, etc.)

3. **Database Service Not Running**
   - Verify the database service is running on the target server
   - Check database logs for any issues

4. **Increase Connection Timeout**
   - For PostgreSQL, set a longer timeout:
     ```bash
     export DBP_POSTGRES_CONNECT_TIMEOUT=60  # 60 seconds
     ```
   - Default timeout is 30 seconds

### Error Handling

The application now provides helpful error messages when connection fails:
- Lists common troubleshooting steps
- Returns gracefully without crashing
- Allows you to re-run with corrected settings

---

# 📄 License

See [LICENSE](LICENSE)

---

# 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md)

---

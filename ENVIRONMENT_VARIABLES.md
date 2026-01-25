# Complete Environment Variables Reference

This document provides a comprehensive list of all environment variables supported by `dlpxdbprofiler` for automated, non-interactive operation.

---

## Compliance Engine Configuration

Required for connecting to the Delphix Compliance Engine (Masking Engine):

```bash
export DBP_CE_BASE_URL="http://your-mask-engine"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxx"
export DBP_CE_API_VERSION="v5.1.46"
```

---

## Application and Environment Configuration

**NEW!** Optional - Set these to avoid interactive prompts:

```bash
export DBP_APPLICATION_NAME="Digital Bank CRM"
export DBP_ENVIRONMENT_NAME="Digital Bank CRM MASK"
```

⚠️ **Note:** If not set, you will be prompted to enter these values interactively.

---

## Database Engine and Connector Scope Configuration

**NEW!** Optional - Set these to make the tool fully non-interactive:

```bash
# Database Engine Selection
# Values: ORACLE, MSSQL, POSTGRES, MYSQL (or 1, 2, 3, 4)
export DBP_DB_ENGINE="MYSQL"

# Connector Scope Selection
# Values: SCHEMA (single schema) or DB/ALL (all schemas)
# Can also use: 1 (single) or 2 (all)
export DBP_CONNECTOR_SCOPE="ALL"
```

⚠️ **Note:** If not set, you will be prompted to select these values interactively.

---

## Profile Set Configuration

Optional - Defaults to 4 if not set:

```bash
export DBP_PROFILE_SET_ID=4
```

---

## Oracle Database Configuration

Choose ONE of the following connection methods:

### Option 1: Using SID
```bash
export DBP_ORACLE_HOST="10.10.10.10"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SID="ORCL"
export DBP_ORACLE_USER="hr"
export DBP_ORACLE_PASSWORD="xxxxxx"
unset DBP_ORACLE_SERVICE_NAME
```

### Option 2: Using SERVICE_NAME
```bash
export DBP_ORACLE_HOST="10.10.10.10"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SERVICE_NAME="appservice"
export DBP_ORACLE_USER="hr"
export DBP_ORACLE_PASSWORD="xxxxxx"
unset DBP_ORACLE_SID
```

⚠️ **Important:** SID and SERVICE_NAME are mutually exclusive. Set only one.

### Oracle Thick Client (Optional)
```bash
export DBP_ORACLE_DRIVER_MODE="thick"
export DBP_ORACLE_CLIENT_LIB_DIR="/opt/homebrew/opt/instantclient-basic/lib"
```

### Oracle Connector Type (Optional)

**NEW!** Set this to avoid the interactive prompt for connector type selection:

```bash
# Oracle Connector Type Selection
# Values: NATIVE (default), JDBC (or 1, 2)
export DBP_ORACLE_CONNECTOR_TYPE="NATIVE"
```

⚠️ **Note:** If not set, you will be prompted to select the connector type interactively.

- **NATIVE** (or `1`): Uses native connector format `host/port/sid`
- **JDBC** (or `2`): Uses JDBC URL format `jdbc:oracle:thin:@//host:port/SID`

### Oracle Cryptography Settings

**Note:** The application automatically sets `CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1` to ensure compatibility with OpenSSL 3.x. This is handled internally and does not need to be set manually unless you want to override the default behavior.

```bash
# Only set this if you need to explicitly control legacy algorithm support
# Default: 1 (legacy algorithms disabled)
# export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1
```

---

## MSSQL Database Configuration

```bash
export DBP_MSSQL_HOST="10.10.10.10"
export DBP_MSSQL_PORT="1433"
export DBP_MSSQL_DATABASE="suitecrm-dev"
export DBP_MSSQL_USER="delphixdb"
export DBP_MSSQL_PASSWORD="xxxxxx"
```

---

## PostgreSQL Database Configuration

```bash
export DBP_POSTGRES_HOST="10.10.10.10"
export DBP_POSTGRES_PORT="5432"
export DBP_POSTGRES_DATABASE="digitalbank"
export DBP_POSTGRES_SCHEMA="public"
export DBP_POSTGRES_USER="postgres"
export DBP_POSTGRES_PASSWORD="xxxxxx"
export DBP_POSTGRES_CONNECT_TIMEOUT=60  # Default: 30 seconds
```

⚠️ **Note:** Increase this value if you experience connection timeouts due to network latency or firewall issues.

---

## MySQL Database Configuration

```bash
export DBP_MYSQL_HOST="10.10.10.10"
export DBP_MYSQL_PORT="3306"
export DBP_MYSQL_DATABASE="delphixdb"
export DBP_MYSQL_USER="root"
export DBP_MYSQL_PASSWORD="xxxxxx"
export DBP_MYSQL_CONNECT_TIMEOUT=60  # Default: 30 seconds
```

---

## Parallel Execution Configuration

Control the degree of parallelism for profile job execution:

```bash
export DBP_PROFILE_MAX_PARALLEL=3  # Default: 1 (serial execution)
```

---

## Complete Example: Fully Non-Interactive PostgreSQL Setup

```bash
#!/bin/bash

# Compliance Engine
export DBP_CE_BASE_URL="http://ajaytcc.example.com"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxxxx"
export DBP_CE_API_VERSION="v5.1.46"

# Application and Environment (NEW!)
export DBP_APPLICATION_NAME="Demo_CRM_App"
export DBP_ENVIRONMENT_NAME="Demo_CRM_Env"

# Database Engine and Connector Scope (NEW!)
export DBP_DB_ENGINE="POSTGRES"
export DBP_CONNECTOR_SCOPE="ALL"

# Profile Set
export DBP_PROFILE_SET_ID=4

# PostgreSQL Database
export DBP_POSTGRES_HOST="postgres.example.com"
export DBP_POSTGRES_PORT="5432"
export DBP_POSTGRES_DATABASE="digitalbank"
export DBP_POSTGRES_SCHEMA="public"
export DBP_POSTGRES_USER="postgres"
export DBP_POSTGRES_PASSWORD="postgres_password"

# Optional: Increase timeout for slow networks
export DBP_POSTGRES_CONNECT_TIMEOUT=60

# Optional: Enable parallel profile job execution
export DBP_PROFILE_MAX_PARALLEL=3

# Run the profiler
./dlpxdbprofiler
```

---

## Complete Example: Fully Non-Interactive Oracle Setup

```bash
#!/bin/bash

# Compliance Engine
export DBP_CE_BASE_URL="http://ajaytcc.example.com"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxxxx"
export DBP_CE_API_VERSION="v5.1.46"

# Application and Environment (NEW!)
export DBP_APPLICATION_NAME="Demo_CRM_App"
export DBP_ENVIRONMENT_NAME="Demo_CRM_Env"

# Database Engine and Connector Scope (NEW!)
export DBP_DB_ENGINE="ORACLE"
export DBP_CONNECTOR_SCOPE="ALL"

# Profile Set
export DBP_PROFILE_SET_ID=4

# Oracle Database (using SERVICE_NAME)
export DBP_ORACLE_HOST="oracle.example.com"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SERVICE_NAME="HRPROD"
export DBP_ORACLE_USER="hr_admin"
export DBP_ORACLE_PASSWORD="xxxxxxxx"

# Optional: Oracle connector type (NEW!)
export DBP_ORACLE_CONNECTOR_TYPE="NATIVE"

# Optional: Enable parallel profile job execution
export DBP_PROFILE_MAX_PARALLEL=5

# Run the profiler
./dlpxdbprofiler
```

---

## Complete Example: Fully Non-Interactive MSSQL Setup

```bash
#!/bin/bash

# Compliance Engine
export DBP_CE_BASE_URL="http://ajaytcc.example.com"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxxxx"
export DBP_CE_API_VERSION="v5.1.46"

# Application and Environment (NEW!)
export DBP_APPLICATION_NAME="Demo_CRM_App"
export DBP_ENVIRONMENT_NAME="Demo_CRM_Env"

# Database Engine and Connector Scope (NEW!)
export DBP_DB_ENGINE="MSSQL"
export DBP_CONNECTOR_SCOPE="ALL"

# Profile Set
export DBP_PROFILE_SET_ID=4

# MSSQL Database
export DBP_MSSQL_HOST="mssql.example.com"
export DBP_MSSQL_PORT="1433"
export DBP_MSSQL_DATABASE="CRM_UAT"
export DBP_MSSQL_USER="crm_user"
export DBP_MSSQL_PASSWORD="xxxxxxxx"

# Optional: Enable parallel profile job execution
export DBP_PROFILE_MAX_PARALLEL=2

# Run the profiler
./dlpxdbprofiler
```

---

## Complete Example: Fully Non-Interactive MySQL Setup

```bash
#!/bin/bash

# Compliance Engine
export DBP_CE_BASE_URL="http://ajaytcc.example.com"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="xxxxxxxx"
export DBP_CE_API_VERSION="v5.1.46"

# Application and Environment (NEW!)
export DBP_APPLICATION_NAME="Demo_CRM_App"
export DBP_ENVIRONMENT_NAME="Demo_CRM_Env"

# Database Engine and Connector Scope (NEW!)
export DBP_DB_ENGINE="MYSQL"
export DBP_CONNECTOR_SCOPE="ALL"

# Profile Set
export DBP_PROFILE_SET_ID=4

# MySQL Database
export DBP_MYSQL_HOST="mysql.example.com"
export DBP_MYSQL_PORT="3306"
export DBP_MYSQL_DATABASE="delphixdb"
export DBP_MYSQL_USER="root"
export DBP_MYSQL_PASSWORD="xxxxxxxx"

# Optional: Increase timeout for slow networks
export DBP_MYSQL_CONNECT_TIMEOUT=60

# Optional: Enable parallel profile job execution
export DBP_PROFILE_MAX_PARALLEL=2

# Run the profiler
./dlpxdbprofiler
```

---

## Environment Variable Loading Behavior

When you set environment variables:

1. **If environment variable is set:**
   - Value is loaded from the environment
   - Logs: `"<Name> loaded from environment variable <VAR>: <value>"`
   - No interactive prompt

2. **If environment variable is NOT set:**
   - User is prompted interactively
   - Logs: `"<Name> not found in environment variable <VAR>, prompting..."`
   - User enters value manually

3. **If environment variable has invalid value:**
   - Warning logged (for timeout values)
   - Falls back to default or prompts user

---

## Quick Reference Table

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `DBP_CE_BASE_URL` | Yes | - | Compliance Engine URL |
| `DBP_CE_USERNAME` | Yes | - | CE username |
| `DBP_CE_PASSWORD` | Yes | - | CE password |
| `DBP_CE_API_VERSION` | Yes | - | CE API version |
| `DBP_APPLICATION_NAME` | No | (prompt) | Application name |
| `DBP_ENVIRONMENT_NAME` | No | (prompt) | Environment name |
| `DBP_DB_ENGINE` | No | (prompt) | Database engine (ORACLE, MSSQL, POSTGRES, MYSQL or 1-4) |
| `DBP_CONNECTOR_SCOPE` | No | (prompt) | Connector scope (SCHEMA/SINGLE/1 or DB/ALL/2) |
| `DBP_PROFILE_SET_ID` | No | 20 | Profile set ID |
| `DBP_ORACLE_HOST` | Conditional | - | Oracle host |
| `DBP_ORACLE_PORT` | Conditional | - | Oracle port |
| `DBP_ORACLE_SID` | Conditional | - | Oracle SID (exclusive with SERVICE_NAME) |
| `DBP_ORACLE_SERVICE_NAME` | Conditional | - | Oracle service name (exclusive with SID) |
| `DBP_ORACLE_USER` | Conditional | - | Oracle username |
| `DBP_ORACLE_PASSWORD` | Conditional | - | Oracle password |
| `DBP_ORACLE_DRIVER_MODE` | No | thin | Oracle driver mode (thin/thick) |
| `DBP_ORACLE_CLIENT_LIB_DIR` | No | - | Oracle client library directory |
| `DBP_ORACLE_CONNECTOR_TYPE` | No | NATIVE | Oracle connector type (NATIVE/1 or JDBC/2) |
| `DBP_MSSQL_HOST` | Conditional | - | MSSQL host |
| `DBP_MSSQL_PORT` | Conditional | - | MSSQL port |
| `DBP_MSSQL_DATABASE` | Conditional | - | MSSQL database |
| `DBP_MSSQL_USER` | Conditional | - | MSSQL username |
| `DBP_MSSQL_PASSWORD` | Conditional | - | MSSQL password |
| `DBP_POSTGRES_HOST` | Conditional | - | PostgreSQL host |
| `DBP_POSTGRES_PORT` | Conditional | 5432 | PostgreSQL port |
| `DBP_POSTGRES_DATABASE` | Conditional | - | PostgreSQL database |
| `DBP_POSTGRES_SCHEMA` | Conditional | public | PostgreSQL schema |
| `DBP_POSTGRES_USER` | Conditional | - | PostgreSQL username |
| `DBP_POSTGRES_PASSWORD` | Conditional | - | PostgreSQL password |
| `DBP_POSTGRES_CONNECT_TIMEOUT` | No | 30 | PostgreSQL connection timeout (seconds) |
| `DBP_MYSQL_HOST` | Conditional | - | MySQL host |
| `DBP_MYSQL_PORT` | Conditional | 3306 | MySQL port |
| `DBP_MYSQL_DATABASE` | Conditional | - | MySQL database |
| `DBP_MYSQL_USER` | Conditional | - | MySQL username |
| `DBP_MYSQL_PASSWORD` | Conditional | - | MySQL password |
| `DBP_MYSQL_CONNECT_TIMEOUT` | No | 30 | MySQL connection timeout (seconds) |
| `DBP_PROFILE_MAX_PARALLEL` | No | 1 | Parallel profile job execution (1=serial) |

**Conditional:** Required when selecting that specific database engine.

---

## Troubleshooting

### "Application name not found in environment variable..."
- This is normal if `DBP_APPLICATION_NAME` is not set
- You will be prompted to enter it interactively
- To avoid the prompt, set the environment variable

### "Invalid DBP_POSTGRES_CONNECT_TIMEOUT value..."
- The timeout value must be a positive integer
- Example: `export DBP_POSTGRES_CONNECT_TIMEOUT=60`
- Do not use quotes or non-numeric values

### Connection Still Timing Out
- Increase `DBP_POSTGRES_CONNECT_TIMEOUT` to 60 or 90 seconds
- Check network connectivity: `ping <host>`
- Check port accessibility: `nc -zv <host> <port>`
- Verify firewall rules and VPN connection

---

## See Also

- [README.md](README.md) - Main documentation

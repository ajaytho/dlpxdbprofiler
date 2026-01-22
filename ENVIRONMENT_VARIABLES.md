# Complete Environment Variables Reference

This document provides a comprehensive list of all environment variables supported by `dlpxdbprofiler` for fully automated, non-interactive operation.

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

## Profile Set Configuration

Optional - Defaults to 20 if not set:

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
```

### Option 2: Using SERVICE_NAME
```bash
export DBP_ORACLE_HOST="10.10.10.10"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SERVICE_NAME="appservice"
export DBP_ORACLE_USER="hr"
export DBP_ORACLE_PASSWORD="xxxxxx"
```

⚠️ **Important:** SID and SERVICE_NAME are mutually exclusive. Set only one.

### Oracle Thick Client (Optional)
```bash
export DBP_ORACLE_DRIVER_MODE="thick"
export DBP_ORACLE_CLIENT_LIB_DIR="/opt/homebrew/opt/instantclient-basic/lib"
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
```

### PostgreSQL Connection Timeout (Optional)
**NEW!** Control connection timeout for slow networks:

```bash
export DBP_POSTGRES_CONNECT_TIMEOUT=60  # Default: 30 seconds
```

⚠️ **Note:** Increase this value if you experience connection timeouts due to network latency or firewall issues.

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
export DBP_CE_BASE_URL="http://uvo1ex5yozzx8l4494d.vm.cld.sr"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="MySecurePassword123"
export DBP_CE_API_VERSION="v5.1.46"

# Application and Environment (NEW!)
export DBP_APPLICATION_NAME="Digital Bank CRM"
export DBP_ENVIRONMENT_NAME="Digital Bank CRM MASK"

# Profile Set
export DBP_PROFILE_SET_ID=4

# PostgreSQL Database
export DBP_POSTGRES_HOST="10.160.1.74"
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
export DBP_CE_BASE_URL="http://your-mask-engine"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="admin_password"
export DBP_CE_API_VERSION="v5.1.46"

# Application and Environment (NEW!)
export DBP_APPLICATION_NAME="HR Application"
export DBP_ENVIRONMENT_NAME="HR Production"

# Profile Set
export DBP_PROFILE_SET_ID=20

# Oracle Database (using SERVICE_NAME)
export DBP_ORACLE_HOST="oracle.example.com"
export DBP_ORACLE_PORT="1521"
export DBP_ORACLE_SERVICE_NAME="HRPROD"
export DBP_ORACLE_USER="hr_admin"
export DBP_ORACLE_PASSWORD="oracle_password"

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
export DBP_CE_BASE_URL="http://your-mask-engine"
export DBP_CE_USERNAME="admin"
export DBP_CE_PASSWORD="admin_password"
export DBP_CE_API_VERSION="v5.1.46"

# Application and Environment (NEW!)
export DBP_APPLICATION_NAME="CRM System"
export DBP_ENVIRONMENT_NAME="CRM UAT"

# Profile Set
export DBP_PROFILE_SET_ID=4

# MSSQL Database
export DBP_MSSQL_HOST="mssql.example.com"
export DBP_MSSQL_PORT="1433"
export DBP_MSSQL_DATABASE="CRM_UAT"
export DBP_MSSQL_USER="crm_user"
export DBP_MSSQL_PASSWORD="mssql_password"

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
| `DBP_PROFILE_SET_ID` | No | 20 | Profile set ID |
| `DBP_ORACLE_HOST` | Conditional | - | Oracle host |
| `DBP_ORACLE_PORT` | Conditional | - | Oracle port |
| `DBP_ORACLE_SID` | Conditional | - | Oracle SID (exclusive with SERVICE_NAME) |
| `DBP_ORACLE_SERVICE_NAME` | Conditional | - | Oracle service name (exclusive with SID) |
| `DBP_ORACLE_USER` | Conditional | - | Oracle username |
| `DBP_ORACLE_PASSWORD` | Conditional | - | Oracle password |
| `DBP_ORACLE_DRIVER_MODE` | No | thin | Oracle driver mode (thin/thick) |
| `DBP_ORACLE_CLIENT_LIB_DIR` | No | - | Oracle client library directory |
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

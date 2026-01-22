
# dlpxdbprofiler

`dlpxdbprofiler` is a standalone CLI utility designed to automate profiling across an entire database for the **Delphix Continuous Compliance Engine (Masking Engine)**.
It supports Oracle, MSSQL, and PostgreSQL databases and performs:

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
  - Thick mode supported via env var. Oracle Client must be installed separately. Instant Client supported.

### ✔ Supported Databases:
- **Oracle**
- **MSSQL**
- **PostgreSQL**

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

## Profile Set
```
export DBP_PROFILE_SET_ID=4
```

## Degree of parallelism for profile jobs
```
export DBP_PROFILE_MAX_PARALLEL=3
```

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

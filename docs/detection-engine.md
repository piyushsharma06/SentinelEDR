# SentinelEDR YAML Detection Engine Specification

The SentinelEDR detection engine is designed for clear, testable, and explainable behavioral detection.

## 1. Rule Schema Definition

Each YAML detection rule adheres to the following structure:

```yaml
id: RULE-001-PARENT-CHILD
name: Suspicious Script Interpreter Spawned by Office or Web Application
description: Detailed description of the behavioral pattern...
severity: high # critical | high | medium | low | info
category: Execution
enabled: true
version: "1.0.0"
mitre_attack:
  technique_id: "T1059.001"
  technique_name: "Command and Scripting Interpreter: PowerShell"
  tactic: "Execution"
detection:
  event_type: "process_creation"
  logic: "all" # all | any
  conditions:
    - field: "parent_process_name"
      operator: "in"
      value:
        - "winword.exe"
        - "excel.exe"
    - field: "process_name"
      operator: "in"
      value:
        - "powershell.exe"
        - "cmd.exe"
rationale: |
  Why this activity is suspicious from an adversary perspective...
evidence_fields:
  - "process_id"
  - "process_name"
  - "command_line"
false_positive_notes: |
  Known legitimate administrative triggers...
```

---

## 2. Evaluation Operators

| Operator | Supported Types | Description |
| :--- | :--- | :--- |
| `equals` | string, int, float | Exact match (case-insensitive for strings) |
| `not_equals` | string, int, float | Value does not equal target |
| `in` | string in list | Target value is in candidate list |
| `not_in` | string in list | Target value is not in candidate list |
| `contains` | substring in string | Case-insensitive substring match |
| `matches_any_substring` | list of substrings | Any of the target substrings match the field |
| `matches_regex` | regex pattern | Regular expression search |
| `greater_than` | numeric | Numeric comparison `> value` |
| `less_than` | numeric | Numeric comparison `< value` |
| `not_in_cidr_or_local` | IP address | IP is not loopback, private, or in excluded list |

---

## 3. Included Detection Rules

### Rule A: Suspicious Parent-Child Process Relationship (`RULE-001-PARENT-CHILD`)
- **Event Type:** `process_creation`
- **Mitre Technique:** T1059.001 (Command and Scripting Interpreter: PowerShell)
- **Description:** Detects shells (`powershell.exe`, `cmd.exe`, `wscript.exe`) spawned by document apps (`winword.exe`, `excel.exe`) or web server workers.

### Rule B: Suspicious Script Command-Line Indicators (`RULE-002-SCRIPT-CLI-INDICATORS`)
- **Event Type:** `process_creation`
- **Mitre Technique:** T1059.001 (Execution Policy Bypass)
- **Description:** Detects stealth and evasion flags (`-enc`, `-encodedcommand`, `bypass`, `-w hidden`, `downloadstring`, `iex(`).

### Rule C: Unusual Process Execution Context (`RULE-003-UNUSUAL-EXEC-CONTEXT`)
- **Event Type:** `process_creation`
- **Mitre Technique:** T1036.005 (Masquerading: Match Legitimate Name or Location)
- **Description:** Detects executable binaries launching directly from user AppData, Temp, or Public folders (`\appdata\local\temp\`, `\users\public\`).

### Rule D: Suspicious Network Context (`RULE-004-SUSPICIOUS-NETWORK`)
- **Event Type:** `network_connection`
- **Mitre Technique:** T1071.001 (Web Protocols)
- **Description:** Detects outbound socket connections established directly by command shells or scripting utilities to external public IP addresses.

### Rule E: Monitored Directory Activity (`RULE-005-MONITORED-DIRECTORY-ANOMALY`)
- **Event Type:** `file_activity`
- **Mitre Technique:** T1486 (Data Encrypted for Impact)
- **Description:** Detects suspicious file extensions (`.locked`, `.crypto`, `.wnry`, `.vbs`, `.ps1`) in the designated honeypot directory.

### Rule F: Agent Health (`RULE-006-AGENT-HEALTH-ANOMALY`)
- **Event Type:** `agent_health`
- **Mitre Technique:** T1562.001 (Impair Defenses: Disable or Modify Tools)
- **Description:** Detects when an endpoint agent reports degraded health or consecutive collection errors exceeding thresholds.

---

## 4. Alert Deduplication Window

To prevent alert storms, the engine checks for existing open alerts matching `(rule_id, host_id)` within `ALERT_DEDUPLICATION_WINDOW_MINUTES` (default: 10 minutes):
1. If an existing alert exists: increments `event_count`, updates `last_seen`, appends the new event to evidence.
2. If no existing alert exists: generates a new `Alert` with status `new`.

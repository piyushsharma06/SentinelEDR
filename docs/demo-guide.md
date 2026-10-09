# SentinelEDR Safe Demo Guide & Analyst Walkthrough

This guide provides a hands-on walkthrough of SentinelEDR using the built-in deterministic synthetic demonstration dataset.

## 1. Seeding Synthetic Data

To populate the system with realistic simulated endpoints, attack chains, and cases:

```powershell
python -c "import sys; sys.path.insert(0, 'backend'); import app.demo.seed; app.demo.seed.main()"
```

Output highlights:
- **Enrolled Endpoints:** `FIN-WIN11-EXEC`, `ENG-WIN10-WS02`, `DMZ-WEB-SRV01`
- **Telemetry Events:** 9 normalized events (benign baseline + simulated attacks)
- **Alerts Generated:** 8 detection alerts across high, medium, and low severities
- **Incidents Seeded:** 2 pre-configured cases with timeline notes
- **Safety Guarantee:** All records are clearly flagged with `is_synthetic = true`.

---

## 2. Step-by-Step Analyst Triage Walkthrough

### Step 1: Log In to the SOC Dashboard
1. Open `http://localhost:5173` in your browser.
2. Sign in with the default credentials:
   - **Username:** `admin`
   - **Password:** `SentinelAdmin!2026Secure`
3. Notice the persistent amber **DEMO MODE** banner at the top of the screen.

### Step 2: Review Security Overview
1. Observe the KPI cards: Total Endpoints (3), Telemetry Events (9), Active Alerts, Open Incidents (2).
2. Review the **Telemetry & Detection Activity** timeline chart and the **Alerts by Severity** distribution.
3. Review the **Recent Detections** and **Live Event Stream**.

### Step 3: Investigate a Spearphishing Alert
1. Click **Alerts** in the sidebar.
2. Select the High-severity alert: **"Suspicious Script Interpreter Spawned by Office or Web Application"** on `HOST-DEMO-FIN01`.
3. In the **Alert Details** view:
   - Check the **MITRE ATT&CK Mapping**: `T1059.001 (Command and Scripting Interpreter: PowerShell)` under the `Execution` tactic.
   - Review the **Preserved Forensic Evidence Summary**: examine `parent_process_name: winword.exe` spawning `process_name: powershell.exe`.
   - Examine the **Associated Security Telemetry Events** table to inspect the exact command-line arguments.

### Step 4: Work the Incident Case
1. Click **View Incident** or navigate to **Incidents** in the sidebar.
2. Open case `INC-DEMO-PHISH-01`: *"Suspicious Office Macro Spawning PowerShell & Beaconing on FIN-WIN11-EXEC"*.
3. Review the collaborative investigation timeline notes posted by the analyst.
4. Add a new investigation note:
   - Type *"Memory artifact preserved. Quarantined infected workstation."* in the input box.
   - Click **Post Note** to append the entry with your username and timestamp.
5. Update the case status from `Investigating` to `Contained`.

### Step 5: Triage a False Positive
1. Navigate back to **Alerts**.
2. Open an alert you wish to close as a false positive.
3. Click the **False Positive** button.
4. Enter an explanation (e.g., *"Verified scheduled backup task"*).
5. Confirm. The alert status transitions to `false_positive` with your justification preserved.

---

## 3. Resetting Synthetic Data

Demo seeding is completely idempotent. To reset the demo state at any time, re-run:

```powershell
python -c "import sys; sys.path.insert(0, 'backend'); import app.demo.seed; app.demo.seed.main()"
```

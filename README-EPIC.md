
# Epic Clarity Add-on for FHIR Snapshot Agent

This add-on layers Epic note summarization and patient detail enrichment on top of the FHIR-based snapshot.

## What you get
- **DB connector** for Epic Clarity via ODBC (with a CSV mock fallback)
- **Queries** to pull key fields for PCP briefing (customize with your Epic analysts)
- **Lightweight summarizer** that strips boilerplate and surfaces high-signal sentences
- **Runner** that merges FHIR snapshot + Epic summaries into one PCP briefing

## Quick start (mock mode, no DB required)
```bash
python main_epic.py --data ../fhir-data --out ./out --mock_csv ./epic-mock
```

This will produce `out/<patient-id>-briefing.md` and `out/<patient-id>-briefing.json`.

## Connect to Clarity
1) Install deps:
```bash
python3 -m pip install pyodbc pandas
```
2) Ensure an ODBC DSN to Clarity is configured (or provide a connection string).
3) Put credentials in environment variables or a .env (not committed):
```
CLARITY_DSN=YourClarityDSN
CLARITY_UID=service_user
CLARITY_PWD=********
```
4) Run:
```bash
python main_epic.py --data ../fhir-data --dsn $CLARITY_DSN --uid $CLARITY_UID --pwd $CLARITY_PWD
```

## Notes on schema
Epic Clarity schemas vary by version and site. Work with an Epic analyst to map the placeholder query to your environment.
You are looking for tables or views that contain:
- Patient MRN and internal ID
- Encounter ID, type, start/end, department
- Note text, author, datetime, note type/class
- PCP and scheduling metadata

## Security
- Follow your org's HIPAA/PHI policies.
- Run this in a private network.
- Avoid exporting raw note text; keep only summaries + links to source.
- Log minimally and never print PHI to stdout in production.

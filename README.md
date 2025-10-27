
# FHIR Snapshot Agent (Python, no external deps)

This minimal agent:
- Loads FHIR-like JSON for each patient under `fhir-data/`
- Generates a focused clinical snapshot
- Polls for Encounter updates to simulate a "new encounter" event

## Quick start

```bash
python main.py --data ../fhir-data --once
```

or run the simple watcher:

```bash
python main.py --data ../fhir-data --watch
```

Outputs appear in `./out/` and also print to the console.

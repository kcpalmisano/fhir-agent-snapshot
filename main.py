
import argparse
import os
import time
from pathlib import Path
from src.loader import load_all_patients, load_patient_bundle
from src.snapshot import build_snapshot
from src.watcher import EncounterWatcher

def print_snapshot(patient_id, snapshot):
    print(f"\n===== Snapshot for {patient_id} =====")
    print("Key signals:")
    for s in snapshot['signals']:
        print(f" - {s}")
    print("\nIssues needing attention:")
    for i in snapshot['issues']:
        print(f" * {i}")
    print("\nVitals/Labs summary:")
    for k, v in snapshot['summary'].items():
        print(f" {k}: {v}")

def save_snapshot(out_dir, patient_id, snapshot):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{patient_id}-snapshot.json"
    path.write_text(__import__('json').dumps(snapshot, indent=2))
    return path

def run_once(data_dir, out_dir):
    patients = load_all_patients(data_dir)
    for pid in patients:
        bundle = load_patient_bundle(data_dir, pid)
        snapshot = build_snapshot(bundle)
        save_snapshot(out_dir, pid, snapshot)
        print_snapshot(pid, snapshot)

def run_watch(data_dir, out_dir, interval=3):
    watcher = EncounterWatcher(data_dir)
    print("Watching for new/updated encounters... Press Ctrl+C to stop.")
    try:
        while True:
            changed_pids = watcher.poll()
            for pid in changed_pids:
                bundle = load_patient_bundle(data_dir, pid)
                snapshot = build_snapshot(bundle)
                save_snapshot(out_dir, pid, snapshot)
                print_snapshot(pid, snapshot)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to fhir-data folder")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--watch", action="store_true", help="Watch for Encounter changes")
    parser.add_argument("--out", type=str, default="out", help="Output folder for snapshots")
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_dir = Path(args.out)

    if args.once:
        run_once(data_dir, out_dir)
    elif args.watch:
        run_watch(data_dir, out_dir)
    else:
        print("Specify --once or --watch")

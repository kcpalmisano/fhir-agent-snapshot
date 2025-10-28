
import argparse, os, json
from pathlib import Path
from src.loader import load_all_patients, load_patient_bundle
from src.snapshot import build_snapshot
from epic.clarity_client import ClarityClient
from notes.clean import normalize_note_text
from notes.summarizer_advanced import summarize_long_note
from notes.change_detector import detect_changes_between_notes
from notes.actions import extract_actions
from notes.markdown_template import render_briefing_md
from notes.markdown_template import render_briefing_md
from safety.evidence import collect_objective_evidence
from safety.overdue import check_post_ed_followup, check_lab_overdue
from safety.confidence import enrich_snapshot_issues

DEFAULT_SUMMARY_NOTES_LIMIT = 10

def build_briefing(bundle, epic_notes):
    snap = build_snapshot(bundle)
    summarized_notes = []
    for n in epic_notes:
        cleaned = normalize_note_text(n['note_text'])
        note_summary = summarize_long_note(cleaned, max_points=12)
        actions = extract_actions(cleaned)
        summarized_notes.append({
            'encounter_id': n.get('encounter_id'),
            'note_datetime': n.get('note_datetime'),
            'note_type': n.get('note_type'),
            'author': n.get('author'),
            'summary_points': note_summary,
            'actions': actions
        })

    change_block = {}
    if len(summarized_notes) >= 2:
        latest = summarized_notes[0]
        prior  = summarized_notes[1]
        change_block = detect_changes_between_notes(latest, prior)
    else:
        change_block = {'new_items': [], 'resolved_items': [], 'numeric_changes': [], 'regressions': [], 'improvements': []}

    evidence = collect_objective_evidence(bundle)
    enriched_issues = enrich_snapshot_issues(snap, evidence)
    overdue_flags = []
    overdue_flags += check_post_ed_followup(bundle.get('encounters', []), window_days=14)
    overdue_flags += check_lab_overdue(bundle, days=30)

    briefing = {
        'patientId': snap['patientId'],
        'name': snap['name'],
        'signals': snap['signals'],
        'issues': snap['issues'],
        'summary': snap['summary'],
        'changes': change_block,
        'recent_notes': summarized_notes,
        'issues_enriched': enriched_issues,
        'overdue_flags': overdue_flags
    }
    return briefing

def save_outputs(out_dir: Path, patient_id: str, briefing: dict):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{patient_id}-briefing.json").write_text(json.dumps(briefing, indent=2))
    (out_dir / f"{patient_id}-briefing.md").write_text(render_briefing_md(briefing))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Path to fhir-data folder")
    ap.add_argument("--dsn", help="ODBC DSN for Epic Clarity")
    ap.add_argument("--uid", help="DB username")
    ap.add_argument("--pwd", help="DB password")
    ap.add_argument("--mock_csv", help="Path to CSV folder for mock mode (if no DB)" )
    ap.add_argument("--out", default="out", help="Output folder")
    ap.add_argument("--limit", type=int, default=DEFAULT_SUMMARY_NOTES_LIMIT, help="Max recent notes to summarize")
    args = ap.parse_args()

    data_dir = Path(args.data)
    out_dir = Path(args.out)

    client = ClarityClient(dsn=args.dsn, uid=args.uid, pwd=args.pwd, mock_csv=args.mock_csv)

    for pid in load_all_patients(data_dir):
        bundle = load_patient_bundle(data_dir, pid)
        epic_notes = client.fetch_recent_notes(patient_id=pid, limit=args.limit)
        briefing = build_briefing(bundle, epic_notes)
        save_outputs(out_dir, pid, briefing)
        print(f"Wrote {pid}-briefing.md and .json")

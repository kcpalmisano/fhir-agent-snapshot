
import json
from pathlib import Path

def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text())

def list_patient_ids(data_dir: Path):
    return [p.name for p in data_dir.iterdir() if p.is_dir()]

def load_all_patients(data_dir: Path):
    return list_patient_ids(data_dir)

def load_patient_bundle(data_dir: Path, patient_id: str):
    pdir = data_dir / patient_id
    bundle = {
        'patient': load_json(pdir / 'Patient.json'),
        'conditions': load_json(pdir / 'Conditions.json') or [],
        'medications': load_json(pdir / 'Medications.json') or [],
        'allergies': load_json(pdir / 'Allergies.json') or [],
        'encounters': load_json(pdir / 'Encounters.json') or [],
        'observations': load_json(pdir / 'Observations.json') or [],
        'episodes': load_json(pdir / 'EpisodeOfCare.json') or {}
    }
    return bundle


from src.util import parse_dt
from datetime import timedelta, datetime

def _latest_encounter(encs):
    dated = []
    for e in encs:
        start = ((e.get('period') or {}).get('start'))
        dt = parse_dt(start)
        if dt:
            dated.append((dt, e))
    return sorted(dated, key=lambda x: x[0])[-1][1] if dated else None

def check_post_ed_followup(encounters, window_days=14):
    last = _latest_encounter(encounters or [])
    if not last:
        return []
    cls = (last.get('class') or {}).get('code','').upper()
    if cls != 'EMER':
        return []
    last_dt = parse_dt((last.get('period') or {}).get('start'))
    needed_by = (last_dt + timedelta(days=window_days)).date().isoformat() if last_dt else None
    for e in encounters:
        start = parse_dt((e.get('period') or {}).get('start'))
        if not start:
            continue
        if start > last_dt and ((e.get('class') or {}).get('code','').upper() in ['AMB','OBS']):
            return []
    return [{
        'text': f'Post-ED follow-up not documented within {window_days} days of {last_dt.date().isoformat()}',
        'confidence': 'medium',
        'evidence': [{
            'type': 'Encounter',
            'id': last.get('id'),
            'when': (last.get('period') or {}).get('start'),
            'detail': 'ED encounter'
        }],
        'category': 'follow_up',
        'needed_by': needed_by
    }]

def check_lab_overdue(bundle, days=30):
    meds = bundle.get('medications', [])
    on_diuretic = any('furosemide' in ((m.get('medicationCodeableConcept') or {}).get('text','')).lower() for m in meds)
    if not on_diuretic:
        return []
    observations = bundle.get('observations', [])
    # Look for potassium or BMP references
    def has_recent(obs, keywords):
        latest_dt = None
        for o in obs:
            code = (o.get('code') or {}).get('text','').lower()
            if any(k in code for k in keywords):
                dt = parse_dt(o.get('effectiveDateTime'))
                if dt and (latest_dt is None or dt > latest_dt):
                    latest_dt = dt
        return latest_dt
    latest_lab = has_recent(observations, ['potassium', 'basic metabolic', 'bmp'])
    if latest_lab is None:
        return [{
            'text': f'Electrolytes/BMP not found for patient on loop diuretic (check K+ within {days} days)',
            'confidence': 'medium',
            'evidence': [],
            'category': 'lab_overdue'
        }]
    if (datetime.utcnow() - latest_lab).days > days:
        return [{
            'text': f'Last electrolytes/BMP older than {days} days while on loop diuretic',
            'confidence': 'medium',
            'evidence': [],
            'category': 'lab_overdue'
        }]
    return []

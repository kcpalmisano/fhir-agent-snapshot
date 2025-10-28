
import re

NUM_PATTERNS = [
    ('bnp', r'\bbnp\b[^\d]*(\d+(?:\.\d+)?)'),
    ('a1c', r'\ba1c\b[^\d]*(\d+(?:\.\d+)?)'),
    ('weight', r'\bweight\b[^\d]*(\d+(?:\.\d+)?)')
]

IMPROV_TERMS = ['improved', 'better', 'resolved', 'stable']
WORSEN_TERMS = ['worsening', 'worse', 'increased', 'decompens', 'exacerb']

def _extract_numbers(points):
    vals = {}
    text = ' '.join(points).lower()
    for name, pat in NUM_PATTERNS:
        m = re.search(pat, text)
        if m:
            try:
                vals[name] = float(m.group(1))
            except:
                pass
    return vals

def _classify_trend(latest_text):
    low = latest_text.lower()
    if any(t in low for t in WORSEN_TERMS):
        return 'regression'
    if any(t in low for t in IMPROV_TERMS):
        return 'improvement'
    return None

def detect_changes_between_notes(latest_note: dict, prior_note: dict):
    latest_points = latest_note.get('summary_points', [])
    prior_points = prior_note.get('summary_points', [])

    set_latest = set([p.lower() for p in latest_points])
    set_prior = set([p.lower() for p in prior_points])

    new_items = [p for p in latest_points if p.lower() not in set_prior]
    resolved_items = [p for p in prior_points if p.lower() not in set_latest]

    latest_nums = _extract_numbers(latest_points)
    prior_nums = _extract_numbers(prior_points)
    num_changes = []
    for k in latest_nums:
        if k in prior_nums:
            delta = latest_nums[k] - prior_nums[k]
            if abs(delta) >= 0.5:
                num_changes.append({'metric': k, 'delta': delta, 'from': prior_nums[k], 'to': latest_nums[k]})

    trend = _classify_trend(' '.join(latest_points))

    return {
        'new_items': new_items,
        'resolved_items': resolved_items,
        'numeric_changes': num_changes,
        'regressions': latest_points if trend == 'regression' else [],
        'improvements': latest_points if trend == 'improvement' else []
    }

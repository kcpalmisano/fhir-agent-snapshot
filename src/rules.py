
from .util import parse_dt

ACE_ARB_KEYWORDS = ["pril", "sartan"]  # lisinopril, enalapril, losartan, valsartan

def has_hf(conditions):
    for c in conditions:
        txt = (c.get('code', {}) or {}).get('text', '').lower()
        if 'heart failure' in txt:
            return True
    return False

def on_ace_arb(medications):
    texts = [ (m.get('medicationCodeableConcept') or {}).get('text','').lower() for m in medications ]
    for t in texts:
        for kw in ACE_ARB_KEYWORDS:
            if kw in t:
                return True
    return False

def is_recent_ed(encounter):
    cls = (encounter.get('class') or {}).get('code', '').upper()
    reason = ' '.join([rc.get('text','') for rc in encounter.get('reasonCode', [])]).lower()
    return cls == 'EMER' or 'ed' in reason or 'emergency' in reason

def extract_numeric_obs(observations, name_contains):
    vals = []
    for o in observations:
        code_txt = (o.get('code') or {}).get('text','')
        if name_contains.lower() in code_txt.lower():
            v = ((o.get('valueQuantity') or {}).get('value', None))
            dt = parse_dt(o.get('effectiveDateTime'))
            if v is not None and dt is not None:
                vals.append({'value': float(v), 'dt': dt, 'id': o.get('id')})
    return sorted(vals, key=lambda x: x['dt'])

def evaluate_flags(bundle):
    issues = []
    signals = []

    conditions = bundle.get('conditions', [])
    meds = bundle.get('medications', [])
    encounters = bundle.get('encounters', [])
    observations = bundle.get('observations', [])

    # Heart failure care optimization
    if has_hf(conditions) and not on_ace_arb(meds):
        issues.append("No ACE/ARB documented for patient with HF")

    # Recent ED visit
    if encounters:
        last_enc = sorted(encounters, key=lambda e: (e.get('period',{}).get('start','') or ''))[-1]
        if is_recent_ed(last_enc):
            signals.append("Recent emergency encounter")

    # BNP
    bnp_series = extract_numeric_obs(observations, 'BNP')
    if bnp_series:
        latest_bnp = bnp_series[-1]['value']
        signals.append(f"Latest BNP {latest_bnp} pg/mL")
        if latest_bnp >= 300:
            issues.append("Elevated BNP; evaluate volume status and HF control")

    # A1c
    a1c_series = extract_numeric_obs(observations, 'A1c')
    if a1c_series:
        latest_a1c = a1c_series[-1]['value']
        signals.append(f"Latest A1c {latest_a1c}%")
        if latest_a1c >= 8.0:
            issues.append("Poor glycemic control (A1c ≥ 8.0%)")

    # Weight trend
    wt_series = extract_numeric_obs(observations, 'weight')
    if len(wt_series) >= 2:
        delta = wt_series[-1]['value'] - wt_series[-2]['value']
        signals.append(f"Weight change {delta:+.1f} since last measurement")
        if delta >= 2.0:
            issues.append("Rapid weight gain; consider HF exacerbation")

    return signals, issues

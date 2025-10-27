
from .rules import evaluate_flags
from .util import parse_dt

def summarize(observations):
    def latest_val(name):
        vals = []
        for o in observations:
            code = (o.get('code') or {}).get('text','')
            if name.lower() in code.lower():
                v = ((o.get('valueQuantity') or {}).get('value', None))
                if v is not None:
                    dt = parse_dt(o.get('effectiveDateTime'))
                    if dt:
                        vals.append((dt, v))
        if not vals:
            return None
        return sorted(vals, key=lambda x: x[0])[-1][1]

    return {
        'BNP': latest_val('BNP'),
        'A1c': latest_val('A1c'),
        'Weight(kg)': latest_val('weight'),
    }

def build_snapshot(bundle):
    patient = bundle.get('patient', {})
    pid = patient.get('id','unknown')
    name = ''
    n = (patient.get('name') or [{}])[0]
    name = f"{(n.get('given') or [''])[0]} {(n.get('family') or '')}".strip()

    signals, issues = evaluate_flags(bundle)
    return {
        'patientId': pid,
        'name': name,
        'signals': signals,
        'issues': issues,
        'summary': summarize(bundle.get('observations', []))
    }

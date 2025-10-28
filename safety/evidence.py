
from src.util import parse_dt
def extract_observation_series(observations, label):
    series = []
    for o in observations:
        code = (o.get('code') or {}).get('text','')
        if label.lower() in code.lower():
            dt = parse_dt(o.get('effectiveDateTime'))
            val = ((o.get('valueQuantity') or {}).get('value', None))
            if dt and val is not None:
                series.append({
                    'id': o.get('id'),
                    'when': dt.isoformat(),
                    'value': float(val),
                    'unit': (o.get('valueQuantity') or {}).get('unit','')
                })
    series = sorted(series, key=lambda x: x['when'])
    latest = series[-1] if series else None
    prior = series[-2] if len(series) >= 2 else None
    return {'series': series, 'latest': latest, 'prior': prior}

def collect_objective_evidence(bundle):
    obs = bundle.get('observations', [])
    out = {}
    out['BNP'] = extract_observation_series(obs, 'BNP')
    out['A1c'] = extract_observation_series(obs, 'A1c')
    out['Weight'] = extract_observation_series(obs, 'weight')
    return out

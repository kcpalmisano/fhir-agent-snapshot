
from datetime import datetime

def parse_dt(s):
    # Accept 'YYYY-MM-DD' or ISO with time; fallback to None
    if not s:
        return None
    fmts = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            pass
    return None

def latest(items, key):
    items = [i for i in items if key(i) is not None]
    if not items:
        return None
    return sorted(items, key=key)[-1]

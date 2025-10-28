
import re

ACTION_PATTERNS = [
    r'\b(start|stop|increase|decrease|change|continue|hold|resume|titrate)\b.*',
    r'\b(refer|consult)\b.*',
    r'\b(order|repeat)\b.*(lab|test|imaging|echo|bmp|cmp|a1c|bnp).*',
    r'\b(follow up|follow-up|schedule|arrange)\b.*'
]

def extract_actions(text: str):
    actions = []
    for line in text.splitlines():
        low = line.strip()
        if not low:
            continue
        for pat in ACTION_PATTERNS:
            if re.search(pat, low, flags=re.IGNORECASE):
                actions.append(line.strip())
                break
    seen = set()
    out = []
    for a in actions:
        key = re.sub(r'\s+', ' ', a.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out[:10]

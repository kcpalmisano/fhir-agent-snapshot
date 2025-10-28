
import re

SECTION_PRIORITIES = {
    'assessment': 3.0,
    'plan': 3.0,
    'impression': 2.5,
    'hospital course': 2.0,
    'ed course': 2.0,
    'discharge': 2.0,
    'history of present illness': 1.5,
    'hpi': 1.5
}

ACTION_TERMS = [
    'start', 'stop', 'increase', 'decrease', 'change', 'continue',
    'hold', 'resume', 'titrate', 'begin', 'initiate', 'discontinue',
    'follow up', 'schedule', 'arrange', 'refer', 'consult', 'order'
]

CLINICAL_TERMS = [
    'shortness of breath', 'dyspnea', 'edema', 'orthopnea',
    'bnp', 'a1c', 'weight', 'creatinine', 'gfr', 'potassium',
    'bp ', 'blood pressure', 'tachy', 'fever', 'saturation', 'hypoxia',
    'worsening', 'improved', 'stable'
]

def split_sections(text: str):
    lines = text.splitlines()
    sections = [{'name': 'unknown', 'content': []}]
    for line in lines:
        l = line.strip()
        low = l.lower()
        if re.match(r'^(assessment|plan|impression|hospital course|ed course|discharge|history of present illness|hpi)[:\-\s]*$', low):
            sections.append({'name': low.split(':')[0], 'content': []})
        else:
            sections[-1]['content'].append(l)
    for s in sections:
        s['text'] = '\n'.join(s['content']).strip()
    return [s for s in sections if s['text']]

def sentence_split(text: str):
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def score_sentence(sent: str, section_name: str):
    if not sent or len(sent) < 7:
        return 0.0
    score = 0.0
    low = sent.lower()
    score += SECTION_PRIORITIES.get(section_name, 1.0)
    for t in ACTION_TERMS:
        if t in low:
            score += 2.0
    for t in CLINICAL_TERMS:
        if t in low:
            score += 1.5
    if re.search(r'\b\d+(\.\d+)?\b', sent):
        score += 0.8
    if any(u in low for u in [' mg', ' kg', ' mmhg', '%', ' pg/ml']):
        score += 0.5
    score += min(len(sent) / 200.0, 1.0)
    return score

def dedupe_keep_order(items):
    seen = set()
    out = []
    for it in items:
        norm = re.sub(r'\s+', ' ', it.lower())
        if norm in seen:
            continue
        seen.add(norm)
        out.append(it)
    return out

def summarize_long_note(text: str, max_points=12):
    sections = split_sections(text or '')
    if not sections:
        sections = [{'name':'unknown', 'text': text or ''}]
    scored = []
    for sec in sections:
        sec_name = sec['name']
        for s in sentence_split(sec['text']):
            scored.append((score_sentence(s, sec_name), s))
    ranked = [s for sc, s in sorted(scored, key=lambda x: x[0], reverse=True)]
    ranked = dedupe_keep_order(ranked)
    return ranked[:max_points]

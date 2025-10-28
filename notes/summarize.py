
import re

KEY_TERMS = [
    'assessment', 'plan', 'impression', 'diagnosis', 'discharge', 'follow up',
    'medication', 'dose', 'change', 'started', 'stopped', 'increased', 'decreased',
    'shortness of breath', 'edema', 'weight', 'bnp', 'a1c', 'bp ', 'blood pressure',
    'worsening', 'improved', 'stable', 'abnormal', 'critical', 'urgent', 'return to ed'
]

def score_sentence(sent: str) -> float:
    s = sent.strip()
    if not s or len(s) < 8:
        return 0.0
    score = 0.0
    low = s.lower()
    for term in KEY_TERMS:
        if term in low:
            score += 2.0
    score += min(len(s) / 200.0, 1.0)
    if re.search(r"\b\d+\b", s):
        score += 0.5
    return score

def split_into_sentences(text: str):
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]

def extract_key_points(text: str, max_points=8):
    sents = split_into_sentences(text)
    ranked = sorted(sents, key=score_sentence, reverse=True)
    seen = set()
    key_points = []
    for s in ranked:
        norm = re.sub(r"\s+", " ", s.lower())
        if norm in seen:
            continue
        seen.add(norm)
        key_points.append(s)
        if len(key_points) >= max_points:
            break
    return key_points

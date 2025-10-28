
import re

def normalize_note_text(text: str) -> str:
    t = text or ""
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = t.replace("\t", " ")
    lines = []
    for line in t.splitlines():
        s = line.strip()
        if not s:
            lines.append("")
            continue
        low = s.lower()
        # Skip common headings
        skip_prefixes = [
            "chief complaint:", "review of systems:", "past medical history:",
            "allergies:", "medications:", "signature:"
        ]
        if any(low.startswith(p) for p in skip_prefixes):
            continue
        lines.append(s)
    return "\n".join(lines)


def _format_evidence(ev_list):
    lines = []
    for e in ev_list or []:
        ref = f"{e.get('type','')}/{e.get('id','')}" if e.get('id') else e.get('type','')
        when = e.get('when', '')
        detail = e.get('detail', '')
        parts = [p for p in [ref, when, detail] if p]
        lines.append("; ".join(parts))
    return lines

def render_briefing_md(briefing: dict) -> str:
    name = briefing.get('name', 'Unknown')
    pid  = briefing.get('patientId', 'unknown')
    parts = []
    parts.append(f"# PCP Clinical Briefing — {name} ({pid})\n")
    sig = briefing.get('signals', [])
    if sig:
        parts.append("## Today’s Key Signals")
        for s in sig:
            parts.append(f"- {s}")
        parts.append("")
    enriched_issues = briefing.get('issues_enriched') or []
    if enriched_issues:
        parts.append("## Issues Requiring Action")
        for it in enriched_issues:
            parts.append(f"- {it['text']}  ")
            parts.append(f"  Confidence: **{it['confidence']}**")
            ev_lines = _format_evidence(it.get('evidence'))
            if ev_lines:
                parts.append("  Evidence:")
                for l in ev_lines:
                    parts.append(f"  - {l}")
        parts.append("")
    overdue = briefing.get('overdue_flags') or []
    if overdue:
        parts.append("## Safety Net Checks")
        for it in overdue:
            parts.append(f"- {it['text']}")
            parts.append(f"  Confidence: **{it['confidence']}**")
            ev_lines = _format_evidence(it.get('evidence'))
            if ev_lines:
                parts.append("  Evidence:")
                for l in ev_lines:
                    parts.append(f"  - {l}")
        parts.append("")
    ch = briefing.get('changes', {}) or {}
    if any(ch.get(k) for k in ['new_items','resolved_items','numeric_changes','regressions','improvements']):
        parts.append("## Changes Since Last Note")
        if ch.get('numeric_changes'):
            for n in ch['numeric_changes']:
                parts.append(f"- {n['metric'].upper()} {n['from']} → {n['to']} (Δ {n['delta']:+.1f})")
        if ch.get('new_items'):
            parts.append("- New items:")
            for it in ch['new_items'][:5]:
                parts.append(f"  - {it}")
        if ch.get('resolved_items'):
            parts.append("- Resolved items:")
            for it in ch['resolved_items'][:5]:
                parts.append(f"  - {it}")
        parts.append("")
    notes = briefing.get('recent_notes', [])
    if notes:
        parts.append("## Recent Note Highlights (last {} notes)".format(len(notes)))
        for n in notes[:10]:
            header = f"- {n.get('note_datetime','')} • {n.get('note_type','')} • {n.get('author','')} (enc {n.get('encounter_id','')})"
            parts.append(header)
            if n.get('summary_points'):
                for p in n['summary_points'][:8]:
                    parts.append(f"  - {p}")
            if n.get('actions'):
                parts.append("  - **Action items:**")
                for a in n['actions'][:5]:
                    parts.append(f"    - {a}")
            parts.append("")
    parts.append("## Latest Objective Data")
    for k, v in (briefing.get('summary') or {}).items():
        parts.append(f"- **{k}**: {v}")
    parts.append("")
    return "\n".join(parts)

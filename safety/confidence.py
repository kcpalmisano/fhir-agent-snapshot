
def label_issue_with_objective(issue_text, evidence_obj):
    txt = issue_text.lower()
    if 'bnp' in txt and evidence_obj.get('BNP',{}).get('latest'):
        return 'high'
    if 'a1c' in txt and evidence_obj.get('A1c',{}).get('latest'):
        return 'high'
    if 'weight' in txt and evidence_obj.get('Weight',{}).get('latest'):
        return 'high'
    return 'medium'

def enrich_snapshot_issues(snapshot, evidence):
    enriched = []
    for raw in snapshot.get('issues', []):
        conf = label_issue_with_objective(raw, evidence)
        ev = []
        low = raw.lower()
        if 'bnp' in low and evidence.get('BNP',{}).get('latest'):
            ev.append({'type':'Observation','id':evidence['BNP']['latest']['id'],'when':evidence['BNP']['latest']['when'],'detail':'BNP latest'})
            if evidence['BNP'].get('prior'):
                ev.append({'type':'Observation','id':evidence['BNP']['prior']['id'],'when':evidence['BNP']['prior']['when'],'detail':'BNP prior'})
        if 'a1c' in low and evidence.get('A1c',{}).get('latest'):
            ev.append({'type':'Observation','id':evidence['A1c']['latest']['id'],'when':evidence['A1c']['latest']['when'],'detail':'A1c latest'})
        if 'weight' in low and evidence.get('Weight',{}).get('latest'):
            ev.append({'type':'Observation','id':evidence['Weight']['latest']['id'],'when':evidence['Weight']['latest']['when'],'detail':'Weight latest'})
        enriched.append({'text': raw, 'confidence': conf, 'evidence': ev, 'category': 'issue'})
    return enriched

"""NyxOS Risk Engine (skeleton)

Risk = f(severity, asset_criticality, exposure, confidence, evidence)
"""
SEVERITY = {"info":1, "low":2, "medium":3, "high":4, "critical":5}

def compute_risk(severity, asset_criticality=3, exposure=3, confidence=3, has_evidence=True):
    s = SEVERITY.get(severity.lower(), 1)
    score = (s/5)*6 + (asset_criticality/5)*1.5 + (exposure/5)*1.5 + (confidence/5)*1.0
    if not has_evidence:
        score *= 0.8
    return round(min(score, 10.0), 2)

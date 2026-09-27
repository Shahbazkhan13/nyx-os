"""NyxOS Risk Engine (skeleton)

Risk = f(severity, asset_criticality, exposure, confidence, evidence)
"""
SEVERITY = {"info":1, "low":2, "medium":3, "high":4, "critical":5}

def compute_risk(severity, asset_criticality=3, exposure=3, confidence=3, has_evidence=True):
    s = SEVERITY.get(severity.lower(), 1)
    base = (s * 0.4) + (asset_criticality * 0.2) + (exposure * 0.2) + (confidence * 0.2)
    score = base * 2  # scale to 10
    if not has_evidence:
        score *= 0.8
    return round(min(score, 10.0), 2)

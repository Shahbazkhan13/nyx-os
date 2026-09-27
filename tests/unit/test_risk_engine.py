"""Unit tests for Risk Engine"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from core.risk.engine import compute_risk

def test_low_risk():
    assert compute_risk("low") < 5

def test_critical_risk():
    assert compute_risk("critical") >= 6

def test_no_evidence_reduces_score():
    with_ev = compute_risk("high", has_evidence=True)
    without_ev = compute_risk("high", has_evidence=False)
    assert without_ev < with_ev

def test_max_score():
    assert compute_risk("critical", 5, 5, 5) <= 10.0

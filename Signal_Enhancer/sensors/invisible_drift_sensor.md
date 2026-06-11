INVISIBLE DRIFT SENSOR

Purpose:
Detect changes not visible at the object level.

Detects:
- assumption drift
- trust drift
- dependency drift
- authority drift
- relationship drift
- standing formation
- interpretation drift

Primary question:
What is changing while the object appears stable?

Outputs:
- drift_candidate
- hidden_drift_candidate
- authority_drift_candidate
- dependency_drift_candidate
- standing_drift_candidate
- no_visible_drift
- drift_unknown

Boundary:
Drift candidate ≠ confirmed drift.
Invisible drift detection requires inspection.

UNKNOWN → HOLD
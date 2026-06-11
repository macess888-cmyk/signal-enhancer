MOVEMENT SENSOR

Purpose:
Detect movement direction across signal fields.

Detects:
- forward movement
- reverse movement
- lateral movement
- recursive movement
- hidden movement
- multi-directional movement

Primary question:
Where is the signal moving?

Outputs:
- movement_forward
- movement_reverse
- movement_lateral
- movement_recursive
- movement_hidden
- movement_multi_directional
- movement_unknown

Boundary:
Movement detection does not grant direction authority.
Observed movement ≠ permitted movement.

UNKNOWN → HOLD
PHASE SENSOR

Purpose:
Detect transitions between states.

State path:
stable
↓
forming
↓
transition
↓
drift
↓
rupture
↓
reformation

Detects:
- early formation
- transition pressure
- phase instability
- state rupture
- reformation after rupture

Primary question:
Is the system changing phase?

Outputs:
- phase_stable
- phase_forming
- phase_transition
- phase_drift
- phase_rupture
- phase_reformation
- phase_unknown

Boundary:
Phase detection is not phase authorization.
Observed transition ≠ legitimate transition.

UNKNOWN → HOLD
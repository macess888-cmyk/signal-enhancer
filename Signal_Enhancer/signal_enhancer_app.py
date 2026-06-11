import streamlit as st
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Signal Enhancer v0.1", layout="wide")

BASE = Path(__file__).parent
TELEMETRY = BASE / "telemetry"
TELEMETRY.mkdir(exist_ok=True)

st.title("Signal Enhancer v0.1")
st.caption("Observation ≠ Authority | Signal ≠ Decision | UNKNOWN → HOLD")

# Sidebar: Observation History
st.sidebar.title("Observation History")

obs_files = sorted(
    TELEMETRY.glob("observation_*.md"),
    key=lambda f: f.stat().st_mtime,
    reverse=True,
)

if obs_files:
    selected_obs = st.sidebar.selectbox(
        "Saved Observations",
        [f.name for f in obs_files],
    )

    if st.sidebar.button("Load Observation"):
        loaded = (TELEMETRY / selected_obs).read_text(encoding="utf-8")
        st.sidebar.success("Observation loaded")

        with st.expander("Loaded Observation", expanded=True):
            st.text(loaded)
else:
    st.sidebar.info("No saved observations yet.")

st.divider()

# Main input
target = st.text_input("Observation Target")
source_text = st.text_area("Paste target text / post / discussion here", height=220)

st.divider()

st.subheader("Sensor Review")

col1, col2 = st.columns(2)

with col1:
    pulse = st.selectbox("Pulse", [
        "pulse_unknown", "pulse_stable", "pulse_accelerating",
        "pulse_decelerating", "pulse_irregular", "pulse_interrupted"
    ])

    movement = st.selectbox("Movement", [
        "movement_unknown", "movement_forward", "movement_reverse",
        "movement_lateral", "movement_recursive", "movement_hidden",
        "movement_multi_directional"
    ])

    phase = st.selectbox("Phase", [
        "phase_unknown", "phase_stable", "phase_forming",
        "phase_transition", "phase_drift", "phase_rupture",
        "phase_reformation"
    ])

    relationship = st.selectbox("Relationship", [
        "relationship_unknown", "relationship_forming",
        "relationship_strengthening", "relationship_stable",
        "relationship_weakening", "relationship_dependency_candidate",
        "relationship_standing_candidate"
    ])

with col2:
    boundary = st.selectbox("Boundary", [
        "boundary_unknown", "boundary_stable", "boundary_forming",
        "boundary_weakening", "boundary_relocating",
        "boundary_bypassed", "boundary_reconstructed"
    ])

    pressure = st.selectbox("Pressure", [
        "pressure_unknown", "pressure_stable", "pressure_forming",
        "pressure_accumulating", "pressure_relocating",
        "pressure_concentrated", "pressure_amplified",
        "pressure_released"
    ])

    standing = st.selectbox("Standing", [
        "standing_unknown", "standing_candidate",
        "standing_accumulating", "standing_persistent",
        "standing_protected", "authority_like_standing_candidate"
    ])

    horizon = st.selectbox("Consequence Horizon", [
        "horizon_unknown", "horizon_expanding", "horizon_stable",
        "horizon_forming", "horizon_visible",
        "horizon_shrinking", "horizon_critical"
    ])

notes = st.text_area("Observation Notes", height=160)

if st.button("Generate Observation Record"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = target.strip().replace(" ", "_").lower() or "untitled"
    filename = TELEMETRY / f"observation_{safe_target}_{timestamp}.md"

    content = f"""SIGNAL ENHANCER OBSERVATION

Date:
{datetime.now().isoformat(timespec="seconds")}

Target:
{target}

Authority:
NONE

Promotion:
NONE

Invariant:
NOT ESTABLISHED

UNKNOWN → HOLD

────────────────────────────────────

SOURCE TEXT

{source_text}

────────────────────────────────────

PULSE

{pulse}

────────────────────────────────────

MOVEMENT

{movement}

────────────────────────────────────

PHASE

{phase}

────────────────────────────────────

RELATIONSHIP

{relationship}

────────────────────────────────────

BOUNDARY

{boundary}

────────────────────────────────────

PRESSURE

{pressure}

────────────────────────────────────

STANDING

{standing}

────────────────────────────────────

CONSEQUENCE HORIZON

{horizon}

────────────────────────────────────

NOTES

{notes}

────────────────────────────────────

BOUNDARY

This record observes signals only.

It does not grant authority.

It does not authorize action.

UNKNOWN → HOLD
"""

    filename.write_text(content, encoding="utf-8")
    st.success(f"Observation saved: {filename.name}")

    with st.expander("Generated Observation", expanded=True):
        st.text(content)
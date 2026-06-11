import re
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Signal Enhancer v0.3", layout="wide")

BASE = Path(__file__).parent
TELEMETRY = BASE / "telemetry"
TELEMETRY.mkdir(exist_ok=True)

SENSORS = [
    "PULSE",
    "MOVEMENT",
    "PHASE",
    "RELATIONSHIP",
    "BOUNDARY",
    "PRESSURE",
    "STANDING",
    "CONSEQUENCE HORIZON",
]


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_section(text: str, section: str) -> str:
    pattern = rf"{section}\s*\n\n(.*?)(?:\n\n─|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else "not_found"


def observation_files():
    return sorted(
        TELEMETRY.glob("observation_*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )


def compare_observation_texts(text_a: str, text_b: str):
    rows = []
    shared = []
    changed = []
    unknowns = []
    matches = 0

    for sensor in SENSORS:
        value_a = extract_section(text_a, sensor)
        value_b = extract_section(text_b, sensor)
        is_match = value_a == value_b

        if is_match:
            matches += 1
            shared.append(sensor)
        else:
            changed.append(sensor)

        if "unknown" in value_a.lower() or "unknown" in value_b.lower():
            unknowns.append(sensor)

        rows.append({
            "Sensor": sensor.title(),
            "Observation A": value_a,
            "Observation B": value_b,
            "Match": is_match,
        })

    match_score = round((matches / len(SENSORS)) * 100, 2)

    return {
        "rows": rows,
        "shared": shared,
        "changed": changed,
        "unknowns": unknowns,
        "match_score": match_score,
    }


st.title("Signal Enhancer v0.3")
st.caption("Observation ≠ Authority | Signal ≠ Decision | UNKNOWN → HOLD")

tab1, tab2 = st.tabs(["Create Observation", "Compare Observations"])

# -------------------------
# TAB 1: CREATE OBSERVATION
# -------------------------
with tab1:
    st.subheader("Create Observation")

    target = st.text_input("Observation Target")
    source_text = st.text_area("Paste target text / post / discussion here", height=220)

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

# -------------------------
# TAB 2: COMPARE OBSERVATIONS
# -------------------------
with tab2:
    st.subheader("Compare Observations")

    files = observation_files()

    if len(files) < 2:
        st.info("Need at least two observation_*.md files in telemetry/ to compare.")
    else:
        names = [f.name for f in files]

        col_a, col_b = st.columns(2)

        with col_a:
            obs_a_name = st.selectbox("Observation A", names, index=0)

        with col_b:
            obs_b_name = st.selectbox("Observation B", names, index=1)

        obs_a = TELEMETRY / obs_a_name
        obs_b = TELEMETRY / obs_b_name

        text_a = read_file(obs_a)
        text_b = read_file(obs_b)

        result = compare_observation_texts(text_a, text_b)
        comparison_rows = result["rows"]

        st.divider()

        st.metric("Match Score", f"{result['match_score']}%")

        if result["match_score"] >= 75:
            st.success("High signal alignment observed. No authority granted.")
        elif result["match_score"] >= 40:
            st.warning("Partial signal alignment observed. Further inspection recommended.")
        else:
            st.error("Low signal alignment observed. UNKNOWN → HOLD.")

        col_1, col_2, col_3 = st.columns(3)

        with col_1:
            st.markdown("### Shared Signals")
            if result["shared"]:
                st.write(result["shared"])
            else:
                st.info("No shared signals.")

        with col_2:
            st.markdown("### Changed Signals")
            if result["changed"]:
                st.write(result["changed"])
            else:
                st.success("No changed signals.")

        with col_3:
            st.markdown("### UNKNOWN / HOLD")
            if result["unknowns"]:
                st.write(result["unknowns"])
            else:
                st.success("No UNKNOWN surfaces.")

        st.markdown("### Difference Table")
        st.table(comparison_rows)

        with st.expander("Raw Observation A"):
            st.text(text_a)

        with st.expander("Raw Observation B"):
            st.text(text_b)

        if st.button("Save Comparison Record"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = TELEMETRY / f"comparison_app_{timestamp}.md"

            lines = [
                "SIGNAL ENHANCER COMPARISON",
                "",
                f"Date: {datetime.now().isoformat(timespec='seconds')}",
                "",
                f"Observation A: {obs_a_name}",
                f"Observation B: {obs_b_name}",
                "",
                f"Match Score: {result['match_score']}%",
                "",
                f"Shared Signals: {', '.join(result['shared']) if result['shared'] else 'NONE'}",
                f"Changed Signals: {', '.join(result['changed']) if result['changed'] else 'NONE'}",
                f"UNKNOWN / HOLD Surfaces: {', '.join(result['unknowns']) if result['unknowns'] else 'NONE'}",
                "",
                "Authority: NONE",
                "Promotion: NONE",
                "Invariant: NOT ESTABLISHED",
                "",
                "UNKNOWN → HOLD",
                "",
                "────────────────────────────────────",
                "",
            ]

            for row in comparison_rows:
                lines.append(row["Sensor"].upper())
                lines.append("")
                lines.append(f"A: {row['Observation A']}")
                lines.append(f"B: {row['Observation B']}")
                lines.append(f"Match: {row['Match']}")
                lines.append("")
                lines.append("────────────────────────────────────")
                lines.append("")

            lines.extend([
                "BOUNDARY",
                "",
                "This comparison observes signal alignment only.",
                "",
                "It does not grant authority.",
                "",
                "It does not authorize action.",
                "",
                "UNKNOWN → HOLD",
            ])

            filename.write_text("\n".join(lines), encoding="utf-8")
            st.success(f"Comparison saved: {filename.name}")
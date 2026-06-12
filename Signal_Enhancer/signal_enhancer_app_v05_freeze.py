import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Signal Enhancer v0.5", layout="wide")

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
    lines = text.splitlines()
    section = section.strip().upper()

    for i, line in enumerate(lines):
        if line.strip().upper() == section:
            collected = []

            for next_line in lines[i + 1:]:
                stripped = next_line.strip()

                if stripped.startswith("─"):
                    break

                if stripped:
                    collected.append(stripped)

            return "\n".join(collected).strip() if collected else "not_found"

    return "not_found"


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

        if (
            "unknown" in value_a.lower()
            or "unknown" in value_b.lower()
            or "not_found" in value_a.lower()
            or "not_found" in value_b.lower()
        ):
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


def safe_filename(text: str) -> str:
    cleaned = text.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_")
    return cleaned or "untitled"


def summarize_observation(path: Path) -> dict:
    text = read_file(path)

    return {
        "File": path.name,
        "Target": extract_section(text, "Target"),
        "Pulse": extract_section(text, "PULSE"),
        "Movement": extract_section(text, "MOVEMENT"),
        "Phase": extract_section(text, "PHASE"),
        "Relationship": extract_section(text, "RELATIONSHIP"),
        "Boundary": extract_section(text, "BOUNDARY"),
        "Pressure": extract_section(text, "PRESSURE"),
        "Standing": extract_section(text, "STANDING"),
        "Consequence Horizon": extract_section(text, "CONSEQUENCE HORIZON"),
        "Notes": extract_section(text, "NOTES"),
    }


def build_frequency_counter(files, sensor: str) -> Counter:
    counter = Counter()

    for file in files:
        text = read_file(file)
        value = extract_section(text, sensor)
        counter[value] += 1

    return counter


def count_unknown_surfaces(files) -> Counter:
    counter = Counter()

    for file in files:
        text = read_file(file)

        for sensor in SENSORS:
            value = extract_section(text, sensor)
            if "unknown" in value.lower() or "not_found" in value.lower():
                counter[sensor] += 1

    return counter


def build_pattern_counter(files) -> Counter:
    counter = Counter()

    for file in files:
        text = read_file(file)

        pattern = (
            extract_section(text, "PULSE"),
            extract_section(text, "MOVEMENT"),
            extract_section(text, "PHASE"),
        )

        counter[pattern] += 1

    return counter


def build_standing_pressure_counter(files) -> Counter:
    counter = Counter()

    for file in files:
        text = read_file(file)

        pattern = (
            extract_section(text, "STANDING"),
            extract_section(text, "PRESSURE"),
        )

        counter[pattern] += 1

    return counter


def build_boundary_horizon_counter(files) -> Counter:
    counter = Counter()

    for file in files:
        text = read_file(file)

        pattern = (
            extract_section(text, "BOUNDARY"),
            extract_section(text, "CONSEQUENCE HORIZON"),
        )

        counter[pattern] += 1

    return counter


def build_unknown_pattern_counter(files) -> Counter:
    counter = Counter()

    for file in files:
        text = read_file(file)

        pattern = []

        for sensor in SENSORS:
            value = extract_section(text, sensor)

            if "unknown" in value.lower() or "not_found" in value.lower():
                pattern.append(sensor)

        if pattern:
            counter[tuple(pattern)] += 1

    return counter


st.title("Signal Enhancer v0.5")
st.caption("Observation ≠ Authority | Signal ≠ Decision | Pattern ≠ Truth | UNKNOWN → HOLD")

tab1, tab2, tab3, tab4 = st.tabs([
    "Create Observation",
    "Compare Observations",
    "Observation Explorer",
    "Pattern Explorer",
])

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
        filename = TELEMETRY / f"observation_{safe_filename(target)}_{timestamp}.md"

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

BOUNDARY STATEMENT

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
                "BOUNDARY STATEMENT",
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

# -------------------------
# TAB 3: OBSERVATION EXPLORER
# -------------------------
with tab3:
    st.subheader("Observation Explorer")

    files = observation_files()

    if not files:
        st.info("No observation_*.md files found in telemetry/.")
    else:
        st.markdown("### Corpus Status")

        unknown_counter = count_unknown_surfaces(files)

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Observation Files", len(files))

        with col_b:
            st.metric("UNKNOWN Surfaces", sum(unknown_counter.values()))

        with col_c:
            st.metric("Architecture", "FROZEN")

        st.divider()

        search_text = st.text_input(
            "Search observations",
            placeholder="Search target, notes, source text, or signal values..."
        )

        sort_mode = st.selectbox(
            "Sort",
            ["Newest First", "Oldest First", "Filename A-Z", "Filename Z-A"]
        )

        display_files = files.copy()

        if sort_mode == "Oldest First":
            display_files = sorted(display_files, key=lambda f: f.stat().st_mtime)
        elif sort_mode == "Filename A-Z":
            display_files = sorted(display_files, key=lambda f: f.name.lower())
        elif sort_mode == "Filename Z-A":
            display_files = sorted(display_files, key=lambda f: f.name.lower(), reverse=True)

        if search_text:
            filtered_files = []

            for file in display_files:
                text = read_file(file)

                if search_text.lower() in text.lower() or search_text.lower() in file.name.lower():
                    filtered_files.append(file)

            display_files = filtered_files

        st.markdown("### Observation List")

        if not display_files:
            st.warning("No observations matched the current search.")
        else:
            selected_file = st.selectbox(
                "Open Observation",
                [f.name for f in display_files]
            )

            selected_path = TELEMETRY / selected_file
            selected_text = read_file(selected_path)
            selected_summary = summarize_observation(selected_path)

            st.markdown("### Selected Observation Summary")
            st.table([selected_summary])

            with st.expander("Raw Observation", expanded=False):
                st.text(selected_text)

        st.divider()

        st.markdown("### Frequency Analysis")

        freq_col_1, freq_col_2, freq_col_3 = st.columns(3)

        with freq_col_1:
            st.markdown("#### Pulse")
            st.json(dict(build_frequency_counter(files, "PULSE")))

        with freq_col_2:
            st.markdown("#### Pressure")
            st.json(dict(build_frequency_counter(files, "PRESSURE")))

        with freq_col_3:
            st.markdown("#### Standing")
            st.json(dict(build_frequency_counter(files, "STANDING")))

        st.markdown("### UNKNOWN / HOLD Frequency")

        if unknown_counter:
            st.json(dict(unknown_counter))
        else:
            st.success("No UNKNOWN or not_found surfaces detected.")

        st.caption("Observation Explorer observes stored records only. It grants no authority.")

# -------------------------
# TAB 4: PATTERN EXPLORER
# -------------------------
with tab4:
    st.subheader("Pattern Explorer")

    files = observation_files()

    if not files:
        st.info("No observation_*.md files found in telemetry/.")
    else:
        pattern_counter = build_pattern_counter(files)
        standing_pressure_counter = build_standing_pressure_counter(files)
        boundary_horizon_counter = build_boundary_horizon_counter(files)
        unknown_pattern_counter = build_unknown_pattern_counter(files)

        st.markdown("### Pattern Status")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Observation Files", len(files))

        with col_b:
            st.metric("Unique Pulse / Movement / Phase Patterns", len(pattern_counter))

        with col_c:
            st.metric("UNKNOWN Pattern Types", len(unknown_pattern_counter))

        st.divider()

        st.markdown("### Most Common Pulse / Movement / Phase Patterns")

        common_patterns = pattern_counter.most_common(10)

        if common_patterns:
            for pattern, count in common_patterns:
                st.write({
                    "count": count,
                    "pulse": pattern[0],
                    "movement": pattern[1],
                    "phase": pattern[2],
                })
        else:
            st.info("No patterns found.")

        st.divider()

        st.markdown("### Standing / Pressure Patterns")

        if standing_pressure_counter:
            for pattern, count in standing_pressure_counter.most_common(10):
                st.write({
                    "count": count,
                    "standing": pattern[0],
                    "pressure": pattern[1],
                })
        else:
            st.info("No standing / pressure patterns found.")

        st.divider()

        st.markdown("### Boundary / Consequence Horizon Patterns")

        if boundary_horizon_counter:
            for pattern, count in boundary_horizon_counter.most_common(10):
                st.write({
                    "count": count,
                    "boundary": pattern[0],
                    "consequence_horizon": pattern[1],
                })
        else:
            st.info("No boundary / consequence horizon patterns found.")

        st.divider()

        st.markdown("### UNKNOWN Patterns")

        if unknown_pattern_counter:
            for pattern, count in unknown_pattern_counter.most_common(10):
                st.write({
                    "count": count,
                    "unknown_surfaces": list(pattern),
                })
        else:
            st.success("No UNKNOWN patterns detected.")

        st.divider()

        st.markdown("### Observatory Statement")
        st.caption(
            "Pattern visibility only. "
            "Pattern ≠ Authority. "
            "Frequency ≠ Truth. "
            "Frequency ≠ Permission. "
            "UNKNOWN → HOLD."
        )
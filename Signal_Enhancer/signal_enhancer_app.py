import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Signal Enhancer v0.8", layout="wide")

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
    "INTERRUPTIBILITY",
    "CONSEQUENCE HORIZON",
]


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_section(text: str, section: str) -> str:
    lines = text.splitlines()
    section = section.strip().upper()

    for i, line in enumerate(lines):
        if line.strip().upper().rstrip(":") == section:
            if line.strip().endswith(":"):
                for next_line in lines[i + 1:]:
                    stripped = next_line.strip()
                    if stripped:
                        return stripped
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
        "Date": extract_section(text, "Date"),
        "Target": extract_section(text, "Target"),
        "Pulse": extract_section(text, "PULSE"),
        "Movement": extract_section(text, "MOVEMENT"),
        "Phase": extract_section(text, "PHASE"),
        "Relationship": extract_section(text, "RELATIONSHIP"),
        "Boundary": extract_section(text, "BOUNDARY"),
        "Pressure": extract_section(text, "PRESSURE"),
        "Standing": extract_section(text, "STANDING"),
        "Interruptibility": extract_section(text, "INTERRUPTIBILITY"),
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


def build_standing_interruptibility_counter(files) -> Counter:
    counter = Counter()

    for file in files:
        text = read_file(file)

        pattern = (
            extract_section(text, "STANDING"),
            extract_section(text, "INTERRUPTIBILITY"),
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


def counter_to_rows(counter: Counter, label: str = "Value"):
    return [
        {
            label: key,
            "Count": value,
        }
        for key, value in counter.most_common()
    ]


def emerging_signal_rows(files):
    rows = []

    for sensor in SENSORS:
        counter = build_frequency_counter(files, sensor)

        for value, count in counter.most_common():
            if count > 1:
                rows.append({
                    "Sensor": sensor.title(),
                    "Signal": value,
                    "Count": count,
                    "Status": "recurring",
                })

    return rows


def rare_signal_rows(files):
    rows = []

    for sensor in SENSORS:
        counter = build_frequency_counter(files, sensor)

        for value, count in counter.most_common():
            if count == 1:
                rows.append({
                    "Sensor": sensor.title(),
                    "Signal": value,
                    "Count": count,
                    "Status": "rare",
                })

    return rows


def evidence_summary(files):
    pattern_counter = build_pattern_counter(files)
    unknown_counter = count_unknown_surfaces(files)

    return {
        "Observation Count": len(files),
        "Unique Pulse / Movement / Phase Patterns": len(pattern_counter),
        "UNKNOWN Surface Count": sum(unknown_counter.values()),
        "Architecture": "FROZEN",
        "Authority": "NONE",
        "Promotion": "NONE",
    }


def parse_observation_datetime(value: str):
    try:
        return datetime.fromisoformat(value.strip())
    except Exception:
        return None


def timeline_rows(files):
    rows = []

    for file in files:
        summary = summarize_observation(file)
        parsed_date = parse_observation_datetime(summary["Date"])

        rows.append({
            "File": file.name,
            "Date": summary["Date"],
            "Parsed Date": parsed_date,
            "Target": summary["Target"],
            "Pulse": summary["Pulse"],
            "Movement": summary["Movement"],
            "Phase": summary["Phase"],
            "Relationship": summary["Relationship"],
            "Boundary": summary["Boundary"],
            "Pressure": summary["Pressure"],
            "Standing": summary["Standing"],
            "Interruptibility": summary["Interruptibility"],
            "Consequence Horizon": summary["Consequence Horizon"],
        })

    return rows


def unique_targets(rows):
    return sorted(
        {
            row["Target"]
            for row in rows
            if row["Target"] and row["Target"] != "not_found"
        }
    )


def stability_rows(rows):
    output = []

    if not rows:
        return output

    for sensor in SENSORS:
        display_name = sensor.title()
        values = []

        for row in rows:
            key = display_name
            if key in row:
                values.append(row[key])

        clean_values = [value for value in values if value and value != "not_found"]
        unique_values = sorted(set(clean_values))

        if not clean_values:
            status = "not_found"
        elif len(unique_values) == 1:
            status = "stable"
        else:
            status = "change_detected"

        output.append({
            "Sensor": display_name,
            "Status": status,
            "Unique Values": ", ".join(unique_values) if unique_values else "NONE",
            "Observation Count": len(clean_values),
        })

    return output


st.title("Signal Enhancer v0.8")
st.caption(
    "Observation ≠ Authority | Signal ≠ Decision | Pattern ≠ Truth | "
    "Evidence ≠ Authority | Timeline ≠ Prediction | UNKNOWN → HOLD"
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Create Observation",
    "Compare Observations",
    "Observation Explorer",
    "Pattern Explorer",
    "Evidence Dashboard",
    "Observation Timeline",
    "Inspectable Unknowns",
    "Governability Inspector"
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

        interruptibility = st.selectbox("Interruptibility", [
            "interruptibility_unknown",
            "interruptibility_open",
            "interruptibility_narrowing",
            "interruptibility_resistant",
            "interruptibility_self_reinforcing",
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

INTERRUPTIBILITY

{interruptibility}

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

        freq_col_1, freq_col_2, freq_col_3, freq_col_4 = st.columns(4)

        with freq_col_1:
            st.markdown("#### Pulse")
            st.json(dict(build_frequency_counter(files, "PULSE")))

        with freq_col_2:
            st.markdown("#### Pressure")
            st.json(dict(build_frequency_counter(files, "PRESSURE")))

        with freq_col_3:
            st.markdown("#### Standing")
            st.json(dict(build_frequency_counter(files, "STANDING")))

        with freq_col_4:
            st.markdown("#### Interruptibility")
            st.json(dict(build_frequency_counter(files, "INTERRUPTIBILITY")))

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
        standing_interruptibility_counter = build_standing_interruptibility_counter(files)
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

        st.markdown("### Standing / Interruptibility Patterns")

        if standing_interruptibility_counter:
            for pattern, count in standing_interruptibility_counter.most_common(10):
                st.write({
                    "count": count,
                    "standing": pattern[0],
                    "interruptibility": pattern[1],
                })
        else:
            st.info("No standing / interruptibility patterns found.")

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

# -------------------------
# TAB 5: EVIDENCE DASHBOARD
# -------------------------
with tab5:
    st.subheader("Evidence Dashboard")

    files = observation_files()

    if not files:
        st.info("No observation_*.md files found in telemetry/.")
    else:
        summary = evidence_summary(files)
        unknown_counter = count_unknown_surfaces(files)

        st.markdown("### Corpus Health")

        col_a, col_b, col_c, col_d, col_e = st.columns(5)

        with col_a:
            st.metric("Observation Files", summary["Observation Count"])

        with col_b:
            st.metric("Unique Patterns", summary["Unique Pulse / Movement / Phase Patterns"])

        with col_c:
            st.metric("UNKNOWN Surfaces", summary["UNKNOWN Surface Count"])

        with col_d:
            st.metric("Authority", "NONE")

        with col_e:
            st.metric("Architecture", "FROZEN")

        st.divider()

        st.markdown("### Top Signal States")

        top_col_1, top_col_2, top_col_3, top_col_4, top_col_5 = st.columns(5)

        with top_col_1:
            st.markdown("#### Pulse")
            st.table(counter_to_rows(build_frequency_counter(files, "PULSE"), "Pulse"))

        with top_col_2:
            st.markdown("#### Pressure")
            st.table(counter_to_rows(build_frequency_counter(files, "PRESSURE"), "Pressure"))

        with top_col_3:
            st.markdown("#### Standing")
            st.table(counter_to_rows(build_frequency_counter(files, "STANDING"), "Standing"))

        with top_col_4:
            st.markdown("#### Interruptibility")
            st.table(counter_to_rows(build_frequency_counter(files, "INTERRUPTIBILITY"), "Interruptibility"))

        with top_col_5:
            st.markdown("#### Boundary")
            st.table(counter_to_rows(build_frequency_counter(files, "BOUNDARY"), "Boundary"))

        st.divider()

        st.markdown("### UNKNOWN Surfaces")

        if unknown_counter:
            st.table(counter_to_rows(unknown_counter, "UNKNOWN Surface"))
        else:
            st.success("No UNKNOWN or not_found surfaces detected.")

        st.divider()

        st.markdown("### Emerging Signals")

        emerging_rows = emerging_signal_rows(files)

        if emerging_rows:
            st.table(emerging_rows)
        else:
            st.info("No recurring signals detected yet.")

        st.markdown("### Rare Signals")

        rare_rows = rare_signal_rows(files)

        if rare_rows:
            st.table(rare_rows)
        else:
            st.info("No rare signals detected.")

        st.divider()

        st.markdown("### Evidence Boundary")

        st.caption(
            "Evidence Dashboard provides visibility only. "
            "Evidence ≠ Authority. "
            "Evidence ≠ Decision. "
            "Frequency ≠ Truth. "
            "Pattern ≠ Permission. "
            "UNKNOWN → HOLD."
        )

# -------------------------
# TAB 6: OBSERVATION TIMELINE
# -------------------------
with tab6:
    st.subheader("Observation Timeline")

    files = observation_files()

    if not files:
        st.info("No observation_*.md files found in telemetry/.")
    else:
        rows = timeline_rows(files)
        targets = unique_targets(rows)

        parsed_dates = [
            row["Parsed Date"]
            for row in rows
            if row["Parsed Date"] is not None
        ]

        st.markdown("### Timeline Status")

        col_a, col_b, col_c, col_d = st.columns(4)

        with col_a:
            st.metric("Observation Files", len(rows))

        with col_b:
            st.metric("Unique Targets", len(targets))

        with col_c:
            earliest = min(parsed_dates).isoformat(timespec="seconds") if parsed_dates else "UNKNOWN"
            st.metric("Earliest Observation", earliest)

        with col_d:
            latest = max(parsed_dates).isoformat(timespec="seconds") if parsed_dates else "UNKNOWN"
            st.metric("Latest Observation", latest)

        st.divider()

        target_filter_options = ["All Targets"] + targets

        selected_target = st.selectbox(
            "Target Filter",
            target_filter_options
        )

        sort_mode = st.selectbox(
            "Timeline Sort",
            ["Newest First", "Oldest First"]
        )

        filtered_rows = rows

        if selected_target != "All Targets":
            filtered_rows = [
                row
                for row in filtered_rows
                if row["Target"] == selected_target
            ]

        if sort_mode == "Oldest First":
            filtered_rows = sorted(
                filtered_rows,
                key=lambda row: row["Parsed Date"] or datetime.min
            )
        else:
            filtered_rows = sorted(
                filtered_rows,
                key=lambda row: row["Parsed Date"] or datetime.min,
                reverse=True
            )

        st.markdown("### Timeline Records")

        display_rows = []

        for row in filtered_rows:
            display_rows.append({
                "Date": row["Date"],
                "Target": row["Target"],
                "Pulse": row["Pulse"],
                "Movement": row["Movement"],
                "Phase": row["Phase"],
                "Relationship": row["Relationship"],
                "Boundary": row["Boundary"],
                "Pressure": row["Pressure"],
                "Standing": row["Standing"],
                "Interruptibility": row["Interruptibility"],
                "Consequence Horizon": row["Consequence Horizon"],
                "File": row["File"],
            })

        if display_rows:
            st.table(display_rows)
        else:
            st.warning("No timeline records matched the current filter.")

        st.divider()

        st.markdown("### Stability / Change Detection")

        stability = stability_rows(filtered_rows)

        if stability:
            st.table(stability)
        else:
            st.info("No stability data available.")

        st.divider()

        st.markdown("### Timeline Boundary")

        st.caption(
            "Timeline visibility only. "
            "Timeline ≠ Prediction. "
            "Temporal order ≠ Causation. "
            "Stability ≠ Authority. "
            "Change ≠ Permission. "
            "UNKNOWN → HOLD."
        )

# -------------------------
# TAB 7: INSPECTABLE UNKNOWNS
# -------------------------
with tab7:
    st.subheader("Inspectable Unknown Explorer")
    st.info("Integration in progress.")
    st.caption(
        "Discovery surface only. Unknowns ≠ conclusions. UNKNOWN → HOLD."
    )


# -------------------------
# TAB 8: GOVERNABILITY INSPECTOR
# -------------------------
with tab8:
    st.subheader("Continuous Governability Inspector")
    st.info("Integration in progress.")
    st.caption(
        "Inspection surface only. Visibility ≠ Governability. UNKNOWN → HOLD."
    )

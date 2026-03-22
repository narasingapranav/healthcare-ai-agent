from datetime import datetime


def _parse_recorded_at(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _current_value_for_mode(metrics: list[dict], metric_name: str, progress_mode: str) -> float:
    mode = progress_mode.lower()
    metric_rows = [item for item in metrics if str(item.get("metric_name", "")) == metric_name]
    if not metric_rows:
        return 0.0

    parsed_rows: list[tuple[datetime, float]] = []
    for row in metric_rows:
        parsed = _parse_recorded_at(str(row.get("recorded_at", "")))
        if parsed is None:
            continue
        parsed_rows.append((parsed, float(row.get("metric_value", 0))))

    if not parsed_rows:
        return 0.0

    parsed_rows.sort(key=lambda value: value[0], reverse=True)

    if mode == "latest":
        return parsed_rows[0][1]

    now = datetime.utcnow()
    if mode == "daily":
        return sum(value for dt, value in parsed_rows if dt.date() == now.date())

    if mode == "monthly":
        return sum(value for dt, value in parsed_rows if dt.year == now.year and dt.month == now.month)

    return parsed_rows[0][1]


def generate_health_report(
    metrics: list[dict],
    medications: list[dict],
    goals: list[dict],
    progress_mode: str = "Latest",
) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append("Healthcare AI Agent - Health Summary Report")
    lines.append(f"Generated: {now}")
    lines.append("")

    lines.append("1) Medication Summary")
    if medications:
        for med in medications:
            lines.append(
                f"- {med.get('name', '')} ({med.get('dosage', '')}) at {med.get('schedule_time', '')}"
            )
    else:
        lines.append("- No active medications")
    lines.append("")

    lines.append("2) Recent Metrics")
    if metrics:
        for item in metrics[:20]:
            lines.append(
                f"- {item.get('recorded_at', '')}: {item.get('metric_name', '')} = {item.get('metric_value', '')} {item.get('unit', '')}"
            )
    else:
        lines.append("- No metrics available")
    lines.append("")

    lines.append("3) Goal Progress")
    lines.append(f"Mode: {progress_mode}")
    if goals:
        for goal in goals:
            metric_name = str(goal.get("metric_name", ""))
            target = float(goal.get("target_value", 0))
            current = _current_value_for_mode(metrics, metric_name, progress_mode)
            if current > 0:
                progress = (current / target * 100) if target > 0 else 0
                lines.append(
                    f"- {metric_name}: {current:.2f}/{target:.2f} {goal.get('unit', '')} ({progress:.1f}% of target)"
                )
            else:
                lines.append(
                    f"- {metric_name}: no data yet (target {target:.2f} {goal.get('unit', '')})"
                )
    else:
        lines.append("- No active goals")

    lines.append("")
    lines.append("Disclaimer: This report is informational and not a substitute for medical advice.")
    return "\n".join(lines)

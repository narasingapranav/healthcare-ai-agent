from datetime import datetime


def generate_health_report(metrics: list[dict], medications: list[dict], goals: list[dict]) -> str:
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
    if goals:
        latest_by_metric: dict[str, dict] = {}
        for item in metrics:
            key = str(item.get("metric_name", ""))
            if key not in latest_by_metric:
                latest_by_metric[key] = item

        for goal in goals:
            metric_name = str(goal.get("metric_name", ""))
            target = float(goal.get("target_value", 0))
            latest = latest_by_metric.get(metric_name)
            if latest:
                current = float(latest.get("metric_value", 0))
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

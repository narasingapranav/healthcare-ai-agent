from datetime import datetime


def parse_metric_input(metric_name: str, metric_value: str, unit: str) -> tuple[str, float, str, str]:
    clean_name = metric_name.strip().lower()
    if not clean_name:
        raise ValueError("Metric name is required.")

    try:
        value = float(metric_value)
    except ValueError as error:
        raise ValueError("Metric value must be a valid number.") from error

    clean_unit = unit.strip()
    if not clean_unit:
        raise ValueError("Unit is required.")

    timestamp = datetime.utcnow().isoformat()
    return clean_name, value, clean_unit, timestamp

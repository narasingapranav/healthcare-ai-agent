import csv
import json
from datetime import datetime
from io import StringIO
import xml.etree.ElementTree as ET


def parse_metrics_csv_text(content: str) -> list[dict]:
    reader = csv.DictReader(StringIO(content))
    metrics: list[dict] = []
    for row in reader:
        metrics.append(
            {
                "metric_name": (row.get("metric_name") or "steps").strip().lower(),
                "metric_value": float(row.get("metric_value") or 0),
                "unit": (row.get("unit") or "count").strip(),
                "recorded_at": row.get("recorded_at") or datetime.utcnow().isoformat(),
            }
        )
    return metrics


def parse_metrics_json_text(content: str) -> list[dict]:
    raw = json.loads(content)
    metrics: list[dict] = []
    for item in raw:
        metrics.append(
            {
                "metric_name": str(item.get("metric_name", "steps")).strip().lower(),
                "metric_value": float(item.get("metric_value", 0)),
                "unit": str(item.get("unit", "count")).strip(),
                "recorded_at": item.get("recorded_at") or datetime.utcnow().isoformat(),
            }
        )
    return metrics


def parse_metrics_xml_text(content: str) -> list[dict]:
    root = ET.fromstring(content)
    metrics: list[dict] = []

    for metric_node in root.findall(".//metric"):
        metric_name = (metric_node.findtext("metric_name") or "steps").strip().lower()
        metric_value = float(metric_node.findtext("metric_value") or 0)
        unit = (metric_node.findtext("unit") or "count").strip()
        recorded_at = metric_node.findtext("recorded_at") or datetime.utcnow().isoformat()
        metrics.append(
            {
                "metric_name": metric_name,
                "metric_value": metric_value,
                "unit": unit,
                "recorded_at": recorded_at,
            }
        )

    return metrics


def export_metrics_to_csv(metrics: list[dict]) -> str:
    output = StringIO()
    fieldnames = ["metric_name", "metric_value", "unit", "recorded_at"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for item in metrics:
        writer.writerow(
            {
                "metric_name": item.get("metric_name", ""),
                "metric_value": item.get("metric_value", ""),
                "unit": item.get("unit", ""),
                "recorded_at": item.get("recorded_at", ""),
            }
        )
    return output.getvalue()


def export_metrics_to_json(metrics: list[dict]) -> str:
    return json.dumps(metrics, indent=2)


def export_metrics_to_xml(metrics: list[dict]) -> str:
    root = ET.Element("metrics")
    for item in metrics:
        metric_node = ET.SubElement(root, "metric")
        ET.SubElement(metric_node, "metric_name").text = str(item.get("metric_name", ""))
        ET.SubElement(metric_node, "metric_value").text = str(item.get("metric_value", ""))
        ET.SubElement(metric_node, "unit").text = str(item.get("unit", ""))
        ET.SubElement(metric_node, "recorded_at").text = str(item.get("recorded_at", ""))

    return ET.tostring(root, encoding="unicode")

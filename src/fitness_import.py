import csv
import json
from datetime import datetime
from typing import List, Dict, Any
from .database import add_health_metric

def import_fitness_csv(file_path: str) -> int:
    """Import fitness data (steps/calories) from a CSV file. Returns number of records added."""
    count = 0
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            metric_name = row.get('metric_name', 'steps')
            metric_value = float(row.get('metric_value', 0))
            unit = row.get('unit', 'count')
            recorded_at = row.get('recorded_at', datetime.utcnow().isoformat())
            add_health_metric(metric_name, metric_value, unit, recorded_at)
            count += 1
    return count

def import_fitness_json(file_path: str) -> int:
    """Import fitness data from a JSON file. Returns number of records added."""
    count = 0
    with open(file_path, encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
        for entry in data:
            metric_name = entry.get('metric_name', 'steps')
            metric_value = float(entry.get('metric_value', 0))
            unit = entry.get('unit', 'count')
            recorded_at = entry.get('recorded_at', datetime.utcnow().isoformat())
            add_health_metric(metric_name, metric_value, unit, recorded_at)
            count += 1
    return count

"""Parse project-specific metadata stored on Task.requirements."""
import json


def parse_project_meta(task) -> dict | None:
    for entry in task.requirements or []:
        if not isinstance(entry, dict):
            continue
        if entry.get('type') != 'dashboard_meta' or not entry.get('value'):
            continue
        try:
            parsed = json.loads(entry['value'])
        except (json.JSONDecodeError, TypeError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None

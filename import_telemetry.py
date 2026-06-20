"""
Import telemetry into RevLabs Django models.

Accepts:
  - SQLite database (.db): reads directly from TelemetryIQ
  - JSON file (.json): portable export from export_telemetry.py

Usage:
    python import_telemetry.py [path_to_file]
    python manage.py import_telemetry [path_to_file]
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.telemetry_import import run_import, run_import_from_json

SOURCE = sys.argv[1] if len(sys.argv) > 1 else r'..\TelemetryIQ\telemetry.db'


def main():
    if SOURCE.lower().endswith('.json'):
        run_import_from_json(SOURCE)
    else:
        run_import(SOURCE)


if __name__ == '__main__':
    main()

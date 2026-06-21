"""
One‑time project setup for fresh clones.

Usage:
    python setup.py

Runs, in order:
    1. manage.py migrate
    2. populate_data.py          (cars + tracks)
    3. populateparts.py           (91 mod parts)
    4. populate_gt7_parts.py      (Sports Medium Tyre)
    5. populate_adjustments.py    (14 adjustable parts)
    6. Telemetry import from bundled JSON
    7. manage.py createsuperuser  (interactive)
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

def run_step(label, script, args=None):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    cmd = [PYTHON, script] + (args or [])
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n  ERRO: '{script}' falhou (código {result.returncode})")
        sys.exit(result.returncode)
    print(f"  OK")

def main():
    print(f"{'='*60}")
    print(f"  RevLabs — Fresh Clone Setup")
    print(f"{'='*60}")

    run_step("1/6  Applying database migrations...", "manage.py", ["migrate"])
    run_step("2/6  Seeding cars and tracks...", "populate_data.py")
    run_step("3/6  Seeding mod parts...", "populateparts.py")
    run_step("4/6  Seeding GT7 parts...", "populate_gt7_parts.py")
    run_step("5/6  Seeding adjustable parts...", "populate_adjustments.py")

    telemetry_bundle = os.path.join(BASE_DIR, 'revlabs', 'data', 'telemetry_bundle.json')
    if os.path.exists(telemetry_bundle):
        run_step("6/6  Importing bundled telemetry...", "import_telemetry.py", [telemetry_bundle])
        print(f"\n  Telemetry imported from {telemetry_bundle}")
    else:
        print(f"\n  Telemetry bundle not found at {telemetry_bundle}")
        print("  Skip or provide telemetry later via import.")

    print(f"\n{'='*60}")
    print(f"  Setup complete!")
    print(f"  Run: python manage.py runserver")
    print(f"{'='*60}")

    # Optional superuser
    try:
        resp = input("\n  Create a superuser now? (y/N): ").strip().lower()
        if resp == 'y':
            subprocess.run([PYTHON, 'manage.py', 'createsuperuser'], cwd=BASE_DIR)
    except (EOFError, KeyboardInterrupt):
        pass

if __name__ == '__main__':
    main()

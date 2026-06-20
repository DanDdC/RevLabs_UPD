# RevLabs Setup & Usage Guide

## Project Structure

```
C:\Users\user\RevLabs\
├── TelemetryIQ\           # GT7 telemetry capture app (separate project)
│   ├── telemetry.db       # Raw telemetry data (SQLite)
│   ├── Makefile            # Unix-style (won't work on Windows directly)
│   └── ...
└── RevLabs_UPD\           # Django web app (this project)
    ├── manage.py
    ├── import_telemetry.py # CLI import script
    └── ...
```

---

## TelemetryIQ Setup (Windows)

`make` does **not** work on Windows PowerShell because the Makefile uses Unix paths (`.venv/bin/pip`). Instead, run the commands manually:

```powershell
cd C:\Users\user\RevLabs\TelemetryIQ

# Create virtual environment
python -m venv .venv

# Install dependencies
.venv\Scripts\pip install -r requirements.txt

# Run TelemetryIQ
.venv\Scripts\python telemetryiq.py   # or the appropriate entry point
```

To use `make` on Windows, install it via:
- **Chocolatey**: `choco install make`
- **Git Bash**: included with Git for Windows
- **WSL**: native Linux make

Then run `make install` from **Git Bash** or **WSL**, NOT from PowerShell.

---

## RevLabs Setup

```powershell
cd C:\Users\user\RevLabs\RevLabs_UPD

# Activate virtual environment (if not already)
.venv\Scripts\activate

# Run migrations
python manage.py migrate

# Seed data
python populate_data.py       # Cars and tracks
python populateparts.py       # GT7 parts catalog (91 parts)
python populate_adjustments.py  # Tuning adjustments (55 parameters)

# Create admin user (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## How to Export Laps from TelemetryIQ

Laps are automatically recorded by TelemetryIQ while you drive in GT7. The data is stored in `TelemetryIQ\telemetry.db`.

**To verify laps were recorded:**

```powershell
cd C:\Users\user\RevLabs\RevLabs_UPD
.venv\Scripts\python -c "
import sqlite3
conn = sqlite3.connect(r'..\TelemetryIQ\telemetry.db')
cur = conn.cursor()
cur.execute('''
    SELECT l.id, l.lap_number, l.lap_time_ms, l.is_complete, l.car_code, l.track_id
    FROM laps l
    WHERE l.is_complete = 1 AND l.lap_time_ms IS NOT NULL AND l.lap_time_ms > 0
    ORDER BY l.lap_time_ms
''')
for r in cur.fetchall():
    time_s = r[2] / 1000.0
    print(f'Lap {r[1]}: {time_s:.3f}s  car_code={r[4]} track_id={r[5]}')
conn.close()
"
```

**Important**: TelemetryIQ records `car_code` and `track_id` per GT7 internal IDs. For RevLabs to import a lap, both must be non-null and must match a Car/Track in the RevLabs database.

Current known IDs:
- Car 3539 → Porsche 911 GT3 RS (992)
- Track 152 → Autódromo José Carlos Pace (Interlagos)

---

## Portable JSON Export

You can export laps from TelemetryIQ as a standalone JSON file and import it anywhere (even without TelemetryIQ installed).

### Export

```powershell
cd C:\Users\user\RevLabs\RevLabs_UPD
.venv\Scripts\python export_telemetry.py
# Optional: specify custom db and output paths:
.venv\Scripts\python export_telemetry.py "..\TelemetryIQ\telemetry.db" "my_export.json"
```

This creates `telemetry_export.json` containing all complete laps with their frames, stats, and metadata. The file is self-contained — it can be shared, backed up, or imported on a deployed instance.

### Import from JSON

Same as the regular import, just pass the `.json` file instead of `.db`:

```powershell
# CLI
.venv\Scripts\python import_telemetry.py telemetry_export.json

# Management command
.venv\Scripts\python manage.py import_telemetry telemetry_export.json
```

The importer auto-detects `.json` vs `.db` by the file extension.

---

## How to Import Laps into RevLabs

There are **four ways** to import:

### 1. CLI (standalone script)
```powershell
cd C:\Users\user\RevLabs\RevLabs_UPD
.venv\Scripts\python import_telemetry.py
# Optional: specify a different TelemetryIQ db path:
.venv\Scripts\python import_telemetry.py "C:\path\to\telemetry.db"
# Import from JSON export:
.venv\Scripts\python import_telemetry.py telemetry_export.json
```

### 2. Django management command
```powershell
cd C:\Users\user\RevLabs\RevLabs_UPD
.venv\Scripts\python manage.py import_telemetry
# Optional: specify a different path:
.venv\Scripts\python manage.py import_telemetry "C:\path\to\telemetry.db"
.venv\Scripts\python manage.py import_telemetry telemetry_export.json
```

### 3. Web interface — TelemetryIQ DB import (local/dev only)
1. Start the server: `python manage.py runserver`
2. Log in, navigate to the **Dashboard** (select a car + track)
3. Click the **IMPORT TELEMETRY** button below the lap time display
4. The page will reload automatically after import completes

### 4. Web interface — JSON file upload (works anywhere, including deployed)
1. Start the server and log in to the Dashboard
2. Click **IMPORT FROM FILE...** below the IMPORT TELEMETRY button
3. Select a `.json` export file (from `export_telemetry.py`)
4. The page will reload automatically after import completes

**What the import does:**
- Reads completed laps from TelemetryIQ's SQLite database **or** a JSON export file
- For each lap matching a known car+track, creates a `TelemetryLap` record
- Calculates sector times from 3D position data (cumulative distance → 1/3 splits)
- Rejects laps with cumulative distance < 80% of track length (incomplete recordings)
- Keeps only the top 10 fastest laps per car+track combination
- Shows per-car/per-track statistics in the console/log

---

## Adding New Cars or Tracks for Telemetry

To make the importer recognize new GT7 cars/tracks:

1. Add the car to RevLabs:
   ```powershell
   cd C:\Users\user\RevLabs\RevLabs_UPD
   .venv\Scripts\python manage.py shell
   ```
   ```python
   from revlabs.models import Car, Track
   Car.objects.create(name='Ferrari F40', slug_id='ferrari-f40',
       base_avg_speed_kmh=180, power_hp=478, weight_kg=1100,
       car_code=1234, image_path='img/ferrari-f40.png')
   Track.objects.create(name='Monza', slug_id='monza',
       length_km=5.793, speed_multiplier=1.05, track_id=456,
       image_path='img/monza-layout.png')
   ```

2. Run the import again.

---

## Sector Times: How They Work

Sector times are **not directly exported** by TelemetryIQ. They are calculated from **3D position data**:

1. **Cumulative distance** — Euclidean distance between consecutive `(position_x, position_y, position_z)` frames
2. **Track filter** — only laps with cumulative distance >= 80% of actual track length are processed (prevents short/incomplete recordings)
3. **Equal 1/3 splits** — frame indices where cumulative distance reaches 1/3 and 2/3 of total distance
4. **Timestamps** — the `ts` (Unix timestamp) difference at each boundary gives raw sector times
5. **Normalization** — scaled so `sector_1 + sector_2 + sector_3 == lap_time_ms` (matching GT7 official time)

The **Best Projected Lap** = best S1 + best S2 + best S3 across all laps. This is the reference time used for tuning calculations, not the raw best lap.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `make` command not found | Install make (choco, Git Bash, WSL) or run commands manually (see above) |
| Import finds 0 laps | Check TelemetryIQ recorded data: `car_code` and `track_id` must be non-null |
| "No matching car/track" | Add the car/track to RevLabs database first |
| Sector times not calculated | Lap may have < 80% of track length in cumulative distance (incomplete recording) |
| Lap time seems wrong | Check `lap_time_ms` in telemetry.db directly; it's the GT7-reported official time |
| Web import button not working | Ensure server is running and you're logged in; check browser console for errors |

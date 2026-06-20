"""
Export telemetry laps from TelemetryIQ to a portable JSON file.

Usage:
    python export_telemetry.py [path_to_telemetry.db] [output.json]

The JSON file can then be imported into RevLabs via:
    - Web interface: click "IMPORT TELEMETRY" and select the file
    - python manage.py import_telemetry my_export.json
"""
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from math import sqrt

TELEMETRY_DB = sys.argv[1] if len(sys.argv) > 1 else r'..\TelemetryIQ\telemetry.db'
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else 'telemetry_export.json'


def calculate_sectors_export(frames, lap_time_ms, track_length_km=None):
    """
    Simplified sector calculation for export (same logic as import).
    track_length_km is optional; if None, skips the distance filter.
    """
    if not frames or len(frames) < 10:
        return None, None, None

    fs = sorted(frames, key=lambda f: f['seq'])
    n = len(fs)

    cum_dist = [0.0]
    for i in range(1, n):
        dx = (fs[i].get('position_x') or 0) - (fs[i-1].get('position_x') or 0)
        dy = (fs[i].get('position_y') or 0) - (fs[i-1].get('position_y') or 0)
        dz = (fs[i].get('position_z') or 0) - (fs[i-1].get('position_z') or 0)
        cum_dist.append(cum_dist[-1] + sqrt(dx*dx + dy*dy + dz*dz))

    total_dist = cum_dist[-1]
    if total_dist <= 0:
        return None, None, None

    if track_length_km and total_dist < track_length_km * 1000 * 0.8:
        return None, None, None

    s1_threshold = total_dist / 3.0
    s2_threshold = total_dist * 2.0 / 3.0
    s1_idx = next((i for i, d in enumerate(cum_dist) if d >= s1_threshold), None)
    s2_idx = next((i for i, d in enumerate(cum_dist) if d >= s2_threshold), None)
    if s1_idx is None or s2_idx is None:
        return None, None, None

    start_ts = fs[0].get('ts') or 0
    s1_ts = fs[s1_idx].get('ts') or start_ts
    s2_ts = fs[s2_idx].get('ts') or s1_ts
    end_ts = fs[-1].get('ts') or s2_ts

    raw_s1 = max(0, int((s1_ts - start_ts) * 1000))
    raw_s2 = max(0, int((s2_ts - s1_ts) * 1000))
    raw_s3 = max(0, int((end_ts - s2_ts) * 1000))
    raw_sum = raw_s1 + raw_s2 + raw_s3
    if raw_sum <= 0:
        return None, None, None

    scale = lap_time_ms / raw_sum
    return int(raw_s1 * scale), int(raw_s2 * scale), lap_time_ms - int(raw_s1 * scale) - int(raw_s2 * scale)


def main():
    if not os.path.exists(TELEMETRY_DB):
        print(f"ERRO: Arquivo {TELEMETRY_DB} nao encontrado")
        sys.exit(1)

    conn = sqlite3.connect(TELEMETRY_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get tracks for track_id -> length mapping
    cur.execute("SELECT DISTINCT track_id FROM laps WHERE track_id IS NOT NULL")
    track_ids = [r[0] for r in cur.fetchall()]

    # Export sessions with their laps and frames
    cur.execute("""
        SELECT s.id as session_id, s.car_code, s.track_id, s.started_at, s.completed_at, s.notes,
               l.id as lap_id, l.lap_number, l.lap_time_ms, l.is_complete
        FROM sessions s
        JOIN laps l ON l.session_id = s.id
        WHERE l.is_complete = 1 AND l.lap_time_ms IS NOT NULL AND l.lap_time_ms > 0
        ORDER BY s.started_at DESC, l.lap_number
    """)
    rows = cur.fetchall()

    if not rows:
        print("Nenhuma volta completa encontrada")
        conn.close()
        return

    export = {
        'export_version': 1,
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'source': 'TelemetryIQ',
        'laps': [],
    }

    for row in rows:
        car_code = row['car_code']
        track_id = row['track_id']
        if not car_code or not track_id:
            continue

        # Get frames
        cur2 = conn.cursor()
        cur2.execute(
            """SELECT seq, ts, speed_mps, throttle, brake, engine_rpm,
                      position_x, position_y, position_z
               FROM frames WHERE lap_id = ? ORDER BY seq""",
            (row['lap_id'],)
        )
        col_names = [d[0] for d in cur2.description]
        frames = [dict(zip(col_names, r)) for r in cur2.fetchall()]
        cur2.close()

        if not frames:
            continue

        # Basic stats for the export
        speeds = [f.get('speed_mps') for f in frames if f.get('speed_mps')]
        speeds_kmh = [s * 3.6 for s in speeds]
        max_speed = max(speeds_kmh) if speeds_kmh else None
        min_speed = min(speeds_kmh) if speeds_kmh else None
        avg_speed = (sum(speeds_kmh) / len(speeds_kmh)) if speeds_kmh else None
        thr_vals = [f.get('throttle') for f in frames if f.get('throttle') is not None]
        avg_thr = (sum(thr_vals) / len(thr_vals) / 255 * 100) if thr_vals else None
        brk_vals = [f.get('brake') for f in frames if f.get('brake') is not None]
        avg_brk = (sum(brk_vals) / len(brk_vals) / 255 * 100) if brk_vals else None
        max_rpm = max((f.get('engine_rpm') or 0) for f in frames) if frames else None

        export['laps'].append({
            'car_code': car_code,
            'track_id': track_id,
            'lap_number': row['lap_number'],
            'lap_time_ms': row['lap_time_ms'],
            'session_notes': row['notes'],
            'original_session_id': row['session_id'],
            'original_lap_id': row['lap_id'],
            'stats': {
                'max_speed_kmh': max_speed,
                'min_speed_kmh': min_speed,
                'avg_speed_kmh': avg_speed,
                'avg_throttle_pct': avg_thr,
                'avg_brake_pct': avg_brk,
                'max_rpm': max_rpm,
                'total_frames': len(frames),
            },
            'frames': [{
                'seq': f['seq'],
                'ts': f['ts'],
                'speed_mps': f['speed_mps'],
                'throttle': f['throttle'],
                'brake': f['brake'],
                'engine_rpm': f['engine_rpm'],
                'position_x': f['position_x'],
                'position_y': f['position_y'],
                'position_z': f['position_z'],
            } for f in frames],
        })

    conn.close()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    print(f"Exportadas {len(export['laps'])} voltas para {OUTPUT_FILE}")
    print(f"  Tamanho: {os.path.getsize(OUTPUT_FILE) / 1024:.0f} KB")


if __name__ == '__main__':
    main()

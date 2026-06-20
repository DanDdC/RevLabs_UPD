"""
Import telemetry from TelemetryIQ SQLite database into RevLabs Django models.
Usage: .venv\Scripts\python import_telemetry.py [path_to_telemetry.db]

Sector times are calculated from 3D position data (position_x/y/z in frames).
Method: cumulative distance along the track is divided into 3 equal segments;
the timestamp at each 1/3 boundary defines sector split times.
Total sector time is normalized to match lap_time_ms.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.db import transaction
from revlabs.models import Car, Track, TelemetryLap
import sqlite3
from math import sqrt

TELEMETRY_DB = sys.argv[1] if len(sys.argv) > 1 else r'..\TelemetryIQ\telemetry.db'  # noqa: W605


def estimate_speed_stats(car, track, frames):
    if not frames:
        return None, None, None
    speeds = [f.get('speed_mps') for f in frames if f.get('speed_mps')]
    if not speeds:
        return None, None, None
    speeds_kmh = [s * 3.6 for s in speeds]
    return max(speeds_kmh), min(speeds_kmh), sum(speeds_kmh) / len(speeds_kmh)


def estimate_avg_pedal(frames, key):
    vals = [f.get(key) for f in frames if f.get(key) is not None]
    if not vals:
        return None
    return sum(vals) / len(vals) / 255 * 100


def calculate_sectors(frames, lap_time_ms, track_length_km):
    """
    Calculate sector times from 3D position data.

    Divides the cumulative distance traveled into 3 equal segments.
    Uses the frame timestamp (ts) at each boundary to derive sector times.
    Results are normalized so sector_1 + sector_2 + sector_3 == lap_time_ms.

    Only computes sectors if cumulative distance covers >=80% of the
    actual track length, ensuring only full-lap recordings are used.

    Returns (sector_1_ms, sector_2_ms, sector_3_ms) or (None, None, None).
    """
    if not frames or len(frames) < 10:
        return None, None, None

    fs = sorted(frames, key=lambda f: f['seq'])
    n = len(fs)

    # Cumulative distance from 3D position deltas
    cum_dist = [0.0]
    for i in range(1, n):
        dx = (fs[i].get('position_x') or 0) - (fs[i-1].get('position_x') or 0)
        dy = (fs[i].get('position_y') or 0) - (fs[i-1].get('position_y') or 0)
        dz = (fs[i].get('position_z') or 0) - (fs[i-1].get('position_z') or 0)
        cum_dist.append(cum_dist[-1] + sqrt(dx*dx + dy*dy + dz*dz))

    total_dist = cum_dist[-1]
    if total_dist <= 0:
        return None, None, None

    # Reject laps that don't cover at least 80% of the track
    track_length_m = track_length_km * 1000
    if total_dist < track_length_m * 0.8:
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

    # Normalize so sectors add up to lap_time_ms
    scale = lap_time_ms / raw_sum
    s1 = int(raw_s1 * scale)
    s2 = int(raw_s2 * scale)
    s3 = lap_time_ms - s1 - s2  # ensures exact sum

    return s1, s2, s3


def main():
    if not os.path.exists(TELEMETRY_DB):
        print(f"ERRO: Arquivo {TELEMETRY_DB} nao encontrado")
        sys.exit(1)

    conn = sqlite3.connect(TELEMETRY_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT s.id as session_id, s.car_code, s.track_id, s.started_at, s.completed_at, s.notes,
               l.id as lap_id, l.lap_number, l.lap_time_ms, l.is_complete,
               l.started_at as lap_started_at, l.completed_at as lap_completed_at
        FROM sessions s
        JOIN laps l ON l.session_id = s.id
        WHERE l.is_complete = 1 AND l.lap_time_ms IS NOT NULL AND l.lap_number > 0
        ORDER BY s.started_at DESC, l.lap_number
    """)
    rows = cur.fetchall()

    if not rows:
        print("Nenhuma volta completa encontrada no banco de telemetria")
        return

    imported = 0
    skipped = 0

    for row in rows:
        car_code = row['car_code']
        track_id = row['track_id']

        if not car_code or not track_id:
            skipped += 1
            continue

        try:
            car = Car.objects.get(car_code=car_code)
            track = Track.objects.get(track_id=track_id)
        except (Car.DoesNotExist, Track.DoesNotExist):
            skipped += 1
            continue

        lap_time_ms = row['lap_time_ms']
        if not lap_time_ms or lap_time_ms <= 0:
            skipped += 1
            continue

        lap_time_seconds = lap_time_ms / 1000.0

        existing = TelemetryLap.objects.filter(
            car=car, track=track,
            original_lap_id=row['lap_id']
        ).first()
        if existing:
            skipped += 1
            continue

        # Get frames for stats + sector calculation
        cur2 = conn.cursor()
        cur2.execute(
            "SELECT seq, speed_mps, throttle, brake, engine_rpm, ts, position_x, position_y, position_z FROM frames WHERE lap_id = ? ORDER BY seq",
            (row['lap_id'],)
        )
        frames = [dict(r) for r in cur2.fetchall()]
        cur2.close()

        s1, s2, s3 = calculate_sectors(frames, lap_time_ms, track.length_km)

        max_spd, min_spd, avg_spd = estimate_speed_stats(car, track, frames)
        avg_thr = estimate_avg_pedal(frames, 'throttle')
        avg_brk = estimate_avg_pedal(frames, 'brake')
        max_rpm = max((f.get('engine_rpm') or 0) for f in frames) if frames else None

        TelemetryLap.objects.create(
            car=car,
            track=track,
            lap_number=row['lap_number'],
            lap_time_ms=lap_time_ms,
            lap_time_seconds=lap_time_seconds,
            is_complete=True,
            has_mods=False,
            avg_speed_kmh=avg_spd,
            max_speed_kmh=max_spd,
            min_speed_kmh=min_spd,
            max_rpm=max_rpm,
            avg_throttle_pct=avg_thr,
            avg_brake_pct=avg_brk,
            session_notes=row['notes'],
            original_session_id=row['session_id'],
            original_lap_id=row['lap_id'],
            total_frames=len(frames),
            sector_1_ms=s1,
            sector_2_ms=s2,
            sector_3_ms=s3,
        )
        imported += 1

    conn.close()
    print(f"Importadas {imported} voltas, ignoradas {skipped}")

    # Trim to top 10 per car+track combination
    trimmed = 0
    for car in Car.objects.filter(car_code__gt=0):
        for track in Track.objects.filter(track_id__gt=0):
            laps = TelemetryLap.objects.filter(
                car=car, track=track, is_complete=True
            ).order_by('lap_time_ms')
            if laps.count() > 10:
                to_delete = laps[10:]
                for lap in to_delete:
                    lap.delete()
                trimmed += len(to_delete)
    if trimmed:
        print(f"Removidas {trimmed} voltas extras (mantidas apenas top 10 por carro/pista)")

    # Show per-car/per-track stats
    for car in Car.objects.filter(car_code__gt=0):
        for track in Track.objects.filter(track_id__gt=0):
            laps = TelemetryLap.objects.filter(car=car, track=track, is_complete=True).order_by('lap_time_ms')
            if laps.exists():
                best = laps.first()
                count = laps.count()
                top10_avg = sum(l.lap_time_seconds for l in laps) / count
                print(f"\n{car.name} @ {track.name}:")
                print(f"  Total de voltas: {count}")
                print(f"  Melhor tempo: {best.lap_time_seconds:.3f}s")
                if best.sector_1_ms:
                    proj = best.sector_1_ms + best.sector_2_ms + best.sector_3_ms
                    print(f"  Setores: {best.sector_1_ms} / {best.sector_2_ms} / {best.sector_3_ms} ms (projetado: {proj} ms)")
                print(f"  Media top {count}: {top10_avg:.3f}s")
                print(f"  Vel max: {best.max_speed_kmh:.1f} km/h")
                print(f"  Vel media: {best.avg_speed_kmh:.1f} km/h")


if __name__ == '__main__':
    main()

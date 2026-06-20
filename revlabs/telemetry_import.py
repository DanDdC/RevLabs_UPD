"""
Core telemetry import logic shared by CLI script, management command, and web view.

Accepts both:
  - TelemetryIQ SQLite database (.db) — reads laps + frames directly
  - Exported JSON file (.json) — portable format from export_telemetry.py

Usage (standalone CLI):
    python import_telemetry.py [path_to_telemetry.db_or_json]

Usage (Django management command):
    python manage.py import_telemetry [path_to_telemetry.db_or_json]

Usage (web):
    GET /api/import-telemetry/  — imports from default TelemetryIQ path
    POST /api/import-telemetry/ with file upload — imports from uploaded JSON
"""
import json
import os
import sqlite3
from math import sqrt

from revlabs.models import Car, Track, TelemetryLap


def estimate_speed_stats(frames):
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

    scale = lap_time_ms / raw_sum
    s1 = int(raw_s1 * scale)
    s2 = int(raw_s2 * scale)
    s3 = lap_time_ms - s1 - s2

    return s1, s2, s3


def run_import(telemetry_db_path, print_func=print):
    """
    Import laps from a TelemetryIQ SQLite database.

    Returns dict with keys: imported, skipped, trimmed, results (per-car/per-track list)
    """
    if not os.path.exists(telemetry_db_path):
        msg = f"ERRO: Arquivo {telemetry_db_path} nao encontrado"
        print_func(msg)
        return {'imported': 0, 'skipped': 0, 'trimmed': 0, 'error': msg, 'results': []}

    conn = sqlite3.connect(telemetry_db_path)
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
        conn.close()
        msg = "Nenhuma volta completa encontrada no banco de telemetria"
        print_func(msg)
        return {'imported': 0, 'skipped': 0, 'trimmed': 0, 'error': msg, 'results': []}

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

        cur2 = conn.cursor()
        cur2.execute(
            "SELECT seq, speed_mps, throttle, brake, engine_rpm, ts, position_x, position_y, position_z FROM frames WHERE lap_id = ? ORDER BY seq",
            (row['lap_id'],)
        )
        col_names = [d[0] for d in cur2.description]
        frames = [dict(zip(col_names, r)) for r in cur2.fetchall()]
        cur2.close()

        s1, s2, s3 = calculate_sectors(frames, lap_time_ms, track.length_km)

        max_spd, min_spd, avg_spd = estimate_speed_stats(frames)
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
    print_func(f"Importadas {imported} voltas, ignoradas {skipped}")

    trimmed = _trim_excess_laps(print_func)
    results = _collect_results(print_func)

    return {'imported': imported, 'skipped': skipped, 'trimmed': trimmed, 'error': None, 'results': results}


def run_import_from_json(json_path, print_func=print):
    """
    Import laps from a portable JSON export file.
    Same return format as run_import().
    """
    if not os.path.exists(json_path):
        msg = f"ERRO: Arquivo {json_path} nao encontrado"
        print_func(msg)
        return {'imported': 0, 'skipped': 0, 'trimmed': 0, 'error': msg, 'results': []}

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, dict) or 'laps' not in data:
        msg = "ERRO: JSON invalido — objeto deve conter chave 'laps'"
        print_func(msg)
        return {'imported': 0, 'skipped': 0, 'trimmed': 0, 'error': msg, 'results': []}

    print_func(f"JSON export version {data.get('export_version', '?')} de {data.get('exported_at', 'desconhecido')}")
    print_func(f"Arquivo contem {len(data['laps'])} volta(s)")

    imported = 0
    skipped = 0

    for lap_data in data['laps']:
        car_code = lap_data.get('car_code')
        track_id = lap_data.get('track_id')
        lap_time_ms = lap_data.get('lap_time_ms')

        if not car_code or not track_id or not lap_time_ms or lap_time_ms <= 0:
            skipped += 1
            continue

        try:
            car = Car.objects.get(car_code=car_code)
            track = Track.objects.get(track_id=track_id)
        except (Car.DoesNotExist, Track.DoesNotExist):
            skipped += 1
            continue

        original_lap_id = lap_data.get('original_lap_id')
        if original_lap_id:
            existing = TelemetryLap.objects.filter(
                car=car, track=track,
                original_lap_id=original_lap_id
            ).first()
            if existing:
                skipped += 1
                continue

        frames = lap_data.get('frames', [])
        if not frames:
            skipped += 1
            continue

        stats = lap_data.get('stats', {})

        s1, s2, s3 = calculate_sectors(frames, lap_time_ms, track.length_km)

        TelemetryLap.objects.create(
            car=car,
            track=track,
            lap_number=lap_data.get('lap_number', 0),
            lap_time_ms=lap_time_ms,
            lap_time_seconds=lap_time_ms / 1000.0,
            is_complete=True,
            has_mods=False,
            avg_speed_kmh=stats.get('avg_speed_kmh'),
            max_speed_kmh=stats.get('max_speed_kmh'),
            min_speed_kmh=stats.get('min_speed_kmh'),
            max_rpm=stats.get('max_rpm'),
            avg_throttle_pct=stats.get('avg_throttle_pct'),
            avg_brake_pct=stats.get('avg_brake_pct'),
            session_notes=lap_data.get('session_notes', ''),
            original_session_id=lap_data.get('original_session_id'),
            original_lap_id=original_lap_id,
            total_frames=len(frames),
            sector_1_ms=s1,
            sector_2_ms=s2,
            sector_3_ms=s3,
        )
        imported += 1

    print_func(f"Importadas {imported} voltas, ignoradas {skipped}")

    trimmed = _trim_excess_laps(print_func)
    results = _collect_results(print_func)

    return {'imported': imported, 'skipped': skipped, 'trimmed': trimmed, 'error': None, 'results': results}


def _trim_excess_laps(print_func=print):
    """Trim to top 10 per car+track combination. Returns count of deleted laps."""
    trimmed = 0
    for car in Car.objects.filter(car_code__gt=0):
        for track in Track.objects.filter(track_id__gt=0):
            laps_list = TelemetryLap.objects.filter(
                car=car, track=track, is_complete=True
            ).order_by('lap_time_ms')
            if laps_list.count() > 10:
                to_delete = laps_list[10:]
                for lap in to_delete:
                    lap.delete()
                trimmed += len(to_delete)
    if trimmed:
        print_func(f"Removidas {trimmed} voltas extras (mantidas apenas top 10 por carro/pista)")
    return trimmed


def _collect_results(print_func=print):
    """Collect summary results for all car+track combinations."""
    results = []
    for car in Car.objects.filter(car_code__gt=0):
        for track in Track.objects.filter(track_id__gt=0):
            laps_list = TelemetryLap.objects.filter(car=car, track=track, is_complete=True).order_by('lap_time_ms')
            if laps_list.exists():
                best = laps_list.first()
                count = laps_list.count()
                top10_avg = sum(l.lap_time_seconds for l in laps_list) / count
                info = {
                    'car': str(car),
                    'track': str(track),
                    'count': count,
                    'best_time': best.lap_time_seconds,
                    'avg_time': top10_avg,
                    'max_speed': best.max_speed_kmh,
                    'avg_speed': best.avg_speed_kmh,
                    'sectors': {
                        's1': best.sector_1_ms,
                        's2': best.sector_2_ms,
                        's3': best.sector_3_ms,
                    } if best.sector_1_ms else None,
                }
                results.append(info)
                print_func(f"\n{car.name} @ {track.name}:")
                print_func(f"  Total de voltas: {count}")
                print_func(f"  Melhor tempo: {best.lap_time_seconds:.3f}s")
                if best.sector_1_ms:
                    proj = best.sector_1_ms + best.sector_2_ms + best.sector_3_ms
                    print_func(f"  Setores: {best.sector_1_ms} / {best.sector_2_ms} / {best.sector_3_ms} ms (projetado: {proj} ms)")
                print_func(f"  Media top {count}: {top10_avg:.3f}s")
                print_func(f"  Vel max: {best.max_speed_kmh:.1f} km/h")
                print_func(f"  Vel media: {best.avg_speed_kmh:.1f} km/h")
    return results

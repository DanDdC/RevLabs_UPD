import json
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import RevLabsAuthenticationForm, RevLabsUserCreationForm
from .models import Car, Track, PartCategory, TelemetryLap, CarPart, PartAdjustment


def time_to_seconds(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + float(s)


def seconds_to_time(seconds):
    if seconds is None or seconds <= 0:
        return "--:--.---"
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"


def home(request):
    """Public landing page. It is the only page available before authentication."""
    context = {
        'featured_track': Track.objects.filter(slug_id='interlagos').first() or Track.objects.first(),
        'featured_car': Car.objects.filter(slug_id__in=['porsche', 'porsche-911']).first() or Car.objects.first(),
    }
    return render(request, 'landing/home.html', context)


class RevLabsLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = RevLabsAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('track_selection')


def signup(request):
    if request.user.is_authenticated:
        return redirect('track_selection')

    if request.method == 'POST':
        form = RevLabsUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('track_selection')
    else:
        form = RevLabsUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def track_selection(request):
    try:
        hero_track = Track.objects.get(slug_id='interlagos')
        other_tracks = Track.objects.exclude(slug_id='interlagos')
    except Track.DoesNotExist:
        hero_track = Track.objects.first()
        other_tracks = Track.objects.exclude(id=hero_track.id) if hero_track else []

    context = {
        'hero_track': hero_track,
        'tracks': other_tracks,
    }
    return render(request, 'simulator/track_selection.html', context)


@login_required
def car_selection(request):
    track_id = request.GET.get('track', 'interlagos')

    try:
        selected_track = Track.objects.get(slug_id=track_id)
    except Track.DoesNotExist:
        selected_track = Track.objects.first()

    # Only Interlagos is fully configured; other tracks show coming soon
    if selected_track and selected_track.slug_id != 'interlagos':
        return render(request, 'simulator/coming_soon.html', {'track': selected_track})

    cars = Car.objects.all()

    context = {
        'cars': cars,
        'selected_track': selected_track,
    }
    return render(request, 'simulator/car_selection.html', context)


PRESET_MODS = {
    ('mercedes-amg', 'interlagos'): [
        'Sports Medium Tyres',
        'Bore Up',
        'Engine Balance Tuning',
        'Polish Parts',
        'Stage 1 Weight Reduction',
        'Stage 2 Weight Reduction',
        'Stage 3 Weight Reduction',
        'Stage 4 Weight Reduction',
    ],
}


def _get_preset_mods(car, track):
    from django.templatetags.static import static
    names = PRESET_MODS.get((car.slug_id, track.slug_id), [])
    parts = list(CarPart.objects.filter(name__in=names))
    part_by_name = {p.name: p for p in parts}
    return [
        {
            'name': name,
            'image_path': static(part_by_name[name].image_path) if name in part_by_name else static(f'img/mods/{name.lower().replace(chr(32), "")}.png'),
        }
        for name in names
    ]


@login_required
def dashboard(request):
    car_id = request.GET.get('car', 'mercedes-amg')
    track_id = request.GET.get('track', 'interlagos')

    try:
        selected_car = Car.objects.get(slug_id=car_id)
    except Car.DoesNotExist:
        selected_car = Car.objects.first()

    try:
        selected_track = Track.objects.get(slug_id=track_id)
    except Track.DoesNotExist:
        selected_track = Track.objects.first()

    categories = PartCategory.objects.prefetch_related('parts').all()

    # Telemetry data
    telemetry_laps = TelemetryLap.objects.filter(
        car=selected_car, track=selected_track, is_complete=True
    ).order_by('lap_time_ms')

    has_telemetry = telemetry_laps.exists()

    if has_telemetry:
        top_10 = list(telemetry_laps[:10])
        best_time = top_10[0].lap_time_seconds
        telemetry_json = [{
            'lap_number': l.lap_number,
            'lap_time_seconds': l.lap_time_seconds,
            'max_speed_kmh': l.max_speed_kmh,
            'avg_speed_kmh': l.avg_speed_kmh,
            'sector_1_ms': l.sector_1_ms,
            'sector_2_ms': l.sector_2_ms,
            'sector_3_ms': l.sector_3_ms,
        } for l in top_10]

        # Best projected lap = sum of best sectors across all laps
        sectors = [l for l in top_10 if l.sector_1_ms and l.sector_2_ms and l.sector_3_ms]
        if sectors:
            best_s1 = min(l.sector_1_ms for l in sectors)
            best_s2 = min(l.sector_2_ms for l in sectors)
            best_s3 = min(l.sector_3_ms for l in sectors)
            best_projected_ms = best_s1 + best_s2 + best_s3
            best_projected_seconds = best_projected_ms / 1000.0
        else:
            best_projected_seconds = None
    else:
        best_time = None
        best_projected_seconds = None
        telemetry_json = []

    track_length = selected_track.length_km
    track_multiplier = selected_track.speed_multiplier
    base_speed = selected_car.base_avg_speed_kmh * track_multiplier
    base_seconds = (track_length / base_speed) * 3600

    # Show best projected lap if sectors exist, otherwise best real lap
    tuning_base = best_projected_seconds or best_time
    final_display = seconds_to_time(tuning_base) if tuning_base else "--:--.---"

    # Part adjustments data for tuning UI
    adjustable_parts = CarPart.objects.filter(is_adjustable=True).prefetch_related('adjustments')
    part_adjustments = {}
    for p in adjustable_parts:
        adj_list = []
        for a in p.adjustments.all():
            adj_list.append({
                'key': a.param_key,
                'label': a.label,
                'min': a.min_value,
                'max': a.max_value,
                'step': a.step,
                'default': a.default_value,
                'unit': a.unit,
                'order': a.display_order,
            })
        adj_list.sort(key=lambda x: x['order'])
        part_adjustments[p.name] = adj_list

    context = {
        'car': selected_car,
        'track': selected_track,
        'final_time': final_display,
        'base_time': final_display,
        'track_length': track_length,
        'base_speed': base_speed,
        'base_power': selected_car.power_hp,
        'base_weight': selected_car.weight_kg,
        'categories': categories,
        'has_telemetry': has_telemetry,
        'telemetry_laps': json.dumps(telemetry_json),
        'telemetry_count': min(len(telemetry_laps), 10),
        'best_lap_seconds': best_time,
        'best_projected_seconds': best_projected_seconds,
        'tuning_base_seconds': tuning_base,
        'part_adjustments': json.dumps(part_adjustments),
        'preset_mods': json.dumps(_get_preset_mods(selected_car, selected_track)),
    }
    return render(request, 'simulator/dashboard.html', context)


@login_required
def api_telemetry_laps(request):
    car_id = request.GET.get('car', '')
    track_id = request.GET.get('track', '')

    laps = TelemetryLap.objects.filter(is_complete=True)
    if car_id:
        laps = laps.filter(car__slug_id=car_id)
    if track_id:
        laps = laps.filter(track__slug_id=track_id)

    laps = laps.order_by('lap_time_ms')[:10]

    data = [
        {
            'lap_number': l.lap_number,
            'lap_time_seconds': l.lap_time_seconds,
            'max_speed_kmh': l.max_speed_kmh,
            'min_speed_kmh': l.min_speed_kmh,
            'avg_speed_kmh': l.avg_speed_kmh,
            'avg_throttle_pct': l.avg_throttle_pct,
            'avg_brake_pct': l.avg_brake_pct,
            'max_rpm': l.max_rpm,
            'total_frames': l.total_frames,
            'imported_at': l.imported_at.isoformat(),
        }
        for l in laps
    ]
    return JsonResponse({'laps': data})


@login_required
def api_import_telemetry(request):
    """
    Import telemetry laps.
    - GET:  import from TelemetryIQ SQLite database (uses db_path param or default)
    - POST: import from uploaded JSON export file (multipart form, field name: 'file')
    """
    import tempfile, io

    if request.method == 'POST' and request.FILES.get('file'):
        from revlabs.telemetry_import import run_import_from_json
        uploaded = request.FILES['file']
        suffix = '.json'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in uploaded.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        try:
            buf = io.StringIO()
            result = run_import_from_json(tmp_path, print_func=lambda msg: buf.write(msg + '\n'))
            result['log'] = buf.getvalue()
        finally:
            import os
            os.unlink(tmp_path)

        if result.get('error'):
            return JsonResponse({'status': 'error', 'message': result['error'], 'log': result['log']}, status=400)
        return JsonResponse({'status': 'ok', **result})

    from revlabs.telemetry_import import run_import

    db_path = request.GET.get('db_path') or r'..\TelemetryIQ\telemetry.db'

    buf = io.StringIO()
    result = run_import(db_path, print_func=lambda msg: buf.write(msg + '\n'))
    result['log'] = buf.getvalue()

    if result.get('error'):
        return JsonResponse({'status': 'error', 'message': result['error'], 'log': result['log']}, status=400)

    return JsonResponse({'status': 'ok', **result})

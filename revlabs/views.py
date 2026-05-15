from django.shortcuts import render
from .models import Car, Track, PartCategory

def time_to_seconds(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + float(s)

def seconds_to_time(seconds):
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"

def track_selection(request):
    tracks = Track.objects.all()
    return render(request, 'simulator/track_selection.html', {'tracks': tracks})

def car_selection(request):
    track_id = request.GET.get('track', 'interlagos')
    
    try:
        selected_track = Track.objects.get(slug_id=track_id)
    except Track.DoesNotExist:
        selected_track = Track.objects.first()
    
    cars = Car.objects.all()
    
    context = {
        'cars': cars,
        'selected_track': selected_track 
    }
    return render(request, 'simulator/car_selection.html', context)

def dashboard(request):
    car_id = request.GET.get('car', 'mercedes') 
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

    track_length = selected_track.length_km
    track_multiplier = selected_track.speed_multiplier
    
    base_speed = selected_car.base_avg_speed_kmh * track_multiplier
    base_seconds = (track_length / base_speed) * 3600
    final_time = seconds_to_time(base_seconds)

    context = {
        'car': selected_car,
        'track': selected_track,
        'final_time': final_time,
        'base_time': final_time,
        'track_length': track_length,
        'base_speed': base_speed,
        'base_power': selected_car.power_hp,
        'base_weight': selected_car.weight_kg,
        'categories': categories
    }
    return render(request, 'simulator/dashboard.html', context)
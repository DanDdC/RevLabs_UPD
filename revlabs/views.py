from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import RevLabsAuthenticationForm, RevLabsUserCreationForm
from .models import Car, Track, PartCategory


def time_to_seconds(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + float(s)


def seconds_to_time(seconds):
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"


def home(request):
    """Public landing page. It is the only page available before authentication."""
    context = {
        'featured_track': Track.objects.filter(slug_id='nurburgring').first() or Track.objects.first(),
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
        hero_track = Track.objects.get(slug_id='nurburgring')
        other_tracks = Track.objects.exclude(slug_id='nurburgring')
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

    cars = Car.objects.all()

    context = {
        'cars': cars,
        'selected_track': selected_track,
    }
    return render(request, 'simulator/car_selection.html', context)


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
        'categories': categories,
    }
    return render(request, 'simulator/dashboard.html', context)

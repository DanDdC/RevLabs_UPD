import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.models import Car, Track

Car.objects.all().delete()
Track.objects.all().delete()

cars = [
    Car(slug_id='vw-fusca', name='VW Fusca 1300', base_avg_speed_kmh=108.0, power_hp=44, weight_kg=820, image_path='img/cars/vw-fusca.png', car_code=0),

    Car(slug_id='porsche-911', name='Porsche 911 GT3 RS (992)', base_avg_speed_kmh=183.3, power_hp=525, weight_kg=1450, image_path='img/cars/porsche-911.png', car_code=3539),
    Car(slug_id='mercedes-amg', name='Mercedes-AMG GT Black Series \'20', base_avg_speed_kmh=186.0, power_hp=730, weight_kg=1540, image_path='img/cars/mercedes-amg.png', car_code=3485),
]
Car.objects.bulk_create(cars)

tracks = [
    Track(slug_id='nurburgring', name='Nürburgring Nordschleife', length_km=20.832, speed_multiplier=0.85, image_path='img/layout/nurburgring.png', bg_image_path='img/bg/nurburgring.jpg', track_id=0),
    Track(slug_id='spa', name='Spa-Francorchamps', length_km=7.004, speed_multiplier=0.95, image_path='img/layout/spa.png', bg_image_path='img/bg/spa.jpg', track_id=0),
    Track(slug_id='suzuka', name='Suzuka Circuit', length_km=5.807, speed_multiplier=0.90, image_path='img/layout/suzuka.png', bg_image_path='img/bg/suzuka.jpg', track_id=0),
    Track(slug_id='monza', name='Autodromo Nazionale di Monza', length_km=5.793, speed_multiplier=1.05, image_path='img/layout/monza.png', bg_image_path='img/bg/monza.jpg', track_id=0),
    Track(slug_id='silverstone', name='Silverstone Circuit', length_km=5.891, speed_multiplier=0.95, image_path='img/layout/silverstone.png', bg_image_path='img/bg/silverstone.jpg', track_id=0),
    Track(slug_id='interlagos', name='Autódromo José Carlos Pace (Interlagos)', length_km=4.309, speed_multiplier=0.92, image_path='img/layout/interlagos.png', bg_image_path='img/bg/interlagos.jpg', track_id=152),
]
Track.objects.bulk_create(tracks)

print(f"Criados {Car.objects.count()} carros e {Track.objects.count()} pistas.")

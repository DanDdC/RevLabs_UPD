import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.models import Car, Track

Car.objects.all().delete()
Track.objects.all().delete()

cars = [
    Car(slug_id='vw-fusca', name='VW Fusca 1300', base_avg_speed_kmh=108.0, power_hp=44, weight_kg=820, image_path='img/cars/fusca.png', car_code=0),

    Car(slug_id='ferrari-458', name='Ferrari 458 Italia', base_avg_speed_kmh=165.0, power_hp=570, weight_kg=1380, image_path='img/cars/ferrari-458.png', car_code=0),
    Car(slug_id='porsche-911', name='Porsche 911 GT3 RS (992)', base_avg_speed_kmh=183.3, power_hp=525, weight_kg=1450, image_path='img/cars/porsche-911.png', car_code=3539),
    Car(slug_id='mercedes-amg', name='Mercedes-AMG GT Black Series \'20', base_avg_speed_kmh=186.0, power_hp=730, weight_kg=1540, image_path='img/cars/mercedes-amg.png', car_code=0),
]
Car.objects.bulk_create(cars)

tracks = [
    Track(slug_id='nurburgring', name='Nürburgring Nordschleife', length_km=20.832, speed_multiplier=0.85, image_path='img/tracks/nurburgring.png', bg_image_path='img/tracks/nurburgring-bg.jpg', track_id=0),
    Track(slug_id='spa', name='Spa-Francorchamps', length_km=7.004, speed_multiplier=0.95, image_path='img/tracks/spa.png', bg_image_path='img/tracks/spa-bg.jpg', track_id=0),
    Track(slug_id='suzuka', name='Suzuka Circuit', length_km=5.807, speed_multiplier=0.90, image_path='img/tracks/suzuka.png', bg_image_path='img/tracks/suzuka-bg.jpg', track_id=0),
    Track(slug_id='monza', name='Autodromo Nazionale di Monza', length_km=5.793, speed_multiplier=1.05, image_path='img/tracks/monza.png', bg_image_path='img/tracks/monza-bg.jpg', track_id=0),
    Track(slug_id='silverstone', name='Silverstone Circuit', length_km=5.891, speed_multiplier=0.95, image_path='img/tracks/silverstone.png', bg_image_path='img/tracks/silverstone-bg.jpg', track_id=0),
    Track(slug_id='interlagos', name='Autódromo José Carlos Pace (Interlagos)', length_km=4.309, speed_multiplier=0.92, image_path='img/tracks/interlagos.png', bg_image_path='img/tracks/interlagos-bg.jpg', track_id=152),
]
Track.objects.bulk_create(tracks)

print(f"Criados {Car.objects.count()} carros e {Track.objects.count()} pistas.")

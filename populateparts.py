import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.models import PartCategory, CarPart, Car

print("Iniciando a reestruturação do catálogo com as 40 modificações mapeadas...")

PartCategory.objects.all().delete()
CarPart.objects.all().delete()

cats = {
    'Brake Discs': PartCategory.objects.create(main_category='brakes', name='Brake Discs'),
    'Brake Calipers': PartCategory.objects.create(main_category='brakes', name='Brake Calipers'),
    'Coilover': PartCategory.objects.create(main_category='suspension', name='Coilover'),
    'Anti-roll bar': PartCategory.objects.create(main_category='suspension', name='Anti-roll bar'),
    'Diffuser': PartCategory.objects.create(main_category='aerodynamics', name='Diffuser'),
    'Front Aero': PartCategory.objects.create(main_category='aerodynamics', name='Front Aero'),
    'Rear Aero': PartCategory.objects.create(main_category='aerodynamics', name='Rear Aero'),
    'Engine Block': PartCategory.objects.create(main_category='engine', name='Engine Block'),
    'Air Filters': PartCategory.objects.create(main_category='engine', name='Air Filters'),
    'ECU': PartCategory.objects.create(main_category='engine', name='ECU'),
    'Turbochargers': PartCategory.objects.create(main_category='engine', name='Turbochargers'),
    'Superchargers': PartCategory.objects.create(main_category='engine', name='Superchargers'),
    'Clutch & Flywheel': PartCategory.objects.create(main_category='transmission', name='Clutch & Flywheel'),
    'Gearbox': PartCategory.objects.create(main_category='transmission', name='Gearbox'),
    'Differential': PartCategory.objects.create(main_category='drivetrain', name='Differential'),
    'Driveshaft': PartCategory.objects.create(main_category='drivetrain', name='Driveshaft'),
    'Weight Reduction': PartCategory.objects.create(main_category='chassis', name='Weight Reduction'),
    'Chassis Reinforcement': PartCategory.objects.create(main_category='chassis', name='Chassis Reinforcement'),
    'Touring': PartCategory.objects.create(main_category='tyres', name='Touring'),
    'Performance': PartCategory.objects.create(main_category='tyres', name='Performance'),
    'Semi-Slick': PartCategory.objects.create(main_category='tyres', name='Semi-Slick'),
    'High-Performance': PartCategory.objects.create(main_category='tyres', name='High-Performance'),
    'Slick': PartCategory.objects.create(main_category='tyres', name='Slick'),
}

# FORMATAÇÃO: Categoria, Nome da Peça, HP Adicionado, Peso Adicionado (kg), Imagem Específica
catalogo_pecas = [
    # Engine Block
    (cats['Engine Block'], "Forged Aluminum Pistons", 15, -2, "img/mods/pistao.png"),
    (cats['Engine Block'], "Bore Up", 35, 4, "img/mods/boreup.png"),
    (cats['Engine Block'], "Engine Balance Tuning", 12, -4, "img/mods/enginetuning.png"),
    (cats['Engine Block'], "High Compression Pistons", 25, 1, "img/mods/pistons.png"),
    
    # Air Filters & ECU
    (cats['Air Filters'], "Cold Air Intake", 8, 0, "img/mods/filtro_ar.png"),
    (cats['ECU'], "Stage 2 ECU Remap", 45, 0, "img/mods/ecu.png"),

    # Forced Induction
    (cats['Turbochargers'], "Low-RPM Turbocharger", 60, 15, "img/mods/turbo-icon.png"),
    (cats['Turbochargers'], "High-RPM Turbocharger", 110, 22, "img/mods/highturbo.png"),
    (cats['Superchargers'], "Supercharger (Low-Torque)", 70, 25, "img/mods/supercompressor.png"),
    (cats['Superchargers'], "Supercharger (High-Torque)", 95, 30, "img/mods/highsupercharger.png"),

    # Transmission
    (cats['Clutch & Flywheel'], "Sports Clutch & Flywheel", 0, -3, "img/mods/clutch-flywheel.png"),
    (cats['Clutch & Flywheel'], "Twin-Plate Racing Clutch", 0, -6, "img/mods/twin-clutch.png"),
    (cats['Clutch & Flywheel'], "Lightweight Flywheel", 0, -5, "img/mods/flywheel.png"),

    (cats['Gearbox'], "Close-Ratio Transmission (Low)", 0, 0, "img/mods/transmission.png"),
    (cats['Gearbox'], "Close-Ratio Transmission (High)", 0, 0, "img/mods/transmission.png"),
    (cats['Gearbox'], "Sequential Racing Gearbox", 0, -15, "img/mods/gearbox.png"),

    # Drivetrain
    (cats['Differential'], "1.5-Way LSD", 0, 3, "img/mods/slipdiff.png"),
    (cats['Differential'], "2-Way Racing LSD", 0, 5, "img/mods/lsd.png"),
    (cats['Driveshaft'], "Carbon Fiber Driveshaft", 0, -8, "img/mods/driveshaft.png"),

    # Brakes
    (cats['Brake Discs'], "Slotted Steel Discs", 0, 2, "img/mods/rotors.png"),
    (cats['Brake Discs'], "Carbon Ceramic Discs", 0, -12, "img/mods/discs.png"),
    (cats['Brake Calipers'], "Sports Brake Calipers", 0, -2, "img/mods/sportscalipers.png"),
    (cats['Brake Calipers'], "Performance Brake Kit", 0, 4, "img/mods/brakekit.png"),
    (cats['Brake Calipers'], "Racing Calipers", 0, -4, "img/mods/calipers.png"),

    # Suspension
    (cats['Coilover'], "Street Coilovers", 0, -3, "img/mods/streetcoilovers.png"),
    (cats['Coilover'], "Fully Adjustable Race Coilovers", 0, -8, "img/mods/racecoilovers.png"),
    (cats['Anti-roll bar'], "Stiffened Anti-roll Bars", 0, 4, "img/mods/antirollbars.png"),

    # Aerodynamics
    (cats['Diffuser'], "Rear Diffuser", 0, 3, "img/mods/diffuser.png"),
    (cats['Diffuser'], "Carbon Fiber Rear Diffuser", 0, 1, "img/mods/fiberdiffuser.png"),
    (cats['Front Aero'], "Carbon Fiber Splitter", 0, 2, "img/mods/fibersplitter.png"),
    (cats['Rear Aero'], "Adjustable GT Wing", 0, 8, "img/mods/wing.png"),

    # Chassis & Weight Reduction
    (cats['Weight Reduction'], "Stage 1: Strip Interior", 0, -60, "img/mods/weight-reduction.png"),
    (cats['Weight Reduction'], "Stage 2: Carbon Fiber Panels", 0, -70, "img/mods/weight-reduction.png"),
    (cats['Weight Reduction'], "Stage 3: Lexan Windows & Shell", 0, -50, "img/mods/weight-reduction.png"),
    (cats['Chassis Reinforcement'], "6-Point Roll Cage", 0, 35, "img/mods/rollcage.png"),

    # Tyres
    (cats['Touring'], "Touring Tyres", 0, 0, "img/mods/touringtyres.png"),
    (cats['Performance'], "Performance Tyres", 0, -1, "img/mods/perftyres.png"),
    (cats['High-Performance'], "High-Performance Tyres", 0, -2, "img/mods/highperftyres.png"),
    (cats['Semi-Slick'], "Semi-Slick Track Tyres", 0, -4, "img/mods/tracktyres.png"),
    (cats['Slick'], "Racing Slicks", 0, -6, "img/mods/racingslicks.png"),
]

print("Injetando catálogo de peças com as 40 imagens e HPs correspondentes...")
for categoria, nome, hp, peso, img in catalogo_pecas:
    CarPart.objects.create(category=categoria, name=nome, added_hp=hp, added_weight_kg=peso, image_path=img)

print("Calibrando as velocidades médias realistas dos 6 carros...")
car_calibrations = {
    'vw-fusca': 108.0,
    'vw-brasilia': 108.0,
    'vw-parati': 125.0,
    'ferrari-458': 165.0,
    'porsche-911': 183.3,
    'mercedes-amg': 186.0
}

for slug, speed in car_calibrations.items():
    Car.objects.filter(slug_id=slug).update(base_avg_speed_kmh=speed)

print("Catálogo perfeito!")
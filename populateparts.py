import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.models import PartCategory, CarPart, Car

print("Deletando catálogo antigo...")

PartCategory.objects.all().delete()
CarPart.objects.all().delete()

print("Criando categorias...")

cats = {
    # Engine
    'ECU': PartCategory.objects.create(main_category='engine', name='ECU'),
    'Air Filters': PartCategory.objects.create(main_category='engine', name='Air Filters'),
    'Exhaust': PartCategory.objects.create(main_category='engine', name='Exhaust'),
    'Turbochargers': PartCategory.objects.create(main_category='engine', name='Turbochargers'),
    'Superchargers': PartCategory.objects.create(main_category='engine', name='Superchargers'),
    'Intercooler': PartCategory.objects.create(main_category='engine', name='Intercooler'),
    'Engine Block': PartCategory.objects.create(main_category='engine', name='Engine Block'),
    'Camshaft': PartCategory.objects.create(main_category='engine', name='Camshaft'),
    'Crankshaft': PartCategory.objects.create(main_category='engine', name='Crankshaft'),
    'Pistons': PartCategory.objects.create(main_category='engine', name='Pistons'),
    'Anti-Lag System': PartCategory.objects.create(main_category='engine', name='Anti-Lag System'),
    'Nitro': PartCategory.objects.create(main_category='engine', name='Nitro'),

    # Suspension
    'Coilover': PartCategory.objects.create(main_category='suspension', name='Coilover'),
    'Anti-roll bar': PartCategory.objects.create(main_category='suspension', name='Anti-roll bar'),

    # Transmission
    'Clutch & Flywheel': PartCategory.objects.create(main_category='transmission', name='Clutch & Flywheel'),
    'Gearbox': PartCategory.objects.create(main_category='transmission', name='Gearbox'),

    # Drivetrain
    'Differential': PartCategory.objects.create(main_category='drivetrain', name='Differential'),
    'Driveshaft': PartCategory.objects.create(main_category='drivetrain', name='Driveshaft'),
    'Center Diff': PartCategory.objects.create(main_category='drivetrain', name='Center Diff'),
    'LSD Controller': PartCategory.objects.create(main_category='drivetrain', name='LSD Controller'),

    # Brakes
    'Brake Discs': PartCategory.objects.create(main_category='brakes', name='Brake Discs'),
    'Brake Calipers': PartCategory.objects.create(main_category='brakes', name='Brake Calipers'),
    'Brake Pads': PartCategory.objects.create(main_category='brakes', name='Brake Pads'),
    'Brake Controller': PartCategory.objects.create(main_category='brakes', name='Brake Controller'),

    # Chassis
    'Weight Reduction': PartCategory.objects.create(main_category='chassis', name='Weight Reduction'),
    'Chassis Reinforcement': PartCategory.objects.create(main_category='chassis', name='Chassis Reinforcement'),
    'Body': PartCategory.objects.create(main_category='chassis', name='Body'),
    'Steering': PartCategory.objects.create(main_category='chassis', name='Steering'),
    'Handbrake': PartCategory.objects.create(main_category='chassis', name='Handbrake'),
    'Ballast': PartCategory.objects.create(main_category='chassis', name='Ballast'),

    # Aerodynamics
    'Diffuser': PartCategory.objects.create(main_category='aerodynamics', name='Diffuser'),
    'Front Aero': PartCategory.objects.create(main_category='aerodynamics', name='Front Aero'),
    'Rear Aero': PartCategory.objects.create(main_category='aerodynamics', name='Rear Aero'),

    # Tyres
    'Comfort': PartCategory.objects.create(main_category='tyres', name='Comfort'),
    'Touring': PartCategory.objects.create(main_category='tyres', name='Touring'),
    'Performance': PartCategory.objects.create(main_category='tyres', name='Performance'),
    'Sports': PartCategory.objects.create(main_category='tyres', name='Sports'),
    'High-Performance': PartCategory.objects.create(main_category='tyres', name='High-Performance'),
    'Semi-Slick': PartCategory.objects.create(main_category='tyres', name='Semi-Slick'),
    'Racing': PartCategory.objects.create(main_category='tyres', name='Racing'),
    'Intermediate': PartCategory.objects.create(main_category='tyres', name='Intermediate'),
    'Wet': PartCategory.objects.create(main_category='tyres', name='Wet'),
    'Dirt': PartCategory.objects.create(main_category='tyres', name='Dirt'),
}

print("Inserindo todas as pecas do catalogo GT7...")

catalogo_pecas = [
    # ===== SPORTS TIER =====
    (cats['ECU'], 'Sports Computer', 15, 0, 'img/mods/ecu.png', 'sports'),
    (cats['Air Filters'], 'Sports Air Filter', 5, 0, 'img/mods/filtro_ar.png', 'sports'),
    (cats['Exhaust'], 'Sports Muffler', 10, -2, 'img/mods/filtro_ar.png', 'sports'),
    (cats['Brake Pads'], 'Sports Brake Pads', 0, 0, 'img/mods/sportscalipers.png', 'sports'),
    (cats['Weight Reduction'], 'Stage 1 Weight Reduction', 0, -60, 'img/mods/weight-reduction.png', 'sports'),
    (cats['Coilover'], 'Street Suspension', 0, -2, 'img/mods/streetcoilovers.png', 'sports'),
    (cats['Sports'], 'Sports Hard Tyres', 0, 0, 'img/mods/tracktyres.png', 'sports'),
    (cats['Sports'], 'Sports Medium Tyres', 0, -2, 'img/mods/sportsmedium.png', 'sports'),
    (cats['Sports'], 'Sports Soft Tyres', 0, -3, 'img/mods/racingslicks.png', 'sports'),
    (cats['Comfort'], 'Comfort Hard Tyres', 0, 0, 'img/mods/touringtyres.png', 'sports'),
    (cats['Comfort'], 'Comfort Medium Tyres', 0, 0, 'img/mods/touringtyres.png', 'sports'),
    (cats['Comfort'], 'Comfort Soft Tyres', 0, 0, 'img/mods/touringtyres.png', 'sports'),

    # ===== CLUB SPORTS TIER =====
    (cats['Engine Block'], 'Bore Up', 35, 4, 'img/mods/boreup.png', 'club_sports'),
    (cats['Camshaft'], 'High Lift Camshaft', 20, 1, 'img/mods/enginetuning.png', 'club_sports'),
    (cats['Pistons'], 'High Compression Pistons', 25, 2, 'img/mods/pistons.png', 'club_sports'),
    (cats['Weight Reduction'], 'Stage 2 Weight Reduction', 0, -70, 'img/mods/weight-reduction.png', 'club_sports'),
    (cats['Coilover'], 'Sports Suspension', 0, -4, 'img/mods/racecoilovers.png', 'club_sports'),
    (cats['Brake Calipers'], 'Sports Brake Kit', 0, 1, 'img/mods/sportscalipers.png', 'club_sports'),
    (cats['Clutch & Flywheel'], 'Sports Clutch & Flywheel', 0, -3, 'img/mods/clutch-flywheel.png', 'club_sports'),
    (cats['Differential'], 'One-Way LSD', 0, 3, 'img/mods/slipdiff.png', 'club_sports'),
    (cats['Differential'], 'Two-Way LSD', 0, 5, 'img/mods/lsd.png', 'club_sports'),
    (cats['Gearbox'], 'Close-Ratio Transmission (Low)', 0, 2, 'img/mods/transmission.png', 'club_sports'),
    (cats['Gearbox'], 'Close-Ratio Transmission (High)', 0, 2, 'img/mods/transmission.png', 'club_sports'),
    (cats['ECU'], 'Power Restrictor', -10, 0, 'img/mods/ecu.png', 'club_sports'),
    (cats['Ballast'], 'Ballast', 0, 50, 'img/mods/weight-reduction.png', 'club_sports'),
    (cats['Dirt'], 'Dirt Tyres', 0, 0, 'img/mods/tracktyres.png', 'club_sports'),

    # ===== SEMI-RACING TIER =====
    (cats['Crankshaft'], 'Racing Crankshaft', 18, -3, 'img/mods/enginetuning.png', 'semi_racing'),
    (cats['Weight Reduction'], 'Stage 3 Weight Reduction', 0, -50, 'img/mods/weight-reduction.png', 'semi_racing'),
    (cats['Chassis Reinforcement'], 'Increase Body Rigidity', 0, 35, 'img/mods/rollcage.png', 'semi_racing'),
    (cats['ECU'], 'Fully Customizable Computer', 25, 0, 'img/mods/ecu.png', 'semi_racing'),
    (cats['Exhaust'], 'Semi-Racing Muffler', 18, -3, 'img/mods/filtro_ar.png', 'semi_racing'),
    (cats['Turbochargers'], 'Low-RPM Turbocharger', 60, 15, 'img/mods/turbo-icon.png', 'semi_racing'),
    (cats['Turbochargers'], 'Medium-RPM Turbocharger', 85, 18, 'img/mods/turbo-icon.png', 'semi_racing'),
    (cats['Turbochargers'], 'High-RPM Turbocharger', 110, 22, 'img/mods/highturbo.png', 'semi_racing'),
    (cats['Superchargers'], 'Low-End Torque Supercharger', 70, 25, 'img/mods/supercompressor.png', 'semi_racing'),
    (cats['Intercooler'], 'Sports Intercooler', 5, 3, 'img/mods/turbo-icon.png', 'semi_racing'),
    (cats['Coilover'], 'Height-Adjustable Sports Suspension', 0, -5, 'img/mods/racecoilovers.png', 'semi_racing'),
    (cats['Clutch & Flywheel'], 'Semi-Racing Clutch & Flywheel', 0, -5, 'img/mods/clutch-flywheel.png', 'semi_racing'),
    (cats['Differential'], 'Fully Customizable LSD', 0, 2, 'img/mods/lsd.png', 'semi_racing'),
    (cats['Gearbox'], 'Fully Customizable Manual Transmission', 0, 5, 'img/mods/gearbox.png', 'semi_racing'),

    # ===== RACING TIER =====
    (cats['Engine Block'], 'Stroke Up', 45, 6, 'img/mods/boreup.png', 'racing'),
    (cats['Pistons'], 'Engine Balance Tuning', 12, -4, 'img/mods/enginetuning.png', 'racing'),
    (cats['Pistons'], 'Polish Parts', 8, -2, 'img/mods/pistons.png', 'racing'),
    (cats['Weight Reduction'], 'Stage 4 Weight Reduction', 0, -40, 'img/mods/weight-reduction.png', 'racing'),
    (cats['Anti-Lag System'], 'Anti-Lag System', 15, 2, 'img/mods/turbo-icon.png', 'racing'),
    (cats['Superchargers'], 'High-End Torque Supercharger', 95, 30, 'img/mods/highsupercharger.png', 'racing'),
    (cats['Intercooler'], 'Racing Intercooler', 10, 5, 'img/mods/turbo-icon.png', 'racing'),
    (cats['Air Filters'], 'Racing Air Filter', 8, 0, 'img/mods/filtro_ar.png', 'racing'),
    (cats['Exhaust'], 'Racing Muffler', 22, -4, 'img/mods/filtro_ar.png', 'racing'),
    (cats['Exhaust'], 'Racing Exhaust Manifold', 12, -2, 'img/mods/filtro_ar.png', 'racing'),
    (cats['Brake Pads'], 'Racing Brake Pads', 0, 0, 'img/mods/calipers.png', 'racing'),
    (cats['Brake Discs'], 'Racing Brake Kit (Slotted Discs)', 0, 2, 'img/mods/rotors.png', 'racing'),
    (cats['Brake Discs'], 'Racing Brake Kit (Drilled Discs)', 0, 1, 'img/mods/discs.png', 'racing'),
    (cats['Brake Controller'], 'Brake Balance Controller', 0, 1, 'img/mods/calipers.png', 'racing'),
    (cats['Coilover'], 'Fully Customizable Suspension', 0, -8, 'img/mods/racecoilovers.png', 'racing'),
    (cats['Clutch & Flywheel'], 'Racing Clutch & Flywheel', 0, -6, 'img/mods/twin-clutch.png', 'racing'),
    (cats['Center Diff'], 'Torque-Vectoring Center Differential', 0, 5, 'img/mods/driveshaft.png', 'racing'),
    (cats['LSD Controller'], 'Active LSD Controller', 0, 2, 'img/mods/lsd.png', 'racing'),
    (cats['Gearbox'], 'Fully Customizable Racing Transmission', 0, -5, 'img/mods/gearbox.png', 'racing'),
    (cats['Racing'], 'Racing Hard Tyres', 0, 0, 'img/mods/tracktyres.png', 'racing'),
    (cats['Racing'], 'Racing Medium Tyres', 0, -2, 'img/mods/racingslicks.png', 'racing'),
    (cats['Racing'], 'Racing Soft Tyres', 0, -4, 'img/mods/racingslicks.png', 'racing'),

    # ===== EXTREME TIER =====
    (cats['Engine Block'], 'New Engine', 50, 0, 'img/mods/enginetuning.png', 'extreme'),
    (cats['Body'], 'New Body (Rigidity Refresh)', 0, -25, 'img/mods/rollcage.png', 'extreme'),
    (cats['Nitro'], 'Nitro System', 50, 5, 'img/mods/turbo-icon.png', 'extreme'),
    (cats['Brake Discs'], 'Carbon Ceramic Brake Kit', 0, -12, 'img/mods/discs.png', 'extreme'),
    (cats['Handbrake'], 'Hydraulic Handbrake', 0, 3, 'img/mods/calipers.png', 'extreme'),
    (cats['Steering'], 'Steering Angle Adapter', 0, 2, 'img/mods/racecoilovers.png', 'extreme'),
    (cats['Steering'], 'Four-Wheel Steering Controller', 0, 5, 'img/mods/racecoilovers.png', 'extreme'),
    (cats['Intermediate'], 'Intermediate Tyres', 0, 0, 'img/mods/tracktyres.png', 'extreme'),
    (cats['Wet'], 'Heavy Wet Tyres', 0, 0, 'img/mods/tracktyres.png', 'extreme'),

    # ===== SPECIAL / ROULETTE TIER =====
    (cats['Turbochargers'], 'Ultra-High RPM Turbocharger', 130, 25, 'img/mods/highturbo.png', 'special'),
    (cats['Superchargers'], 'High-RPM S Supercharger', 110, 28, 'img/mods/highsupercharger.png', 'special'),
    (cats['Pistons'], 'Titanium Connecting Rods & Pistons', 30, -6, 'img/mods/pistons.png', 'special'),
    (cats['Engine Block'], 'Bore Up S', 50, 5, 'img/mods/boreup.png', 'special'),
    (cats['Engine Block'], 'Stroke Up S', 60, 8, 'img/mods/boreup.png', 'special'),
    (cats['Camshaft'], 'High Lift Camshaft S', 30, 1, 'img/mods/enginetuning.png', 'special'),
    (cats['Driveshaft'], 'Carbon Propeller Shaft', 0, -10, 'img/mods/driveshaft.png', 'special'),
    (cats['Weight Reduction'], 'Stage 5 Weight Reduction', 0, -30, 'img/mods/weight-reduction.png', 'special'),
    (cats['Weight Reduction'], 'Stage 6 Weight Reduction', 0, -20, 'img/mods/weight-reduction.png', 'special'),

    # ===== CUSTOM / AFTERMARKET (nao sao pecas especificas do GT7) =====
    (cats['Anti-roll bar'], 'Stiffened Anti-roll Bars', 0, 4, 'img/mods/antirollbars.png', None),
    (cats['Diffuser'], 'Rear Diffuser', 0, 3, 'img/mods/diffuser.png', None),
    (cats['Diffuser'], 'Carbon Fiber Rear Diffuser', 0, 1, 'img/mods/fiberdiffuser.png', None),
    (cats['Front Aero'], 'Carbon Fiber Splitter', 0, 2, 'img/mods/fibersplitter.png', None),
    (cats['Rear Aero'], 'Adjustable GT Wing', 0, 8, 'img/mods/wing.png', None),
    (cats['Brake Calipers'], 'Performance Brake Kit', 0, 4, 'img/mods/brakekit.png', None),
    (cats['Touring'], 'Touring Tyres', 0, 0, 'img/mods/touringtyres.png', None),
    (cats['Performance'], 'Performance Tyres', 0, -1, 'img/mods/perftyres.png', None),
    (cats['High-Performance'], 'High-Performance Tyres', 0, -2, 'img/mods/highperftyres.png', None),
    (cats['Semi-Slick'], 'Semi-Slick Track Tyres', 0, -4, 'img/mods/tracktyres.png', None),
    (cats['Pistons'], 'Forged Aluminum Pistons', 15, -2, 'img/mods/pistao.png', None),
]

print(f"Inserindo {len(catalogo_pecas)} pecas no banco...")
for categoria, nome, hp, peso, img, tier in catalogo_pecas:
    CarPart.objects.create(
        category=categoria,
        name=nome,
        added_hp=hp,
        added_weight_kg=peso,
        image_path=img,
        gt7_tier=tier,
    )

print("Atualizando velocidades medias dos carros...")
car_calibrations = {
    'vw-fusca': 108.0,
    'ferrari-458': 165.0,
    'porsche-911': 183.3,
    'mercedes-amg': 186.0
}

for slug, speed in car_calibrations.items():
    Car.objects.filter(slug_id=slug).update(base_avg_speed_kmh=speed)

print(f"Catalogo completo com {len(catalogo_pecas)} pecas!")

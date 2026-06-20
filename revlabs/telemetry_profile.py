from django.db.models import Avg, Max, Min


MOD_PROFILES = {
    # Engine / Power
    'Bore Up': {'type': 'power', 'tier': 0.55},
    'Stroke Up': {'type': 'power', 'tier': 0.65},
    'Bore Up S': {'type': 'power', 'tier': 0.75},
    'Stroke Up S': {'type': 'power', 'tier': 0.85},
    'Engine Balance Tuning': {'type': 'power', 'tier': 0.45},
    'High Compression Pistons': {'type': 'power', 'tier': 0.55},
    'Polish Parts': {'type': 'power', 'tier': 0.25},
    'Titanium Connecting Rods & Pistons': {'type': 'power', 'tier': 0.75},
    'High Lift Camshaft': {'type': 'power', 'tier': 0.45},
    'High Lift Camshaft S': {'type': 'power', 'tier': 0.65},
    'Racing Crankshaft': {'type': 'power', 'tier': 0.55},
    'New Engine': {'type': 'power', 'tier': 0.95},
    'Sports Computer': {'type': 'power', 'tier': 0.25},
    'Fully Customizable Computer': {'type': 'power', 'tier': 0.45},
    'Sports Air Filter': {'type': 'power', 'tier': 0.12},
    'Racing Air Filter': {'type': 'power', 'tier': 0.22},
    # Exhaust
    'Sports Muffler': {'type': 'power', 'tier': 0.3},
    'Semi-Racing Muffler': {'type': 'power', 'tier': 0.45},
    'Racing Muffler': {'type': 'power', 'tier': 0.55},
    'Racing Exhaust Manifold': {'type': 'power', 'tier': 0.35},
    # Intercooler
    'Sports Intercooler': {'type': 'power', 'tier': 0.15},
    'Racing Intercooler': {'type': 'power', 'tier': 0.25},
    # Nitro
    'Nitro System': {'type': 'power', 'tier': 1.1},

    # Forced Induction
    'Low-RPM Turbocharger': {'type': 'forced_induction', 'accel_bias': 0.7, 'tier': 0.5},
    'Medium-RPM Turbocharger': {'type': 'forced_induction', 'accel_bias': 0.6, 'tier': 0.6},
    'High-RPM Turbocharger': {'type': 'forced_induction', 'accel_bias': 0.4, 'tier': 0.7},
    'Ultra-High RPM Turbocharger': {'type': 'forced_induction', 'accel_bias': 0.3, 'tier': 0.85},
    'Low-End Torque Supercharger': {'type': 'forced_induction', 'accel_bias': 0.8, 'tier': 0.6},
    'High-End Torque Supercharger': {'type': 'forced_induction', 'accel_bias': 0.5, 'tier': 0.72},
    'High-RPM S Supercharger': {'type': 'forced_induction', 'accel_bias': 0.4, 'tier': 0.88},
    'Anti-Lag System': {'type': 'forced_induction', 'accel_bias': 0.7, 'tier': 0.35},

    # Weight Reduction
    'Stage 1 Weight Reduction': {'type': 'weight', 'tier': 0.25},
    'Stage 2 Weight Reduction': {'type': 'weight', 'tier': 0.35},
    'Stage 3 Weight Reduction': {'type': 'weight', 'tier': 0.45},
    'Stage 4 Weight Reduction': {'type': 'weight', 'tier': 0.55},
    'Stage 5 Weight Reduction': {'type': 'weight', 'tier': 0.65},
    'Stage 6 Weight Reduction': {'type': 'weight', 'tier': 0.75},

    # Suspension
    'Street Suspension': {'type': 'suspension', 'tier': 0.18},
    'Sports Suspension': {'type': 'suspension', 'tier': 0.3},
    'Height-Adjustable Sports Suspension': {'type': 'suspension', 'tier': 0.45},
    'Fully Customizable Suspension': {'type': 'suspension', 'tier': 0.65},
    'Stiffened Anti-roll Bars': {'type': 'suspension', 'tier': 0.22},
    'Increase Body Rigidity': {'type': 'suspension', 'tier': 0.18},
    'New Body (Rigidity Refresh)': {'type': 'suspension', 'tier': 0.12},
    'Steering Angle Adapter': {'type': 'suspension', 'tier': 0.08},
    'Four-Wheel Steering Controller': {'type': 'suspension', 'tier': 0.28},

    # Brakes
    'Sports Brake Pads': {'type': 'brake', 'tier': 0.12},
    'Sports Brake Kit': {'type': 'brake', 'tier': 0.22},
    'Performance Brake Kit': {'type': 'brake', 'tier': 0.38},
    'Racing Brake Pads': {'type': 'brake', 'tier': 0.28},
    'Racing Brake Kit (Slotted Discs)': {'type': 'brake', 'tier': 0.32},
    'Racing Brake Kit (Drilled Discs)': {'type': 'brake', 'tier': 0.38},
    'Carbon Ceramic Brake Kit': {'type': 'brake', 'tier': 0.52},
    'Brake Balance Controller': {'type': 'brake', 'tier': 0.08},

    # Aero
    'Rear Diffuser': {'type': 'aero', 'tier': 0.12},
    'Carbon Fiber Rear Diffuser': {'type': 'aero', 'tier': 0.18},
    'Carbon Fiber Splitter': {'type': 'aero', 'tier': 0.22},
    'Adjustable GT Wing': {'type': 'aero', 'tier': 0.32},

    # Transmission
    'Sports Clutch & Flywheel': {'type': 'transmission', 'tier': 0.12},
    'Semi-Racing Clutch & Flywheel': {'type': 'transmission', 'tier': 0.22},
    'Racing Clutch & Flywheel': {'type': 'transmission', 'tier': 0.32},
    'Close-Ratio Transmission (Low)': {'type': 'transmission', 'accel_bias': 0.8, 'tier': 0.38},
    'Close-Ratio Transmission (High)': {'type': 'transmission', 'accel_bias': 0.5, 'tier': 0.32},
    'Fully Customizable Manual Transmission': {'type': 'transmission', 'tier': 0.48},
    'Fully Customizable Racing Transmission': {'type': 'transmission', 'tier': 0.62},

    # Drivetrain
    'One-Way LSD': {'type': 'drivetrain', 'tier': 0.18},
    'Two-Way LSD': {'type': 'drivetrain', 'tier': 0.28},
    'Fully Customizable LSD': {'type': 'drivetrain', 'tier': 0.38},
    'Active LSD Controller': {'type': 'drivetrain', 'tier': 0.22},
    'Carbon Propeller Shaft': {'type': 'drivetrain', 'tier': 0.18},
    'Torque-Vectoring Center Differential': {'type': 'drivetrain', 'tier': 0.28},

    # Tyres
    'Touring Tyres': {'type': 'tyre', 'tier': 0.0},
    'Performance Tyres': {'type': 'tyre', 'tier': 0.12},
    'Sports Medium Tyres': {'type': 'tyre', 'tier': 0.22},
    'High-Performance Tyres': {'type': 'tyre', 'tier': 0.32},
    'Semi-Slick Track Tyres': {'type': 'tyre', 'tier': 0.52},
    'Racing Slicks': {'type': 'tyre', 'tier': 0.72},
}


def compute_profile(laps):
    agg = laps.aggregate(
        avg_throttle=Avg('avg_throttle_pct'),
        avg_brake=Avg('avg_brake_pct'),
        avg_speed=Avg('avg_speed_kmh'),
        max_speed=Max('max_speed_kmh'),
        min_speed=Min('min_speed_kmh'),
        avg_lap_time=Avg('lap_time_ms'),
        best_lap_time=Min('lap_time_ms'),
    )
    if not agg['best_lap_time']:
        return None
    mx = agg['max_speed'] or 1
    mn = agg['min_speed'] or 1
    avg_s = agg['avg_speed'] or 1
    return {
        'avg_throttle_pct': (agg['avg_throttle'] or 50) / 100.0,
        'avg_brake_pct': (agg['avg_brake'] or 15) / 100.0,
        'avg_speed_kmh': avg_s,
        'max_speed_kmh': mx,
        'min_speed_kmh': mn,
        'speed_range': (mx - mn) / mx,
        'speed_ratio': avg_s / mx,
        'best_lap_time_ms': agg['best_lap_time'],
        'avg_lap_time_ms': agg['avg_lap_time'] or agg['best_lap_time'],
    }


def predict_impact(part_name, car, profile):
    mod = MOD_PROFILES.get(part_name)
    if not mod or not profile:
        return None

    mt = mod['type']
    tier = mod['tier']
    pt_w = car.power_hp / max(car.weight_kg, 1)
    lap_ms = profile['best_lap_time_ms']

    if mt == 'power':
        pf = profile['avg_throttle_pct'] * (1.0 / (1.0 + 0.7 * pt_w / 0.45))
        im_ms = 1.2 * tier * pf * 1000

    elif mt == 'forced_induction':
        ab = mod.get('accel_bias', 0.5)
        sb = 1.0 - ab
        accel_part = profile['avg_throttle_pct'] * (1.0 - profile['speed_ratio']) * ab
        top_part = profile['speed_ratio'] * sb
        pf = (accel_part + top_part) * (1.0 / (1.0 + 0.5 * pt_w / 0.45))
        im_ms = 1.5 * tier * pf * 1000

    elif mt == 'weight':
        wf = car.weight_kg / 1400.0
        im_ms = 0.9 * tier * wf * 1000

    elif mt == 'brake':
        bf = profile['avg_brake_pct'] * (car.weight_kg / 1400.0)
        im_ms = 0.5 * tier * bf * 1000

    elif mt == 'suspension':
        cf = 1.0 - profile['speed_ratio']
        im_ms = 0.7 * tier * cf * 1000

    elif mt == 'aero':
        af = profile['speed_ratio'] * profile['speed_range']
        im_ms = 0.45 * tier * af * 1000

    elif mt == 'transmission':
        im_ms = 0.45 * tier * 1000

    elif mt == 'drivetrain':
        im_ms = 0.35 * tier * (1.0 - profile['speed_ratio']) * 1000

    elif mt == 'tyre':
        im_ms = 1.6 * tier * (1.0 - profile['speed_ratio']) * 1000

    else:
        return None

    # sanity clamp: never predict more than 25% of lap time
    im_ms = max(im_ms, 0)
    im_ms = min(im_ms, lap_ms * 0.25)
    return max(round(im_ms) / 1000.0, 0.001)  # seconds, min 1ms

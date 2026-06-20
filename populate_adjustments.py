import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.models import CarPart, PartAdjustment

print("Populando dados de ajustes das pecas...")

# Clear existing
PartAdjustment.objects.all().delete()
CarPart.objects.all().update(is_adjustable=False)

ADJUSTMENTS = {
    # === FULLY CUSTOMIZABLE SUSPENSION ===
    "Fully Customizable Suspension": [
        ("ride_height_front",    "Ride Height F",     60,   130,  1,    95,   "mm"),
        ("ride_height_rear",     "Ride Height R",     60,   130,  1,    95,   "mm"),
        ("nat_freq_front",       "Natural Frequency F", 1.0, 7.0, 0.01, 3.0,  "Hz"),
        ("nat_freq_rear",        "Natural Frequency R", 1.0, 7.0, 0.01, 3.0,  "Hz"),
        ("anti_roll_front",      "Anti-Roll Bar F",    1,    10,   1,    4,    ""),
        ("anti_roll_rear",       "Anti-Roll Bar R",    1,    10,   1,    4,    ""),
        ("comp_damp_front",      "Compression Damp F", 1,    99,   1,    30,   ""),
        ("comp_damp_rear",       "Compression Damp R", 1,    99,   1,    30,   ""),
        ("exp_damp_front",       "Expansion Damp F",   1,    99,   1,    30,   ""),
        ("exp_damp_rear",        "Expansion Damp R",   1,    99,   1,    30,   ""),
        ("camber_front",         "Camber Angle F",     -5.0, 0.0,  0.01, -2.0, "deg"),
        ("camber_rear",          "Camber Angle R",     -5.0, 0.0,  0.01, -1.5, "deg"),
        ("toe_front",            "Toe Angle F",        -0.5, 0.5,  0.01, 0.0,  "deg"),
        ("toe_rear",             "Toe Angle R",        -0.5, 0.5,  0.01, 0.15, "deg"),
    ],

    # === HEIGHT-ADJUSTABLE SPORTS SUSPENSION ===
    "Height-Adjustable Sports Suspension": [
        ("ride_height_front",    "Ride Height F",     70,   120,  1,    95,   "mm"),
        ("ride_height_rear",     "Ride Height R",     70,   120,  1,    95,   "mm"),
        ("nat_freq_front",       "Natural Frequency F", 1.0, 5.0, 0.01, 2.5,  "Hz"),
        ("nat_freq_rear",        "Natural Frequency R", 1.0, 5.0, 0.01, 2.5,  "Hz"),
        ("comp_damp_front",      "Compression Damp F", 1,    60,   1,    25,   ""),
        ("comp_damp_rear",       "Compression Damp R", 1,    60,   1,    25,   ""),
        ("exp_damp_front",       "Expansion Damp F",   1,    60,   1,    25,   ""),
        ("exp_damp_rear",        "Expansion Damp R",   1,    60,   1,    25,   ""),
        ("camber_front",         "Camber Angle F",     -5.0, 0.0,  0.01, -2.0, "deg"),
        ("camber_rear",          "Camber Angle R",     -5.0, 0.0,  0.01, -1.5, "deg"),
    ],

    # === FULLY CUSTOMIZABLE LSD ===
    "Fully Customizable LSD": [
        ("initial_torque",       "Initial Torque",     5,    60,   1,    10,   ""),
        ("accel_sensitivity",    "Accel Sensitivity",  5,    60,   1,    30,   ""),
        ("brake_sensitivity",    "Brake Sensitivity",  5,    60,   1,    20,   ""),
    ],

    # === ACTIVE LSD CONTROLLER ===
    "Active LSD Controller": [
        ("initial_torque",       "Initial Torque",     5,    60,   1,    10,   ""),
        ("accel_sensitivity",    "Accel Sensitivity",  5,    60,   1,    30,   ""),
        ("brake_sensitivity",    "Brake Sensitivity",  5,    60,   1,    20,   ""),
    ],

    # === FULLY CUSTOMIZABLE MANUAL TRANSMISSION ===
    "Fully Customizable Manual Transmission": [
        ("final_gear",           "Final Gear",         2.0,  6.0,  0.001, 4.0,  ""),
        ("gear_1",               "Gear 1",             1.0,  5.0,  0.001, 3.0,  ""),
        ("gear_2",               "Gear 2",             1.0,  5.0,  0.001, 2.5,  ""),
        ("gear_3",               "Gear 3",             1.0,  5.0,  0.001, 2.0,  ""),
        ("gear_4",               "Gear 4",             1.0,  5.0,  0.001, 1.6,  ""),
        ("gear_5",               "Gear 5",             1.0,  5.0,  0.001, 1.3,  ""),
        ("gear_6",               "Gear 6",             1.0,  5.0,  0.001, 1.1,  ""),
    ],

    # === FULLY CUSTOMIZABLE RACING TRANSMISSION ===
    "Fully Customizable Racing Transmission": [
        ("final_gear",           "Final Gear",         2.0,  6.0,  0.001, 4.0,  ""),
        ("gear_1",               "Gear 1",             1.0,  5.0,  0.001, 3.0,  ""),
        ("gear_2",               "Gear 2",             1.0,  5.0,  0.001, 2.5,  ""),
        ("gear_3",               "Gear 3",             1.0,  5.0,  0.001, 2.0,  ""),
        ("gear_4",               "Gear 4",             1.0,  5.0,  0.001, 1.6,  ""),
        ("gear_5",               "Gear 5",             1.0,  5.0,  0.001, 1.3,  ""),
        ("gear_6",               "Gear 6",             1.0,  5.0,  0.001, 1.1,  ""),
    ],

    # === FULLY CUSTOMIZABLE COMPUTER (ECU) ===
    "Fully Customizable Computer": [
        ("power_output",         "Power Output",       50,   100,  1,    100,  "%"),
    ],

    # === POWER RESTRICTOR ===
    "Power Restrictor": [
        ("power_restriction",    "Power Restriction",    50,   100,  1,    100,  "%"),
    ],

    # === BALLAST ===
    "Ballast": [
        ("ballast_weight",       "Ballast Weight",     0,    200,  1,    0,    "kg"),
        ("ballast_position",     "Ballast Position",   -50,  50,   1,    0,    ""),
    ],

    # === BRAKE BALANCE CONTROLLER ===
    "Brake Balance Controller": [
        ("brake_balance",        "Brake Balance",      -5,   5,    1,    0,    ""),
    ],

    # === TORQUE-VECTORING CENTER DIFFERENTIAL ===
    "Torque-Vectoring Center Differential": [
        ("front_torque_split",   "Front Torque Split", 10,   90,   1,    50,   "%"),
    ],

    # === FOUR-WHEEL STEERING CONTROLLER ===
    "Four-Wheel Steering Controller": [
        ("steering_effect",      "Steering Effect",    1,    10,   1,    5,    ""),
    ],

    # === CUSTOM AERO PARTS ===
    "Adjustable GT Wing": [
        ("rear_downforce",       "Rear Downforce",     50,   500,  5,    200,  ""),
    ],

    "Carbon Fiber Splitter": [
        ("front_downforce",      "Front Downforce",    0,    300,  5,    100,  ""),
    ],
}

for part_name, params in ADJUSTMENTS.items():
    try:
        part = CarPart.objects.get(name=part_name)
    except CarPart.DoesNotExist:
        print(f"  [WARN] Part not found: '{part_name}' - skipping")
        continue

    part.is_adjustable = True
    part.save()

    for idx, (key, label, min_v, max_v, step, default, unit) in enumerate(params):
        PartAdjustment.objects.create(
            part=part,
            param_key=key,
            label=label,
            min_value=min_v,
            max_value=max_v,
            step=step,
            default_value=default,
            unit=unit,
            display_order=idx,
        )

    print(f"  [OK] {part_name}: {len(params)} adjustments")

print("Pronto! Pecas ajustaveis configuradas.")

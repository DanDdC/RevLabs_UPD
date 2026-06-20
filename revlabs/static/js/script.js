let installedMods = {};
let partAdjustmentsData = {};
let currentTuningPart = null;

// Keep this map synchronized with populateparts.py names.
const incompatibilityMap = {
    // Turbos — mutually exclusive with each other and with superchargers
    "Low-RPM Turbocharger": ["Medium-RPM Turbocharger", "High-RPM Turbocharger", "Ultra-High RPM Turbocharger", "Low-End Torque Supercharger", "High-End Torque Supercharger", "High-RPM S Supercharger"],
    "Medium-RPM Turbocharger": ["Low-RPM Turbocharger", "High-RPM Turbocharger", "Ultra-High RPM Turbocharger", "Low-End Torque Supercharger", "High-End Torque Supercharger", "High-RPM S Supercharger"],
    "High-RPM Turbocharger": ["Low-RPM Turbocharger", "Medium-RPM Turbocharger", "Ultra-High RPM Turbocharger", "Low-End Torque Supercharger", "High-End Torque Supercharger", "High-RPM S Supercharger"],
    "Ultra-High RPM Turbocharger": ["Low-RPM Turbocharger", "Medium-RPM Turbocharger", "High-RPM Turbocharger", "Low-End Torque Supercharger", "High-End Torque Supercharger", "High-RPM S Supercharger"],

    // Superchargers — mutually exclusive with each other and with turbos
    "Low-End Torque Supercharger": ["High-End Torque Supercharger", "High-RPM S Supercharger", "Low-RPM Turbocharger", "Medium-RPM Turbocharger", "High-RPM Turbocharger", "Ultra-High RPM Turbocharger"],
    "High-End Torque Supercharger": ["Low-End Torque Supercharger", "High-RPM S Supercharger", "Low-RPM Turbocharger", "Medium-RPM Turbocharger", "High-RPM Turbocharger", "Ultra-High RPM Turbocharger"],
    "High-RPM S Supercharger": ["Low-End Torque Supercharger", "High-End Torque Supercharger", "Low-RPM Turbocharger", "Medium-RPM Turbocharger", "High-RPM Turbocharger", "Ultra-High RPM Turbocharger"],

    // Suspension — only one type at a time
    "Street Suspension": ["Sports Suspension", "Height-Adjustable Sports Suspension", "Fully Customizable Suspension"],
    "Sports Suspension": ["Street Suspension", "Height-Adjustable Sports Suspension", "Fully Customizable Suspension"],
    "Height-Adjustable Sports Suspension": ["Street Suspension", "Sports Suspension", "Fully Customizable Suspension"],
    "Fully Customizable Suspension": ["Street Suspension", "Sports Suspension", "Height-Adjustable Sports Suspension"],

    // Brake kits — only one set
    "Sports Brake Kit": ["Performance Brake Kit", "Racing Brake Kit (Slotted Discs)", "Racing Brake Kit (Drilled Discs)", "Carbon Ceramic Brake Kit"],
    "Performance Brake Kit": ["Sports Brake Kit", "Racing Brake Kit (Slotted Discs)", "Racing Brake Kit (Drilled Discs)", "Carbon Ceramic Brake Kit"],
    "Racing Brake Kit (Slotted Discs)": ["Sports Brake Kit", "Performance Brake Kit", "Racing Brake Kit (Drilled Discs)", "Carbon Ceramic Brake Kit"],
    "Racing Brake Kit (Drilled Discs)": ["Sports Brake Kit", "Performance Brake Kit", "Racing Brake Kit (Slotted Discs)", "Carbon Ceramic Brake Kit"],
    "Carbon Ceramic Brake Kit": ["Sports Brake Kit", "Performance Brake Kit", "Racing Brake Kit (Slotted Discs)", "Racing Brake Kit (Drilled Discs)"],

    // Clutch — only one
    "Sports Clutch & Flywheel": ["Semi-Racing Clutch & Flywheel", "Racing Clutch & Flywheel"],
    "Semi-Racing Clutch & Flywheel": ["Sports Clutch & Flywheel", "Racing Clutch & Flywheel"],
    "Racing Clutch & Flywheel": ["Sports Clutch & Flywheel", "Semi-Racing Clutch & Flywheel"],

    // LSD — only one
    "One-Way LSD": ["Two-Way LSD", "Fully Customizable LSD", "Active LSD Controller"],
    "Two-Way LSD": ["One-Way LSD", "Fully Customizable LSD", "Active LSD Controller"],
    "Fully Customizable LSD": ["One-Way LSD", "Two-Way LSD", "Active LSD Controller"],
    "Active LSD Controller": ["One-Way LSD", "Two-Way LSD", "Fully Customizable LSD"],

    // Transmission
    "Close-Ratio Transmission (Low)": ["Close-Ratio Transmission (High)", "Fully Customizable Manual Transmission", "Fully Customizable Racing Transmission"],
    "Close-Ratio Transmission (High)": ["Close-Ratio Transmission (Low)", "Fully Customizable Manual Transmission", "Fully Customizable Racing Transmission"],
    "Fully Customizable Manual Transmission": ["Close-Ratio Transmission (Low)", "Close-Ratio Transmission (High)", "Fully Customizable Racing Transmission"],
    "Fully Customizable Racing Transmission": ["Close-Ratio Transmission (Low)", "Close-Ratio Transmission (High)", "Fully Customizable Manual Transmission"],

    // Weight reduction — cumulative, not mutually exclusive, but only one of each stage
    // Actually stages can stack; no conflicts needed

    // ECU — conflicts between fixed and custom
    "Sports Computer": ["Fully Customizable Computer"],
    "Fully Customizable Computer": ["Sports Computer"],

    // Intercooler — only one
    "Sports Intercooler": ["Racing Intercooler"],
    "Racing Intercooler": ["Sports Intercooler"],

    // Air filter
    "Sports Air Filter": ["Racing Air Filter"],
    "Racing Air Filter": ["Sports Air Filter"],

    // Exhaust
    "Sports Muffler": ["Semi-Racing Muffler", "Racing Muffler"],
    "Semi-Racing Muffler": ["Sports Muffler", "Racing Muffler"],
    "Racing Muffler": ["Sports Muffler", "Semi-Racing Muffler"],
};

// ==========================================================================
// 1. VEHICLE DYNAMICS BASE STATS
// ==========================================================================
// cda: Cd * frontal area. Higher = more drag.
// cla: downforce coefficient * reference area. Higher = more aero load.
// mu: tyre/mechanical grip baseline.
// brake_eff: hydraulic/thermal brake capability. Keep near 1.0; tyres still cap braking.
// drivetrain_loss: parasitic drivetrain loss.
// traction: how much longitudinal grip the car can use under power.
//
// These are calibrated game/simulation coefficients, not manufacturer data.
const BASE_CAR_STATS = {
    // chassis_flex expresses how much the platform benefits from rigidity/bracing mods.
    // Old, flexible road shells benefit more; modern track-focused cars benefit very little.
    'vw-fusca':     { cda: 0.85, cla: 0.00, mu: 0.84, brake_eff: 0.78, drivetrain_loss: 0.16, traction: 0.55, chassis_flex: 0.95 },

    // Ferrari is calibrated as a 2009 road supercar on high-performance road tyres.
    // It has strong power/top speed, but far less aero and transient stability than the newer track specials.
    'ferrari-458':  { cda: 0.68, cla: 0.10, mu: 1.08, brake_eff: 0.90, drivetrain_loss: 0.12, traction: 0.60, chassis_flex: 0.30 },

    // Modern track-focused road cars. Their factory tyres are handled by DEFAULT_TYRE_BY_CAR.
    'porsche-911':  { cda: 0.78, cla: 0.70, mu: 1.34, brake_eff: 1.02, drivetrain_loss: 0.10, traction: 0.72, chassis_flex: 0.12 },
    'mercedes-amg': { cda: 0.78, cla: 0.50, mu: 1.30, brake_eff: 0.97, drivetrain_loss: 0.12, traction: 0.68, chassis_flex: 0.16 }
};

// Database/url compatibility aliases. The simulator normalizes every car slug before lookup.
const CAR_SLUG_ALIASES = {
    'porsche': 'porsche-911',
    'porsche-911': 'porsche-911',
    'ferrari': 'ferrari-458',
    'ferrari-458': 'ferrari-458',
    'mercedes': 'mercedes-amg',
    'amg': 'mercedes-amg',
    'mercedes-amg': 'mercedes-amg',
    'fusca': 'vw-fusca',
    'vw-fusca': 'vw-fusca',
    'fusca': 'vw-fusca',
    'vw-fusca': 'vw-fusca'
};

function normalizeCarSlug(slug) {
    return CAR_SLUG_ALIASES[slug] || slug;
}

// Every car now starts with a tyre that represents its calibrated factory/reference condition.
// The baseline lap time therefore means: stock car + this factory/default tyre.
const DEFAULT_TYRE_BY_CAR = {
    'vw-fusca': 'Touring Tyres',

    'ferrari-458': 'High-Performance Tyres',
    'porsche-911': 'Sports Medium Tyres',
    'mercedes-amg': 'Semi-Slick Track Tyres'
};

// Tyre effects are relative classes, not raw lap-time buffs.
// Since BASE_CAR_STATS.mu is already calibrated with each car's default tyre,
// changing tyre applies only the delta from the default tyre to the selected tyre.
const TYRE_CLASS_EFFECTS = {
    'Touring Tyres': { mu: 0.000, traction: 0.000, cda: 0.000 },
    'Performance Tyres': { mu: 0.055, traction: 0.018, cda: 0.000 },
    'Sports Medium Tyres': { mu: 0.080, traction: 0.022, cda: 0.000 },
    'High-Performance Tyres': { mu: 0.105, traction: 0.028, cda: 0.000 },
    'Semi-Slick Track Tyres': { mu: 0.165, traction: 0.040, cda: 0.002 },
    'Racing Slicks': { mu: 0.275, traction: 0.055, cda: 0.006 }
};

// Same weight values used in populateparts.py. This lets the reference stock solver
// reproduce the same factory tyre mass contribution even when the user has installed another tyre.
const TYRE_CATALOG_WEIGHTS = {
    'Touring Tyres': 0,
    'Performance Tyres': -1,
    'Sports Medium Tyres': -2,
    'High-Performance Tyres': -2,
    'Semi-Slick Track Tyres': -4,
    'Racing Slicks': -6
};

// Hybrid calibration layer:
// 1) the physics solver computes how a setup changes performance;
// 2) the stock result is anchored to a reference lap gathered from official/track-test/sim-racing data;
// 3) upgrades use the solver ratio relative to that stock baseline.
// This avoids fake per-upgrade lap-time buffs while keeping stock cars close to real/sim reference pace.
const REFERENCE_STOCK_LAP_SECONDS = {
    'porsche-911': {
        // Official/track-test/sim blend: 6:49.328 Nordschleife, 1:55.3 Monza,
        // 2:08.34 Silverstone GP, 2:29.23 Spa, and TrackTitan-style Suzuka reference.
        nurburgring: 409.328,
        monza: 115.300,
        silverstone: 128.340,
        spa: 149.230,
        suzuka: 132.859,
        interlagos: 100.500
    },
    'mercedes-amg': {
        // Anchored to the official 20.832 km Nürburgring record and scaled against the GT3 RS elsewhere.
        nurburgring: 408.047,
        monza: 113.900,
        silverstone: 128.000,
        spa: 148.900,
        suzuka: 132.000,
        interlagos: 99.800
    },
    'ferrari-458': {
        // Older supercar reference: Nürburgring real-world lap plus Assetto Corsa/TrackTitan ranges.
        nurburgring: 452.900,
        monza: 120.600,
        silverstone: 137.500,
        spa: 158.000,
        suzuka: 141.000,
        interlagos: 109.000
    },
    'vw-fusca': {
        // Low-confidence class: anchored to a Gran Turismo sanity check around Interlagos.
        // Stock Fusca + Touring Tyres should sit around 2:56 at Interlagos, not 2:32.
        nurburgring: 746.000,
        monza: 217.000,
        silverstone: 226.000,
        spa: 274.000,
        suzuka: 236.000,
        interlagos: 176.000
    }
};

function getCurrentTyreName(mods = installedMods) {
    return Object.keys(mods).find(key => mods[key].mainCat === 'tyres') || null;
}

function getDefaultTyreForCar(carSlug) {
    return DEFAULT_TYRE_BY_CAR[normalizeCarSlug(carSlug)] || null;
}

// ==========================================================================
// 2. MOD PHYSICS MAPPING
// ==========================================================================
// Mods should change vehicle attributes, not lap time directly.
// All names below are synchronized with populateparts.py.
const MOD_PHYSICS_MAP = {
    // Engine internals / intake / ECU
    "Forged Aluminum Pistons": { inertia: -0.010, powerband: +0.006 },
    "Bore Up": { inertia: +0.010, powerband: +0.010 },
    "Stroke Up": { inertia: +0.015, powerband: +0.015 },
    "Bore Up S": { inertia: +0.012, powerband: +0.012 },
    "Stroke Up S": { inertia: +0.018, powerband: +0.018 },
    "Engine Balance Tuning": { inertia: -0.015, powerband: +0.014 },
    "High Compression Pistons": { powerband: +0.018 },
    "Polish Parts": { inertia: -0.008, powerband: +0.008 },
    "Titanium Connecting Rods & Pistons": { inertia: -0.025, powerband: +0.022 },
    "High Lift Camshaft": { powerband: +0.015, inertia: +0.005 },
    "High Lift Camshaft S": { powerband: +0.022, inertia: +0.008 },
    "Racing Crankshaft": { inertia: -0.012, powerband: +0.012 },
    "New Engine": { powerband: +0.035, inertia: -0.010 },
    "Sports Computer": { powerband: +0.010 },
    "Fully Customizable Computer": { powerband: +0.020 },
    "Sports Air Filter": { powerband: +0.004 },
    "Racing Air Filter": { powerband: +0.008 },

    // Exhaust
    "Sports Muffler": { powerband: +0.008, inertia: -0.005 },
    "Semi-Racing Muffler": { powerband: +0.014, inertia: -0.008 },
    "Racing Muffler": { powerband: +0.018, inertia: -0.010 },
    "Racing Exhaust Manifold": { powerband: +0.010, inertia: -0.006 },

    // Intercooler
    "Sports Intercooler": { powerband: +0.004 },
    "Racing Intercooler": { powerband: +0.008 },

    // Forced induction
    "Low-RPM Turbocharger": { powerband: +0.020, acceleration_bias: +0.010, inertia: +0.012 },
    "Medium-RPM Turbocharger": { powerband: +0.028, acceleration_bias: +0.006, inertia: +0.018 },
    "High-RPM Turbocharger": { powerband: +0.030, acceleration_bias: -0.004, top_speed_bias: +0.010, inertia: +0.024 },
    "Ultra-High RPM Turbocharger": { powerband: +0.035, acceleration_bias: -0.008, top_speed_bias: +0.014, inertia: +0.030 },
    "Low-End Torque Supercharger": { powerband: +0.026, acceleration_bias: +0.012, drivetrain_loss: +0.010, inertia: +0.018 },
    "High-End Torque Supercharger": { powerband: +0.034, acceleration_bias: +0.014, drivetrain_loss: +0.015, inertia: +0.024 },
    "High-RPM S Supercharger": { powerband: +0.038, acceleration_bias: +0.016, drivetrain_loss: +0.018, inertia: +0.028 },

    // Anti-Lag
    "Anti-Lag System": { powerband: +0.012, inertia: +0.005 },

    // Nitro
    "Nitro System": { powerband: +0.040 },

    // Transmission
    "Sports Clutch & Flywheel": { inertia: -0.012, shift_loss: -0.008 },
    "Semi-Racing Clutch & Flywheel": { inertia: -0.016, shift_loss: -0.012 },
    "Racing Clutch & Flywheel": { inertia: -0.022, shift_loss: -0.016 },
    "Close-Ratio Transmission (Low)": { acceleration_bias: +0.030, top_speed_bias: -0.030, shift_loss: -0.008 },
    "Close-Ratio Transmission (High)": { acceleration_bias: +0.014, top_speed_bias: +0.006, shift_loss: -0.008 },
    "Fully Customizable Manual Transmission": { drivetrain_loss: -0.015, shift_loss: -0.018, acceleration_bias: +0.010 },
    "Fully Customizable Racing Transmission": { drivetrain_loss: -0.025, shift_loss: -0.026, acceleration_bias: +0.015 },

    // Drivetrain
    "One-Way LSD": { traction: +0.026, stability: +0.006 },
    "Two-Way LSD": { traction: +0.038, stability: +0.010 },
    "Fully Customizable LSD": { traction: +0.042, stability: +0.014 },
    "Active LSD Controller": { traction: +0.030, stability: +0.018 },
    "Carbon Propeller Shaft": { drivetrain_loss: -0.010, inertia: -0.014 },
    "Torque-Vectoring Center Differential": { traction: +0.020, stability: +0.010 },

    // Brakes
    "Sports Brake Pads": { brake_eff: +0.015 },
    "Sports Brake Kit": { brake_eff: +0.026 },
    "Performance Brake Kit": { brake_eff: +0.055 },
    "Racing Brake Pads": { brake_eff: +0.035 },
    "Racing Brake Kit (Slotted Discs)": { brake_eff: +0.040 },
    "Racing Brake Kit (Drilled Discs)": { brake_eff: +0.050, inertia: -0.005 },
    "Carbon Ceramic Brake Kit": { brake_eff: +0.075, inertia: -0.010 },
    "Brake Balance Controller": { brake_eff: +0.010 },

    // Suspension / chassis setup
    "Street Suspension": { mu: +0.008, stability: +0.006 },
    "Sports Suspension": { mu: +0.015, stability: +0.012 },
    "Height-Adjustable Sports Suspension": { mu: +0.022, stability: +0.016 },
    "Fully Customizable Suspension": { mu: +0.032, stability: +0.024 },
    "Stiffened Anti-roll Bars": { mu: +0.010, stability: +0.020 },

    // Chassis reinforcement
    "Increase Body Rigidity": { rigidity: +0.045, stability: +0.004 },
    "New Body (Rigidity Refresh)": { rigidity: +0.035, stability: +0.006 },

    // Steering
    "Steering Angle Adapter": { stability: +0.005 },
    "Four-Wheel Steering Controller": { stability: +0.015 },

    // Aerodynamics
    "Rear Diffuser": { cla: +0.060, cda: -0.004, stability: +0.004 },
    "Carbon Fiber Rear Diffuser": { cla: +0.095, cda: -0.009, stability: +0.006 },
    "Carbon Fiber Splitter": { cla: +0.115, cda: +0.018, stability: +0.008 },
    "Adjustable GT Wing": { cla: +0.180, cda: +0.040, stability: +0.012 },

    // Weight reduction
    "Stage 1 Weight Reduction": { stability: -0.002 },
    "Stage 2 Weight Reduction": { stability: -0.003 },
    "Stage 3 Weight Reduction": { stability: -0.005 },
    "Stage 4 Weight Reduction": { stability: -0.007 },
    "Stage 5 Weight Reduction": { stability: -0.009 },
    "Stage 6 Weight Reduction": { stability: -0.012 },

    // Tyres are handled by TYRE_CLASS_EFFECTS using relative deltas from the car's factory tyre.
};

// ==========================================================================
// 2b. ADJUSTMENT PHYSICS MAP (tuning sliders)
// ==========================================================================

function applyTuningEffects(dyn, partName, tuningValues) {
    if (!tuningValues) return;
    const adjDefs = partAdjustmentsData[partName];
    if (!adjDefs) return;

    const defaults = {};
    adjDefs.forEach(a => { defaults[a.key] = a.default; });

    for (const key in tuningValues) {
        const val = tuningValues[key];
        const def = defaults[key];
        if (def === undefined) continue;

        switch (key) {
            // Ride height
            case 'ride_height_front': {
                const ratio = (val - def) / Math.max(def, 1);
                dyn.cda += ratio * 0.02;
                dyn.stability += -ratio * 0.005;
                break;
            }
            case 'ride_height_rear': {
                const ratio = (val - def) / Math.max(def, 1);
                dyn.stability += -ratio * 0.005;
                break;
            }
            // Spring rate
            case 'nat_freq_front': dyn.mu += (val - def) * 0.002; break;
            case 'nat_freq_rear':  dyn.mu += (val - def) * 0.002; break;
            // Anti-roll
            case 'anti_roll_front': dyn.stability += (val - def) * 0.002; break;
            case 'anti_roll_rear':  dyn.stability += (val - def) * (-0.002); break;
            // Damping
            case 'comp_damp_front':
            case 'comp_damp_rear':
            case 'exp_damp_front':
            case 'exp_damp_rear':
                dyn.stability += (val - def) * 0.0005;
                break;
            // Camber
            case 'camber_front': dyn.mu += (val - def) * 0.003; break;
            case 'camber_rear':  dyn.mu += (val - def) * 0.003; break;
            // Toe
            case 'toe_front':
                dyn.stability += (val - def) * 0.01;
                break;
            case 'toe_rear':
                dyn.stability += (val - def) * 0.01;
                dyn.traction += (val - def) * 0.005;
                break;
            // LSD
            case 'initial_torque':
                dyn.traction += (val - def) * 0.0005;
                dyn.stability += (val - def) * 0.0003;
                break;
            case 'accel_sensitivity':
                dyn.traction += (val - def) * 0.0003;
                break;
            case 'brake_sensitivity':
                dyn.stability += (val - def) * 0.0003;
                break;
            // Transmission
            case 'final_gear':
                dyn.acceleration_bias += (val - def) * 0.005;
                dyn.top_speed_bias += (val - def) * (-0.003);
                break;
            case 'gear_1': case 'gear_2': case 'gear_3':
                dyn.acceleration_bias += (val - def) * 0.002;
                break;
            case 'gear_4':
                dyn.acceleration_bias += (val - def) * 0.001;
                dyn.top_speed_bias += (val - def) * (-0.001);
                break;
            case 'gear_5':
            case 'gear_6':
                dyn.top_speed_bias += (val - def) * (-0.003);
                break;
            // Power
            case 'power_output':
            case 'power_restriction':
                // Applied in applyInstalledMods via power_pct
                dyn.power_pct = val / 100;
                break;
            // Ballast
            case 'ballast_weight':
                dyn.extra_weight = (dyn.extra_weight || 0) + (val - def);
                dyn.stability += (val - def) * (-0.001);
                break;
            case 'ballast_position':
                dyn.stability += (val - def) * 0.001;
                break;
            // Brake
            case 'brake_balance':
                dyn.brake_eff += (val - def) * 0.005;
                break;
            // Aero
            case 'rear_downforce':
                dyn.cla += (val - def) * 0.0005;
                dyn.cda += (val - def) * 0.0002;
                break;
            case 'front_downforce':
                dyn.cla += (val - def) * 0.0005;
                dyn.cda += (val - def) * 0.0002;
                break;
            // Center diff
            case 'front_torque_split':
                dyn.traction += (val - def) * 0.001;
                break;
            // 4WS
            case 'steering_effect':
                dyn.stability += (val - def) * 0.002;
                break;
        }
    }
}

// ==========================================================================
// 3. TRACK GEOMETRY
// ==========================================================================
// radius 0 = straight. radius > 0 = approximated corner radius in meters.
// These are not exact GPS traces; they are calibrated macro-segments.
const TRACKS = {
    'monza': [
        { length: 1100, radius: 0 }, { length: 150, radius: 52 },   // Rettifilo + Variante del Rettifilo
        { length: 600,  radius: 0 }, { length: 250, radius: 231 },  // Curva Grande
        { length: 700,  radius: 0 }, { length: 140, radius: 52 },   // Variante della Roggia
        { length: 300,  radius: 0 }, { length: 250, radius: 102 },  // Lesmo section
        { length: 850,  radius: 0 }, { length: 260, radius: 111 },  // Ascari
        { length: 900,  radius: 0 }, { length: 293, radius: 142 }   // Parabolica / Alboreto
    ],

    'interlagos': [
        { length: 800,  radius: 0 }, { length: 200, radius: 55 },
        { length: 600,  radius: 0 }, { length: 300, radius: 105 },
        { length: 200,  radius: 0 }, { length: 800, radius: 65 },
        { length: 200,  radius: 0 }, { length: 200, radius: 75 },
        { length: 1000, radius: 0 }
    ],

    'silverstone': [
        { length: 500, radius: 0 }, { length: 200, radius: 130 },
        { length: 600, radius: 0 }, { length: 300, radius: 65 },
        { length: 800, radius: 0 }, { length: 600, radius: 210 },  // Maggots/Becketts approximation
        { length: 800, radius: 0 }, { length: 300, radius: 115 },
        { length: 500, radius: 0 }, { length: 300, radius: 75 },
        { length: 400, radius: 0 }, { length: 400, radius: 70 }
    ],

    'spa': [
        { length: 300,  radius: 0 }, { length: 100, radius: 45 },
        { length: 200,  radius: 0 }, { length: 500, radius: 240 },
        { length: 1500, radius: 0 }, { length: 300, radius: 90 },
        { length: 200,  radius: 0 }, { length: 400, radius: 95 },
        { length: 200,  radius: 0 }, { length: 400, radius: 110 },
        { length: 800,  radius: 0 }, { length: 500, radius: 210 },
        { length: 1000, radius: 0 }, { length: 200, radius: 48 }
    ],

    'suzuka': [
        { length: 400, radius: 0 }, { length: 230, radius: 90 },
        { length: 220, radius: 105 }, { length: 260, radius: 120 },
        { length: 260, radius: 160 }, { length: 180, radius: 75 },
        { length: 600, radius: 0 }, { length: 130, radius: 45 },
        { length: 780, radius: 0 }, { length: 380, radius: 110 },
        { length: 900, radius: 0 }, { length: 330, radius: 190 },
        { length: 350, radius: 0 }, { length: 150, radius: 55 },
        { length: 637, radius: 0 }
    ]
};

function generateNordschleife() {
    const segs = [];

    // Nordschleife is long and flowing, not 13 repeated hairpin complexes.
    // This generator preserves ~20.832 km while reducing artificial momentum-killing sections.
    for (let i = 0; i < 13; i++) {
        segs.push({ length: 350, radius: 0 });    // acceleration zone
        segs.push({ length: 250, radius: 220 });  // fast sweeper
        segs.push({ length: 200, radius: 0 });
        segs.push({ length: 200, radius: 120 });  // medium technical bend
        segs.push({ length: 150, radius: 80 });   // slower technical bend, not a repeated hairpin
        segs.push({ length: 250, radius: 0 });
    }

    segs.push({ length: 2200, radius: 0 });       // Döttinger Höhe approximation
    segs.push({ length: 432, radius: 120 });      // Tiergarten / Hohenrain approximation
    return segs;
}
TRACKS['nurburgring'] = generateNordschleife();

// ==========================================================================
// 4. UI AND MODAL EVENT LISTENERS
// ==========================================================================

function equipDefaultTyreFromCatalog(parts) {
    const timeDisplay = document.getElementById('lap-time-display');
    if (!timeDisplay) return;

    const context = getSimulationContext(timeDisplay);
    const defaultTyreName = getDefaultTyreForCar(context.carSlug);
    if (!defaultTyreName || getCurrentTyreName()) return;

    const tyrePart = Array.from(parts).find(part => part.getAttribute('data-name') === defaultTyreName);
    if (!tyrePart) return;

    installedMods[defaultTyreName] = {
        hp: parseFloat(tyrePart.getAttribute('data-hp')) || 0,
        weight: parseFloat(tyrePart.getAttribute('data-weight')) || 0,
        img: tyrePart.getAttribute('data-img'),
        mainCat: 'tyres',
        factoryDefault: true
    };
}

function showSystemModal(title, message, isConfirm, callback) {
    const modal = document.getElementById('system-modal');
    if (!modal) return;

    document.getElementById('system-dialog-title').innerText = title;
    document.getElementById('system-dialog-message').innerText = message;
    const actionsContainer = document.getElementById('system-dialog-actions');
    actionsContainer.innerHTML = '';

    if (isConfirm) {
        const btnCancel = document.createElement('button');
        btnCancel.className = 'btn-system cancel';
        btnCancel.innerText = 'CANCEL';
        btnCancel.onclick = () => { modal.close(); if (callback) callback(false); };

        const btnConfirm = document.createElement('button');
        btnConfirm.className = 'btn-system confirm';
        btnConfirm.innerText = 'CONFIRM';
        btnConfirm.onclick = () => { modal.close(); if (callback) callback(true); };

        actionsContainer.appendChild(btnCancel);
        actionsContainer.appendChild(btnConfirm);
    } else {
        const btnOk = document.createElement('button');
        btnOk.className = 'btn-system confirm';
        btnOk.innerText = 'OK';
        btnOk.onclick = () => { modal.close(); };
        actionsContainer.appendChild(btnOk);
    }
    modal.showModal();
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('mod-modal');
    const addModBtn = document.getElementById('add-mod-btn');
    const mainCategories = document.querySelectorAll('#main-category-list li');
    const subCategories = document.querySelectorAll('#category-list li');
    const parts = document.querySelectorAll('.part-item');

    if (addModBtn && modal) {
        addModBtn.addEventListener('click', () => {
            modal.style.margin = 'auto';
            modal.style.right = '0';
            modal.style.bottom = '0';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.transform = 'none';
            modal.showModal();
            const defaultTab = document.querySelector('[data-target-main="engine"]');
            if (defaultTab) defaultTab.click();
        });
    }

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.close();
        });
    }

    mainCategories.forEach(mainLi => {
        mainLi.addEventListener('click', () => {
            mainCategories.forEach(li => li.classList.remove('active-main'));
            mainLi.classList.add('active-main');
            const targetMain = mainLi.getAttribute('data-target-main');
            subCategories.forEach(subLi => {
                subLi.style.display = (subLi.getAttribute('data-main-cat') === targetMain) ? 'block' : 'none';
                subLi.classList.remove('active-category');
            });
            parts.forEach(part => part.style.display = 'none');
        });
    });

    subCategories.forEach(subLi => {
        subLi.addEventListener('click', () => {
            subCategories.forEach(li => li.classList.remove('active-category'));
            subLi.classList.add('active-category');
            const targetCat = subLi.getAttribute('data-target');
            parts.forEach(part => {
                part.style.display = part.classList.contains(targetCat) ? 'flex' : 'none';
            });
        });
    });

    function installPart(partName, hp, weight, img, mainCat) {
        const conflicts = incompatibilityMap[partName] || [];
        for (const conflictMod of conflicts) {
            if (installedMods[conflictMod]) {
                showSystemModal("INCOMPATIBILITY DETECTED", `${partName} cannot be installed alongside ${conflictMod}.`, false);
                return;
            }
        }

        installedMods[partName] = { hp, weight, img, mainCat, factoryDefault: false };
        renderInstalledMods();
        if (modal) modal.close();
    }

    parts.forEach(part => {
        part.addEventListener('click', () => {
            const partName = part.getAttribute('data-name');
            const addedHp = parseFloat(part.getAttribute('data-hp')) || 0;
            const addedWeight = parseFloat(part.getAttribute('data-weight')) || 0;
            const imagePath = part.getAttribute('data-img');
            const activeSubLi = document.querySelector('#category-list li.active-category');
            const mainCat = activeSubLi ? activeSubLi.getAttribute('data-main-cat') : '';

            if (installedMods[partName]) {
                showSystemModal("ITEM ALREADY FITTED", `The component "${partName}" is already installed.`, false);
                return;
            }

            if (mainCat === 'tyres') {
                const existingTyre = Object.keys(installedMods).find(key => installedMods[key].mainCat === 'tyres');
                if (existingTyre) {
                    showSystemModal("TYRE CHANGE", `Vehicle is currently fitted with ${existingTyre}. Proceed with mounting ${partName}?`, true, (agreed) => {
                        if (agreed) {
                            delete installedMods[existingTyre];
                            installPart(partName, addedHp, addedWeight, imagePath, mainCat);
                        }
                    });
                    return;
                }
            }
            installPart(partName, addedHp, addedWeight, imagePath, mainCat);
        });
    });

    // View Laps button
    const btnViewLaps = document.getElementById('btn-view-laps');
    if (btnViewLaps) {
        btnViewLaps.addEventListener('click', () => {
            const timeDisplay = document.getElementById('lap-time-display');
            if (!timeDisplay) return;

            let lapsData = [];
            try {
                lapsData = JSON.parse(timeDisplay.dataset.telemetryLaps || '[]');
            } catch (e) {}

            const tbody = document.getElementById('laps-table-body');
            if (!tbody) return;

            // Find best sectors
            const lapsWithSectors = lapsData.filter(l => l.sector_1_ms && l.sector_2_ms && l.sector_3_ms);
            let bestS1 = null, bestS2 = null, bestS3 = null;
            if (lapsWithSectors.length > 0) {
                bestS1 = Math.min(...lapsWithSectors.map(l => l.sector_1_ms));
                bestS2 = Math.min(...lapsWithSectors.map(l => l.sector_2_ms));
                bestS3 = Math.min(...lapsWithSectors.map(l => l.sector_3_ms));
            }

            function msToTime(ms) {
                if (!ms || ms <= 0) return '--';
                const sec = ms / 1000;
                const m = Math.floor(sec / 60);
                const s = (sec % 60).toFixed(3);
                return `${m}:${+s < 10 ? '0' : ''}${s}`;
            }

            tbody.innerHTML = lapsData.length === 0
                ? '<tr><td colspan="8" class="no-data">No telemetry data available</td></tr>'
                : lapsData.map((lap, idx) => {
                    const hasSectors = lap.sector_1_ms && lap.sector_2_ms && lap.sector_3_ms;
                    const s1Best = hasSectors && bestS1 !== null && lap.sector_1_ms === bestS1;
                    const s2Best = hasSectors && bestS2 !== null && lap.sector_2_ms === bestS2;
                    const s3Best = hasSectors && bestS3 !== null && lap.sector_3_ms === bestS3;
                    const rowClass = s1Best || s2Best || s3Best ? 'has-best-sector' : '';
                    return `<tr class="${rowClass}">
                        <td>${idx + 1}</td>
                        <td>${lap.lap_number}</td>
                        <td class="lap-time-cell">${secondsToTime(lap.lap_time_seconds)}</td>
                        <td class="${s1Best ? 'best-sector-cell' : ''}">${msToTime(lap.sector_1_ms)}</td>
                        <td class="${s2Best ? 'best-sector-cell' : ''}">${msToTime(lap.sector_2_ms)}</td>
                        <td class="${s3Best ? 'best-sector-cell' : ''}">${msToTime(lap.sector_3_ms)}</td>
                        <td>${lap.max_speed_kmh ? lap.max_speed_kmh.toFixed(1) + ' km/h' : '--'}</td>
                        <td>${lap.avg_speed_kmh ? lap.avg_speed_kmh.toFixed(1) + ' km/h' : '--'}</td>
                    </tr>`;
                }).join('');

            // Populate projected footer row
            if (lapsWithSectors.length > 0) {
                const projectedMs = bestS1 + bestS2 + bestS3;
                document.getElementById('best-s1-cell').textContent = msToTime(bestS1);
                document.getElementById('best-s2-cell').textContent = msToTime(bestS2);
                document.getElementById('best-s3-cell').textContent = msToTime(bestS3);
                const projectedRow = document.getElementById('projected-row');
                const projectedTimeCell = projectedRow.querySelector('.lap-time-cell');
                projectedTimeCell.textContent = msToTime(projectedMs);
                projectedTimeCell.classList.add('projected-time');
            } else {
                document.getElementById('best-s1-cell').textContent = '--';
                document.getElementById('best-s2-cell').textContent = '--';
                document.getElementById('best-s3-cell').textContent = '--';
            }

            document.getElementById('laps-modal').showModal();
        });
    }

    // Close laps modal on backdrop click
    const lapsModal = document.getElementById('laps-modal');
    if (lapsModal) {
        lapsModal.addEventListener('click', (e) => {
            if (e.target === lapsModal) lapsModal.close();
        });
    }

    // Import Telemetry from TelemetryIQ database
    const btnImport = document.getElementById('btn-import-telemetry');
    if (btnImport) {
        btnImport.addEventListener('click', async () => {
            btnImport.disabled = true;
            btnImport.textContent = 'IMPORTING...';
            try {
                const resp = await fetch('/api/import-telemetry/');
                const data = await resp.json();
                if (data.status === 'ok') {
                    showSystemModal('TELEMETRY IMPORT', `Imported ${data.imported} laps. ${data.skipped} skipped. ${data.trimmed} trimmed.`, false);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showSystemModal('IMPORT ERROR', data.message || 'Unknown error');
                }
            } catch (e) {
                showSystemModal('IMPORT ERROR', e.message);
            } finally {
                btnImport.disabled = false;
                btnImport.textContent = 'IMPORT TELEMETRY';
            }
        });
    }

    // Import Telemetry from uploaded file
    const btnImportFile = document.getElementById('btn-import-from-file');
    const fileInput = document.getElementById('import-file-input');
    if (btnImportFile && fileInput) {
        btnImportFile.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async () => {
            const file = fileInput.files[0];
            if (!file) return;
            btnImportFile.disabled = true;
            btnImportFile.textContent = 'IMPORTING...';
            try {
                const formData = new FormData();
                formData.append('file', file);
                const resp = await fetch('/api/import-telemetry/', { method: 'POST', body: formData });
                const data = await resp.json();
                if (data.status === 'ok') {
                    showSystemModal('IMPORT COMPLETE', `Imported ${data.imported} laps from ${file.name}. ${data.skipped} skipped. ${data.trimmed} trimmed.`, false);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showSystemModal('IMPORT ERROR', data.message || 'Unknown error');
                }
            } catch (e) {
                showSystemModal('IMPORT ERROR', e.message);
            } finally {
                btnImportFile.disabled = false;
                btnImportFile.textContent = 'IMPORT FROM FILE...';
                fileInput.value = '';
            }
        });
    }

    // Load part adjustments data
    const adjScript = document.getElementById('part-adjustments-data');
    if (adjScript) {
        try {
            partAdjustmentsData = JSON.parse(adjScript.textContent);
        } catch (e) {
            console.warn('Failed to parse part-adjustments-data:', e);
        }
    }

    // Tune modal - close on backdrop click
    const tuneModal = document.getElementById('tune-modal');
    if (tuneModal) {
        tuneModal.addEventListener('click', (e) => {
            if (e.target === tuneModal) tuneModal.close();
        });
    }

    // Tune modal - apply button
    const btnApply = document.getElementById('btn-tune-apply');
    if (btnApply) {
        btnApply.addEventListener('click', () => {
            applyTuningValues();
        });
    }

    // Tune modal - reset button
    const btnReset = document.getElementById('btn-tune-reset');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            resetTuningValues();
        });
    }

    equipDefaultTyreFromCatalog(parts);
    renderInstalledMods();
});

function renderInstalledMods() {
    const listContainer = document.getElementById('installed-mods-list');
    if (!listContainer) return;

    listContainer.innerHTML = '';

    for (const partName in installedMods) {
        const mod = installedMods[partName];
        const row = document.createElement('div');
        row.className = 'installed-mod-row';

        const safePartName = partName.replace(/'/g, "\\'");
        const desc = mod.factoryDefault ? 'FACTORY EQUIPPED TYRE' : 'TUNING PART';

        const hasTuning = partAdjustmentsData[partName] && partAdjustmentsData[partName].length > 0;

        row.innerHTML = `
            <div class="mod-left-info">
                <img src="${mod.img}" alt="${partName}" class="mod-row-img">
                <div class="mod-text-details">
                    <h4>${partName.toUpperCase()}</h4>
                    <p class="mod-short-desc">${desc}</p>
                </div>
            </div>
            <div class="mod-right-stats">
                ${hasTuning ? `<button class="btn-tune-mod" onclick="openTuneModal('${safePartName}')">TUNE</button>` : ''}
                <button class="btn-remove-mod" onclick="removeModification('${partName}')">REMOVE</button>
            </div>
        `;
        listContainer.appendChild(row);
    }
    recalculatePerformance();
}

window.removeModification = function(partName) {
    delete installedMods[partName];
    renderInstalledMods();
};

function secondsToTime(totalSeconds) {
    if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) return "--:--.---";
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    let secondsStr = seconds.toFixed(3);
    if (seconds < 10) secondsStr = '0' + secondsStr;
    return `${minutes}:${secondsStr}`;
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

// ==========================================================================
// 5. CORE SIMULATION ENGINE
// ==========================================================================

function getSimulationContext(timeDisplay) {
    const urlParams = new URLSearchParams(window.location.search);
    const rawCarSlug = timeDisplay.getAttribute('data-car-slug') || urlParams.get('car');
    const carSlug = normalizeCarSlug(rawCarSlug);
    const trackSlug = timeDisplay.getAttribute('data-track-slug') || urlParams.get('track');

    return {
        carSlug,
        trackSlug,
        basePowerHP: parseFloat(timeDisplay.getAttribute('data-base-power')),
        baseWeightKG: parseFloat(timeDisplay.getAttribute('data-base-weight'))
    };
}

function applyInstalledMods(baseStats, basePowerHP, baseWeightKG, carSlug, mods = installedMods) {
    const dyn = {
        powerHP: basePowerHP,
        weightKG: baseWeightKG,
        cda: baseStats.cda,
        cla: baseStats.cla,
        mu: baseStats.mu,
        brake_eff: baseStats.brake_eff,
        drivetrain_loss: baseStats.drivetrain_loss,
        traction: baseStats.traction,
        powerband: 0,
        acceleration_bias: 0,
        top_speed_bias: 0,
        shift_loss: 0,
        inertia: 0,
        stability: 0,
        rigidity: 0,
        extra_weight: 0,
        power_pct: 1.0,
        chassis_flex: baseStats.chassis_flex ?? 0.35
    };

    for (const name in mods) {
        dyn.powerHP += mods[name].hp || 0;
        dyn.weightKG += mods[name].weight || 0;

        // Apply tuning adjustments for this part
        if (mods[name].tuning) {
            applyTuningEffects(dyn, name, mods[name].tuning);
        }

        // Tyres are not additive generic mods. They are handled below as a selected compound
        // relative to the car's factory/default tyre.
        if (mods[name].mainCat === 'tyres') continue;

        const phys = MOD_PHYSICS_MAP[name];
        if (!phys) continue;

        for (const key in phys) {
            if (Object.prototype.hasOwnProperty.call(dyn, key)) {
                dyn[key] += phys[key];
            }
        }
    }

    // Apply global tuning effects
    dyn.powerHP *= dyn.power_pct;
    dyn.weightKG += dyn.extra_weight;

    const currentTyre = getCurrentTyreName(mods);
    const defaultTyre = getDefaultTyreForCar(carSlug);

    if (currentTyre && defaultTyre && TYRE_CLASS_EFFECTS[currentTyre] && TYRE_CLASS_EFFECTS[defaultTyre]) {
        const selectedEffect = TYRE_CLASS_EFFECTS[currentTyre];
        const defaultEffect = TYRE_CLASS_EFFECTS[defaultTyre];
        dyn.mu += (selectedEffect.mu || 0) - (defaultEffect.mu || 0);
        dyn.traction += (selectedEffect.traction || 0) - (defaultEffect.traction || 0);
        dyn.cda += (selectedEffect.cda || 0) - (defaultEffect.cda || 0);
    }

    dyn.weightKG = Math.max(dyn.weightKG, 500);
    dyn.cda = Math.max(dyn.cda, 0.35);
    dyn.cla = Math.max(dyn.cla, 0.0);

    dyn.chassis_flex = clamp(dyn.chassis_flex, 0.08, 1.00);
    dyn.rigidity = clamp(dyn.rigidity, -0.03, 0.08);
    dyn.stability = clamp(dyn.stability, -0.05, 0.08);

    // Stability does not equal free grip. It only converts into a small amount of usable grip,
    // and the conversion is much stronger on old flexible chassis than on modern track cars.
    const stabilityGrip = dyn.stability * (0.12 + 0.30 * dyn.chassis_flex);
    const rigidityGrip = dyn.rigidity * (0.03 + 0.09 * dyn.chassis_flex);
    dyn.mu = clamp(dyn.mu + stabilityGrip + rigidityGrip, 0.65, 2.05);

    // Rigidity can also improve brake/traction consistency slightly, but again mostly on flexible shells.
    dyn.brake_eff += dyn.rigidity * dyn.chassis_flex * 0.025;
    dyn.traction += dyn.rigidity * dyn.chassis_flex * 0.015;

    dyn.brake_eff = clamp(dyn.brake_eff, 0.65, 1.18);
    dyn.drivetrain_loss = clamp(dyn.drivetrain_loss, 0.05, 0.25);
    dyn.traction = clamp(dyn.traction, 0.45, 0.84);
    dyn.powerband = clamp(dyn.powerband, -0.05, 0.12);
    dyn.acceleration_bias = clamp(dyn.acceleration_bias, -0.05, 0.08);
    dyn.top_speed_bias = clamp(dyn.top_speed_bias, -0.05, 0.05);
    dyn.shift_loss = clamp(dyn.shift_loss, -0.06, 0.02);
    dyn.inertia = clamp(dyn.inertia, -0.06, 0.06);

    return dyn;
}

function calculateTopSpeedMs(dyn, constants) {
    const { rho, g, rollingResistanceCoeff } = constants;
    const mass = dyn.weightKG;
    const powerWatts = dyn.powerHP * (1 - dyn.drivetrain_loss) * 745.7;

    let lo = 1;
    let hi = 130; // 468 km/h upper bound, enough for this project.

    for (let i = 0; i < 60; i++) {
        const v = (lo + hi) / 2;
        const fDrag = 0.5 * rho * dyn.cda * v * v;
        const fRolling = rollingResistanceCoeff * mass * g;
        const requiredPower = (fDrag + fRolling) * v;

        if (requiredPower < powerWatts) lo = v;
        else hi = v;
    }

    return lo * (1 + dyn.top_speed_bias);
}

function getEffectiveMu(dyn, speedMs, constants, exponent = 0.055) {
    const { rho, g } = constants;
    const mass = dyn.weightKG;
    const fDownforce = 0.5 * rho * dyn.cla * speedMs * speedMs;
    const fNormal = mass * g + fDownforce;
    const loadFactor = Math.max(1, fNormal / (mass * g));

    // Basic tyre load sensitivity: more vertical load helps, but not linearly.
    const effectiveMu = dyn.mu / Math.pow(loadFactor, exponent);
    return { effectiveMu, fDownforce, fNormal };
}

function calculateCornerLimitMs(radius, dyn, vAbsMax, constants) {
    if (radius <= 0) return vAbsMax;

    let lo = 1;
    let hi = vAbsMax;

    for (let i = 0; i < 45; i++) {
        const v = (lo + hi) / 2;
        const { effectiveMu, fNormal } = getEffectiveMu(dyn, v, constants, 0.060);
        const lateralAvailable = effectiveMu * fNormal;
        const lateralDemand = dyn.weightKG * v * v / radius;

        if (lateralDemand <= lateralAvailable) lo = v;
        else hi = v;
    }

    return lo;
}

function powerCurveFactor(speedMs, dyn) {
    // Simplified gearing/powerband model.
    // Prevents peak power from being available instantly at every speed.
    const base = 0.72 + 0.28 * (1 - Math.exp(-speedMs / 12));
    const response = 1 + dyn.powerband + dyn.acceleration_bias - Math.max(0, dyn.inertia);
    const shiftPenalty = 1 + dyn.shift_loss;
    return clamp(base * response * shiftPenalty, 0.58, 1.08);
}

function expandTrackToSteps(trackSegments, dx) {
    const steps = [];

    trackSegments.forEach(seg => {
        let remaining = seg.length;
        while (remaining > 0.0001) {
            const stepLength = Math.min(dx, remaining);
            steps.push({ length: stepLength, radius: seg.radius });
            remaining -= stepLength;
        }
    });

    return steps;
}

function simulateLap(dyn, trackSegments) {
    const constants = {
        g: 9.81,
        rho: 1.225,
        rollingResistanceCoeff: 0.010,
        brakingScalar: 0.88,
        dx: 20
    };

    const { g, rho, rollingResistanceCoeff, brakingScalar, dx } = constants;
    const mass = dyn.weightKG;
    const powerWatts = dyn.powerHP * (1 - dyn.drivetrain_loss) * 745.7;
    const steps = expandTrackToSteps(trackSegments, dx);
    const n = steps.length;

    if (n === 0 || powerWatts <= 0 || mass <= 0) return null;

    const vAbsMax = calculateTopSpeedMs(dyn, constants);
    const vLimit = new Float64Array(n);
    const vForward = new Float64Array(n);
    const vBackward = new Float64Array(n);

    for (let i = 0; i < n; i++) {
        vLimit[i] = calculateCornerLimitMs(steps[i].radius, dyn, vAbsMax, constants);
    }

    // Rolling start avoids punishing the first straight as if from a standing start.
    vForward[0] = Math.min(22, vLimit[0]);

    // Forward pass: acceleration envelope.
    for (let i = 0; i < n - 1; i++) {
        const v = Math.max(vForward[i], 1);
        const stepLength = steps[i].length;

        const fDrag = 0.5 * rho * dyn.cda * v * v;
        const { effectiveMu, fNormal } = getEffectiveMu(dyn, v, constants, 0.050);
        const fRolling = rollingResistanceCoeff * mass * g;
        const fTractionLimit = effectiveMu * fNormal * dyn.traction;

        let fDrive = (powerWatts * powerCurveFactor(v, dyn)) / v;
        fDrive = Math.min(fDrive, fTractionLimit);

        const acceleration = (fDrive - fDrag - fRolling) / mass;
        const vNext = Math.sqrt(Math.max(0.01, v * v + 2 * acceleration * stepLength));

        vForward[i + 1] = Math.min(vNext, vLimit[i + 1]);
    }

    // Backward pass: braking envelope.
    vBackward[n - 1] = vForward[n - 1];

    for (let i = n - 2; i >= 0; i--) {
        const v = Math.max(vBackward[i + 1], 1);
        const stepLength = steps[i].length;

        const fDrag = 0.5 * rho * dyn.cda * v * v;
        const { effectiveMu, fNormal } = getEffectiveMu(dyn, v, constants, 0.060);
        const fBrake = effectiveMu * dyn.brake_eff * fNormal * brakingScalar;
        const deceleration = (fBrake + fDrag) / mass;

        const vPrev = Math.sqrt(Math.max(0.01, v * v + 2 * deceleration * stepLength));
        vBackward[i] = Math.min(vPrev, vForward[i]);
    }

    // Time accumulation.
    let totalTimeSeconds = 0;
    let topSpeedMs = 0;

    for (let i = 0; i < n; i++) {
        const vActual = Math.max(vBackward[i], 1.0);
        topSpeedMs = Math.max(topSpeedMs, vActual);
        totalTimeSeconds += steps[i].length / vActual;
    }

    return {
        totalTimeSeconds,
        topSpeedKmh: topSpeedMs * 3.6,
        avgSpeedKmh: (steps.reduce((sum, step) => sum + step.length, 0) / 1000) / (totalTimeSeconds / 3600),
        dyn
    };
}

function getReferenceStockLapSeconds(carSlug, trackSlug) {
    const normalizedCar = normalizeCarSlug(carSlug);
    return REFERENCE_STOCK_LAP_SECONDS[normalizedCar]?.[trackSlug] || null;
}

function buildFactoryStockMods(carSlug) {
    const defaultTyre = getDefaultTyreForCar(carSlug);
    if (!defaultTyre) return {};

    return {
        [defaultTyre]: {
            hp: 0,
            weight: TYRE_CATALOG_WEIGHTS[defaultTyre] || 0,
            img: '',
            mainCat: 'tyres',
            factoryDefault: true
        }
    };
}

function calibrateAgainstReference(rawResult, stockResult, carSlug, trackSlug) {
    const referenceSeconds = getReferenceStockLapSeconds(carSlug, trackSlug);

    if (!referenceSeconds || !stockResult || !Number.isFinite(stockResult.totalTimeSeconds) || stockResult.totalTimeSeconds <= 0) {
        return {
            calibratedSeconds: rawResult.totalTimeSeconds,
            referenceSeconds: null,
            solverRatio: 1.0
        };
    }

    const solverRatio = rawResult.totalTimeSeconds / stockResult.totalTimeSeconds;

    return {
        calibratedSeconds: referenceSeconds * solverRatio,
        referenceSeconds,
        solverRatio
    };
}

function recalculatePerformance() {
    const timeDisplay = document.getElementById('lap-time-display');
    if (!timeDisplay) return;

    const hasTelemetry = timeDisplay.dataset.hasTelemetry === 'true';
    // Use best projected lap if available, otherwise fall back to best real lap
    const tuningBase = parseFloat(timeDisplay.dataset.tuningBaseSeconds);
    const bestLapSeconds = parseFloat(timeDisplay.dataset.bestLapSeconds);
    const baseRef = tuningBase && tuningBase > 0 ? tuningBase : (bestLapSeconds || 0);

    if (!hasTelemetry || !baseRef || baseRef <= 0) {
        timeDisplay.innerText = "--:--.---";
        return;
    }

    // Real telemetry base time, with physics delta for mods
    const { carSlug, trackSlug, basePowerHP, baseWeightKG } = getSimulationContext(timeDisplay);

    if (getCurrentTyreName() && BASE_CAR_STATS[carSlug] && TRACKS[trackSlug]) {
        const dyn = applyInstalledMods(BASE_CAR_STATS[carSlug], basePowerHP, baseWeightKG, carSlug, installedMods);
        const stockMods = buildFactoryStockMods(carSlug);
        const stockDyn = applyInstalledMods(BASE_CAR_STATS[carSlug], basePowerHP, baseWeightKG, carSlug, stockMods);
        const stockResult = simulateLap(stockDyn, TRACKS[trackSlug]);
        const moddedResult = simulateLap(dyn, TRACKS[trackSlug]);

        if (stockResult && moddedResult && stockResult.totalTimeSeconds > 0) {
            const modRatio = moddedResult.totalTimeSeconds / stockResult.totalTimeSeconds;
            const calibratedTime = baseRef * modRatio;
            timeDisplay.innerText = secondsToTime(calibratedTime);
            window.REVLABS_LAST_SIM = {
                baseTelemetry: baseRef,
                modRatio: modRatio,
                calibratedTime: calibratedTime,
            };
            return;
        }
    }

    timeDisplay.innerText = secondsToTime(baseRef);
}

// ==========================================================================
// 6. TUNING PANEL (ADJUSTABLE PARTS)
// ==========================================================================

window.openTuneModal = function(partName) {
    const adjDefs = partAdjustmentsData[partName];
    if (!adjDefs || adjDefs.length === 0) return;

    currentTuningPart = partName;

    const titleEl = document.getElementById('tune-modal-title');
    const nameEl = document.getElementById('tune-part-name');
    const imgEl = document.getElementById('tune-part-img');
    const container = document.getElementById('tune-sliders-container');

    if (titleEl) titleEl.innerText = `TUNE: ${partName.toUpperCase()}`;
    if (nameEl) nameEl.innerText = partName.toUpperCase();
    if (imgEl && installedMods[partName]) imgEl.src = installedMods[partName].img;

    if (!container) return;

    const existingTuning = installedMods[partName]?.tuning || {};

    container.innerHTML = adjDefs.map((adj, idx) => {
        const val = existingTuning[adj.key] !== undefined ? existingTuning[adj.key] : adj.default;
        const unitHtml = adj.unit ? `<span class="tune-slider-unit">${adj.unit}</span>` : '';

        return `
            <div class="tune-slider-row">
                <div class="tune-slider-header">
                    <span class="tune-slider-label">${adj.label}</span>
                    <span class="tune-slider-value" id="tune-val-${idx}">${val}${unitHtml}</span>
                </div>
                <input type="range" class="tune-slider"
                    data-adj-key="${adj.key}"
                    data-adj-idx="${idx}"
                    data-unit="${adj.unit}"
                    min="${adj.min}" max="${adj.max}" step="${adj.step}"
                    value="${val}">
            </div>
        `;
    }).join('');

    // Attach input events to sliders
    container.querySelectorAll('.tune-slider').forEach(slider => {
        slider.addEventListener('input', function() {
            const idx = this.dataset.adjIdx;
            const key = this.dataset.adjKey;
            const unit = this.dataset.unit || '';
            const val = parseFloat(this.value);
            const valSpan = document.getElementById(`tune-val-${idx}`);
            if (valSpan) {
                const formatted = adj.step < 1 ? val.toFixed(2) : val;
                valSpan.innerHTML = `${formatted}${unit ? `<span class="tune-slider-unit">${unit}</span>` : ''}`;
            }
            // Store temporary value
            if (!window._tuneTempValues) window._tuneTempValues = {};
            if (!window._tuneTempValues[partName]) window._tuneTempValues[partName] = {};
            window._tuneTempValues[partName][key] = val;
        });
    });

    window._tuneTempValues = {};
    window._tuneTempValues[partName] = {};

    const modal = document.getElementById('tune-modal');
    if (modal) modal.showModal();
};

window.applyTuningValues = function() {
    if (!currentTuningPart || !window._tuneTempValues || !window._tuneTempValues[currentTuningPart]) return;

    if (!installedMods[currentTuningPart]) {
        installedMods[currentTuningPart] = { hp: 0, weight: 0, img: '', mainCat: '', factoryDefault: false };
    }
    installedMods[currentTuningPart].tuning = { ...window._tuneTempValues[currentTuningPart] };

    // Mark any modified values for display
    window._tuneTempValues = {};
    currentTuningPart = null;

    const modal = document.getElementById('tune-modal');
    if (modal) modal.close();

    renderInstalledMods();
};

window.resetTuningValues = function() {
    if (!currentTuningPart) return;
    const adjDefs = partAdjustmentsData[currentTuningPart];
    if (!adjDefs) return;

    // Reset sliders to defaults
    const container = document.getElementById('tune-sliders-container');
    if (container) {
        container.querySelectorAll('.tune-slider').forEach(slider => {
            const idx = slider.dataset.adjIdx;
            const adj = adjDefs[parseInt(idx)];
            if (adj) {
                slider.value = adj.default;
                const valSpan = document.getElementById(`tune-val-${idx}`);
                if (valSpan) {
                    const formatted = adj.step < 1 ? adj.default.toFixed(2) : adj.default;
                    valSpan.innerHTML = `${formatted}${adj.unit ? `<span class="tune-slider-unit">${adj.unit}</span>` : ''}`;
                }
                // Update temp value
                if (!window._tuneTempValues) window._tuneTempValues = {};
                if (!window._tuneTempValues[currentTuningPart]) window._tuneTempValues[currentTuningPart] = {};
                window._tuneTempValues[currentTuningPart][adj.key] = adj.default;
            }
        });
    }
};

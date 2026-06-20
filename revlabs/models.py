from django.db import models

class Track(models.Model):
    slug_id = models.CharField(max_length=50, unique=True, help_text="e.g., 'monza'")
    name = models.CharField(max_length=100)
    length_km = models.FloatField()
    speed_multiplier = models.FloatField()
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/monza-layout.png'")
    bg_image_path = models.CharField(max_length=255, null=True, blank=True, help_text="e.g., 'img/monza-bg.jpg'")
    track_id = models.IntegerField(null=True, blank=True, help_text="GT7 track_id (e.g., 152 for Interlagos)")

    def __str__(self):
        return self.name

class Car(models.Model):
    slug_id = models.CharField(max_length=50, unique=True, help_text="e.g., 'mercedes'")
    name = models.CharField(max_length=100)
    base_avg_speed_kmh = models.FloatField()
    power_hp = models.IntegerField()
    weight_kg = models.IntegerField()
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/mercedes-amg.png'")
    car_code = models.IntegerField(null=True, blank=True, help_text="GT7 car_code (e.g., 3539 for Porsche 911 GT3 RS)")

    def __str__(self):
        return self.name
    
class PartCategory(models.Model):
    # Define the fixed Main Categories from your Figma design
    MAIN_CATEGORY_CHOICES = [
        ('engine', 'Engine'),
        ('suspension', 'Suspension'),
        ('transmission', 'Transmission'),
        ('chassis', 'Chassis'),
        ('aerodynamics', 'Aerodynamics'),
        ('drivetrain', 'Drivetrain'),
        ('brakes', 'Brakes'),
        ('tyres', 'Tyres'),
    ]

    # Add the field to link the sub-category (e.g. Turbochargers) to the main category (e.g. Engine)
    main_category = models.CharField(
        max_length=50, 
        choices=MAIN_CATEGORY_CHOICES, 
        default='engine',
        help_text="The main system this part belongs to."
    )
    
    name = models.CharField(max_length=100, unique=True, help_text="Subcategory name (e.g., Turbochargers)")

    def __str__(self):
        return f"{self.get_main_category_display()} > {self.name}" 
    
class CarPart(models.Model):
    GT7_TIER_CHOICES = [
        ('sports', 'Sports'),
        ('club_sports', 'Club Sports'),
        ('semi_racing', 'Semi-Racing'),
        ('racing', 'Racing'),
        ('extreme', 'Extreme'),
        ('special', 'Special / Roulette'),
    ]

    category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=100, help_text="Specific part name (e.g., Low-RPM Turbocharger)")
    added_hp = models.IntegerField(help_text="Bonus HP")
    added_weight_kg = models.IntegerField(help_text="Weight added/removed (use negative for weight reduction)")
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/turbo-icon.png'")
    gt7_part_id = models.CharField(max_length=50, null=True, blank=True, help_text="GT7 internal part ID for mapping")
    gt7_tier = models.CharField(
        max_length=20, choices=GT7_TIER_CHOICES, null=True, blank=True,
        help_text="GT7 tuning shop tier this part belongs to"
    )
    is_adjustable = models.BooleanField(default=False, help_text="Whether this part has user-configurable settings")

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class PartAdjustment(models.Model):
    part = models.ForeignKey(CarPart, on_delete=models.CASCADE, related_name='adjustments')
    param_key = models.CharField(max_length=60, help_text="e.g., 'ride_height_front'")
    label = models.CharField(max_length=100, help_text="Display label for the slider")
    min_value = models.FloatField()
    max_value = models.FloatField()
    step = models.FloatField(default=1.0)
    default_value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True, default='', help_text="e.g., 'mm', '%', 'Hz'")
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        unique_together = [['part', 'param_key']]

    def __str__(self):
        return f"{self.part.name} > {self.label}"


class TelemetryLap(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='telemetry_laps')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='telemetry_laps')
    lap_number = models.IntegerField(help_text="Lap number in the original session")
    lap_time_ms = models.IntegerField(null=True, blank=True)
    lap_time_seconds = models.FloatField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    has_mods = models.BooleanField(default=False, help_text="Whether modifications were installed")
    mods_hash = models.CharField(max_length=64, null=True, blank=True, help_text="SHA256 hash of installed mod config")
    avg_speed_kmh = models.FloatField(null=True, blank=True)
    max_speed_kmh = models.FloatField(null=True, blank=True)
    min_speed_kmh = models.FloatField(null=True, blank=True)
    max_rpm = models.FloatField(null=True, blank=True)
    avg_throttle_pct = models.FloatField(null=True, blank=True)
    avg_brake_pct = models.FloatField(null=True, blank=True)
    session_notes = models.TextField(null=True, blank=True)
    original_session_id = models.IntegerField(null=True, blank=True)
    original_lap_id = models.IntegerField(null=True, blank=True)
    sector_1_ms = models.IntegerField(null=True, blank=True, help_text="Sector 1 time in milliseconds")
    sector_2_ms = models.IntegerField(null=True, blank=True, help_text="Sector 2 time in milliseconds")
    sector_3_ms = models.IntegerField(null=True, blank=True, help_text="Sector 3 time in milliseconds")
    total_frames = models.IntegerField(null=True, blank=True)
    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['lap_time_ms']
        indexes = [
            models.Index(fields=['car', 'track', 'lap_time_ms']),
            models.Index(fields=['car', 'track', 'is_complete']),
        ]

    def __str__(self):
        time_str = f"{self.lap_time_seconds:.3f}s" if self.lap_time_seconds else "N/A"
        return f"{self.car.name} @ {self.track.name} - Lap {self.lap_number}: {time_str}"
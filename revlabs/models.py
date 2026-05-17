from django.db import models

class Track(models.Model):
    slug_id = models.CharField(max_length=50, unique=True, help_text="e.g., 'monza'")
    name = models.CharField(max_length=100)
    length_km = models.FloatField()
    speed_multiplier = models.FloatField()
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/monza-layout.png'")
    bg_image_path = models.CharField(max_length=255, null=True, blank=True, help_text="e.g., 'img/monza-bg.jpg'")

    def __str__(self):
        return self.name

class Car(models.Model):
    slug_id = models.CharField(max_length=50, unique=True, help_text="e.g., 'mercedes'")
    name = models.CharField(max_length=100)
    base_avg_speed_kmh = models.FloatField()
    power_hp = models.IntegerField()
    weight_kg = models.IntegerField()
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/mercedes-amg.png'")

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
    category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=100, help_text="Specific part name (e.g., Low-RPM Turbocharger)")
    added_hp = models.IntegerField(help_text="Bonus HP")
    added_weight_kg = models.IntegerField(help_text="Weight added/removed (use negative for weight reduction)")
    image_path = models.CharField(max_length=255, help_text="e.g., 'img/turbo-icon.png'")

    def __str__(self):
        return f"{self.name} ({self.category.name})"
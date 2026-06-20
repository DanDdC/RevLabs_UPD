from django.contrib import admin
from .models import Car, Track, PartCategory, CarPart, TelemetryLap

admin.site.register(Car)
admin.site.register(Track)
admin.site.register(PartCategory)
admin.site.register(CarPart)

@admin.register(TelemetryLap)
class TelemetryLapAdmin(admin.ModelAdmin):
    list_display = ['car', 'track', 'lap_number', 'lap_time_seconds', 'max_speed_kmh', 'imported_at']
    list_filter = ['car', 'track', 'is_complete']
    ordering = ['lap_time_ms']
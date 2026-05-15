from django.contrib import admin
from .models import Car, Track, PartCategory, CarPart

admin.site.register(Car)
admin.site.register(Track)
admin.site.register(PartCategory)
admin.site.register(CarPart)
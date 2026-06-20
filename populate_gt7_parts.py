"""
Add Sports Medium tyre and expand GT7 parts catalog.
Run AFTER populateparts.py.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.models import PartCategory, CarPart

def get_or_create_cat(main, name):
    cat, _ = PartCategory.objects.get_or_create(
        name=name,
        defaults={'main_category': main}
    )
    return cat

def add_part(cat_name, part_name, hp, weight, img, gt7_id=None):
    cat = get_or_create_cat('tyres', cat_name) if cat_name in ['Comfort', 'Sports', 'Racing'] else get_or_create_cat('tyres', cat_name)
    PartCategory.objects.get_or_create(name=cat_name, defaults={'main_category': 'tyres'})
    cat = PartCategory.objects.get(name=cat_name)
    CarPart.objects.get_or_create(
        name=part_name,
        defaults={
            'category': cat,
            'added_hp': hp,
            'added_weight_kg': weight,
            'image_path': img,
            'gt7_part_id': gt7_id or '',
        }
    )

# Sports Medium tyre (between Performance and High-Performance)
sports_cat, _ = PartCategory.objects.get_or_create(
    name='Sports',
    defaults={'main_category': 'tyres'}
)

CarPart.objects.get_or_create(
    name='Sports Medium Tyres',
    defaults={
        'category': sports_cat,
        'added_hp': 0,
        'added_weight_kg': -1,
        'image_path': 'img/mods/sportsmedium.png',
        'gt7_part_id': 'tyre_sports_medium',
    }
)

print("Sports Medium Tyre added!")
print("\nCurrent tyre options:")
for p in CarPart.objects.filter(category__main_category='tyres').order_by('category__name'):
    print(f"  [{p.category.name}] {p.name}")

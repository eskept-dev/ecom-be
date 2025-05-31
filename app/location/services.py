import json

from app.core.utils.logger import logger

from app.location.models import Location, LocationType
from app.core.utils.string import slugify


def import_airports():
    with open('app/location/__data__/airports.json', 'r') as f:
        data = json.load(f)

    location_names = [item['name'] for item in data]
    existing_locations = Location.objects.filter(name__in=location_names)
    
    to_create = []
    for item in data:
        if item['name'] not in existing_locations:
            item['type'] = LocationType.AIRPORT
            item['province'] = slugify(item['province'])
            item['city'] = slugify(item['city'])
            item['district'] = slugify(item['district'])
            item['ward'] = slugify(item['ward'])
            to_create.append(Location(**item))
    
    Location.objects.bulk_create(to_create)
    
    logger.info(f"Imported {len(to_create)} airports")

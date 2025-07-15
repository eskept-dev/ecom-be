import json
import random

from app.core.utils.logger import logger
from app.product.models import Product, ServiceType
from app.supplier.models import Supplier


def import_products():
    with open('app/product/__data__/product.json', 'r') as f:
        data = json.load(f)

    services = [
        ServiceType.AIRPORT_TRANSFER,
        ServiceType.FAST_TRACK,
        ServiceType.E_VISA,
    ]
    
    for service in services:
        products = data[service]
        logger.info(f"Importing {len(products)} {service} products")
        
        suppliers = Supplier.objects.filter(name__contains=service.value)
        
        suppliers_list = [*suppliers, None]
        
        for product in products:
            random_supplier = random.choice(suppliers_list)
            logger.info(f"-----> Importing {product['name']} - {random_supplier.name if random_supplier else 'None'}")
            
            formated_details = []
            if service == ServiceType.AIRPORT_TRANSFER.value:
                formated_details.append({
                    'type': 'passenger_capacity',
                    'value': int(product['details']['number_of_travellers'])
                })
                formated_details.append({
                    'type': 'luggage_capacity',
                    'value': int(product['details']['number_of_luggage'])
                })
            elif service == ServiceType.FAST_TRACK.value:
                formated_details.append({
                    'type': 'available_time',
                    'value': f"{product['details']['available_time_from']} - {product['details']['available_time_to']}"
                })
            elif service == ServiceType.E_VISA:
                formated_details.append({
                    'type': 'processing_time',
                    'value': int(product['details']['processing_time'])
                })
                
            formated_highlights = []
            for highlight in product['highlights']:
                formated_highlights.append({
                    'value': highlight,
                    'priority': 1
                })

            payload = {
                'name': product['name'],
                'service_type': service,
                'image_url': "https://placehold.co/300x200",
                'unit': product['unit'],
                'base_price_vnd': product['price_vnd'],
                'base_price_usd': product['price_usd'],
                'rating': product['rating'],
                'review_count': product['review_count'],
                'details': formated_details,
                'highlights': formated_highlights,
                'description': product['description'],
                'cancellation_policy': product['cancellation_policy'],
                'available_locations': product['available_locations'],
                'supplier': random_supplier,
            }
            Product.objects.create(**payload)        

    logger.info("Imported all products")

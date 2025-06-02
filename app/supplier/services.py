import json
import random

from app.core.utils.logger import logger
from app.product.models import Product, ServiceType
from app.supplier.models import Supplier


def import_suppliers():
    with open('app/supplier/__data__/suppliers.json', 'r') as f:
        data = json.load(f)
    
    for service in ServiceType:
        suppliers = data[service.value]
        for supplier in suppliers:
            name = f"{supplier} - {service.value}"
            Supplier.objects.create(name=name)
            logger.info(f"-----> Imported supplier: {name}")
    
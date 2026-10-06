from decimal import Decimal
import json
from product.product_model import Product, ProductCategoryEnum, ProductStatusEnum


products = [
    Product(
        "producct-1",
        "product-1 desc",
        Decimal("1000.13"),
        10,
        ProductCategoryEnum.ELECTRONICS,
        ProductStatusEnum.ACTIVE
    ),
    Product(
            "producct-2",
            "product-2 desc",
            Decimal("2000.13"),
            10,
            ProductCategoryEnum.ELECTRONICS,
            ProductStatusEnum.ACTIVE
        ),
    Product(
            "producct-3",
            "product-1 desc",
            Decimal("3000.13"),
            10,
            ProductCategoryEnum.ELECTRONICS,
            ProductStatusEnum.ACTIVE
        )
]




def make_json(path:str, products: list[Product]):
    data = {
        
    }
    
    for product in products:
        item = {
            "product_id" : str(product.product_id),
            "name" : str(product.name),
            "description" : str(product.description),
            "price" : str(product.price),
            "stock" : product.stock,
            "category" : str(product.category.name),
            "status" : str(product.status.name),
        }
        data[str(product.product_id)] = item
    with open(path, "w") as file:
        json.dump(data,file)
            
            
make_json(r"src/helpers/json_test.json",products=products)
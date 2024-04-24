# CRUD OPERATIONS FOR PRODUCTS

from fastapi import APIRouter, HTTPException
from user_operations import users_db
from models import Product, User

product_router = APIRouter()
products_db = {}

#CREATE
@product_router.post("/products/", response_model=Product)
async def create_product(product: Product):
    if product.seller not in users_db:
        raise HTTPException(status_code=404, detail="Seller username not found")
    if not users_db[product.seller].is_seller:
        raise HTTPException(status_code=403, detail="Forbidden: User must be a seller")
    if product.id in products_db:
        raise HTTPException(status_code=400, detail="ProductId already exists")
    products_db[product.id] = product
    return product

#READ
@product_router.get("/products/")
async def read_products():
    return list(products_db.values())

@product_router.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

#UPDATE
@product_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, name: str, price: float, quantity: int, seller: User):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    if not seller.is_seller:
        raise HTTPException(status_code=403, detail="Forbidden: User must be a seller")
    if products_db[product_id].seller != seller.username:
        raise HTTPException(status_code=403, detail="Forbidden: User is not seller of productId: {}".format(product_id))

    products_db[product_id].name = name
    products_db[product_id].price = price
    products_db[product_id].quantity = quantity

    return products_db[product_id]

#DELETE
@product_router.delete("/products/{product_id}")
async def delete_product(product_id: int, seller: User):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    if not seller.is_seller:
        raise HTTPException(status_code=403, detail="Forbidden: User must be a seller")
    if products_db[product_id].seller != seller.username:
        raise HTTPException(status_code=403, detail="Forbidden: User is not seller of productId: {}".format(product_id))
    
    del products_db[product_id]
    return {"message": "ProductId {} was deleted".format(product_id)}

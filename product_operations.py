# CRUD OPERATIONS FOR PRODUCTS

from fastapi import APIRouter, HTTPException, Depends
from user_operations import users_db, get_current_user
from models import Product, User

product_router = APIRouter()
products_db = {} #using a dictionary for this task, but for production apps would use a real DB

#CREATE
@product_router.post("/products/", response_model=Product)
async def create_product(id: int, name: str, price: float, quantity: int, current_user: User = Depends(get_current_user)):
    if not current_user.is_seller: 
        raise HTTPException(status_code=403, detail="Forbidden: User must be a seller")
    if id in products_db:
        raise HTTPException(status_code=400, detail="ProductId already exists")
    
    product = Product(id=id, name=name, price=price, quantity=quantity, seller=current_user.username)
    products_db[id] = product
    return product

#READ
@product_router.get("/products/all") #created for testing/debugging purposes
async def read_products():
    return list(products_db.values())

@product_router.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

#UPDATE
@product_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, name: str, price: float, quantity: int, current_user: User = Depends(get_current_user)):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    if products_db[product_id].seller != current_user.username:
        raise HTTPException(status_code=403, detail="Forbidden: User is not seller of productId: {}".format(product_id))

    products_db[product_id].name = name
    products_db[product_id].price = price
    products_db[product_id].quantity = quantity

    return products_db[product_id]

#DELETE
@product_router.delete("/products/{product_id}")
async def delete_product(product_id: int, current_user: User = Depends(get_current_user)):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    if products_db[product_id].seller != current_user.username:
        raise HTTPException(status_code=403, detail="Forbidden: User is not seller of productId: {}".format(product_id))
    
    del products_db[product_id]
    return {"message": "ProductId {} was deleted".format(product_id)}

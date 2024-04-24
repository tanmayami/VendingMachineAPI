from fastapi import FastAPI
from user_operations import user_router
from product_operations import product_router
from vending_operations import vending_router

app = FastAPI()

# Include routers
app.include_router(user_router)
app.include_router(product_router)
app.include_router(vending_router)
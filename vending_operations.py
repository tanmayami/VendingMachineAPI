# OPERATIONS FOR VENDING MACHINE

from fastapi import APIRouter, HTTPException
from models import User, Product, Deposit
from user_operations import users_db
from product_operations import products_db

vending_router = APIRouter()

# Deposit coins
@vending_router.post("/deposit")
async def deposit_coins(username: str, deposit: Deposit):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # assumption: a user with a non-buyer role can also deposit money
    users_db[username].balance_in_cents += (deposit.coins_5 * 5) + \
        (deposit.coins_10 * 10) + (deposit.coins_20 * 20) + \
        (deposit.coins_50 * 50) + (deposit.coins_100 * 100)

    return {"message": "Deposit successful", "balance_in_cents": users_db[username].balance_in_cents}

# helper function to compute change
def compute_change(amount):
    denominations = [100, 50, 20, 10, 5]
    change_in_coins = {str(coin): 0 for coin in denominations}

    # Compute the change in coins
    for coin in denominations:
        while amount >= coin:
            amount -= coin
            change_in_coins[str(coin)] += 1

    return {"change_given": change_in_coins, "unpaid_cents": amount}

# Buy products
@vending_router.post("/buy")
async def buy_products(username: str, product_id: int, quantity: int):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[product_id]
    if product.quantity < quantity:
        raise HTTPException(status_code=400, detail="Not enough products available")
    
    #Assumption: Seller of product won't buy their own product but is allowed to buy other user's products 
    if product.seller == username:
        raise HTTPException(status_code=404, detail="Forbidden: Seller can't buy their own products")
   
    price_in_cents = product.price * 100
    total_cost = price_in_cents * quantity
    if users_db[username].balance_in_cents < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    users_db[username].balance_in_cents -= total_cost
    products_db[product_id].quantity -= quantity
    change = compute_change(users_db[username].balance_in_cents)

    return {"message": "ProductId {} purchased successfully".format(product_id), 
            "quanity_purchased": quantity,
            "total_cost": total_cost,
            "change": change}

# Reset deposit
@vending_router.post("/reset/{username}")
async def reset_deposit(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    users_db[username].balance_in_cents = 0
    return {"message": "Deposit reset successful"}
